"""Tests de la sauvegarde automatique (revue d'ensemble 2026-09-10).

Le script Scripts/sauvegarde.py existait mais n'était planifié nulle part et
n'était pas testé. La logique est désormais dans
app/services/sauvegarde_service.py, exécutée quotidiennement par le
planificateur.
"""
import json
import sqlite3
from pathlib import Path

import pytest

from app.services import sauvegarde_service


@pytest.fixture()
def base_sqlite_factice(tmp_path: Path) -> Path:
    chemin = tmp_path / "base_test.sqlite3"
    cx = sqlite3.connect(chemin)
    cx.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    cx.execute("INSERT INTO t (v) VALUES ('donnée test')")
    cx.commit()
    cx.close()
    return chemin


def test_sauvegarde_cree_une_archive_avec_manifeste(tmp_path, base_sqlite_factice, monkeypatch):
    monkeypatch.setattr(sauvegarde_service.settings, "database_url", f"sqlite:///{base_sqlite_factice}")
    monkeypatch.setattr(sauvegarde_service.settings, "storage_dir", str(tmp_path / "storage_inexistant"))
    dest = tmp_path / "sauvegardes"

    archive = sauvegarde_service.sauvegarder(dest, retention=14)

    assert archive.exists()
    assert (archive / "base.sqlite3").exists()
    manifeste = json.loads((archive / "manifeste.json").read_text(encoding="utf-8"))
    assert manifeste["type_base"] == "sqlite"
    assert "secret" in manifeste["avertissement"].lower()

    # La copie de base est bien lisible et contient la donnée.
    cx = sqlite3.connect(archive / "base.sqlite3")
    assert cx.execute("SELECT v FROM t").fetchone()[0] == "donnée test"
    cx.close()


def test_ne_contient_jamais_le_fichier_env(tmp_path, base_sqlite_factice, monkeypatch):
    monkeypatch.setattr(sauvegarde_service.settings, "database_url", f"sqlite:///{base_sqlite_factice}")
    monkeypatch.setattr(sauvegarde_service.settings, "storage_dir", str(tmp_path / "storage"))
    (tmp_path / "storage").mkdir()
    (tmp_path / "storage" / "photo.jpg").write_bytes(b"jpeg")
    dest = tmp_path / "sauvegardes"

    archive = sauvegarde_service.sauvegarder(dest, retention=14)

    noms = {p.name for p in archive.iterdir()}
    assert ".env" not in noms
    assert "base.sqlite3" in noms and "storage.tar.gz" in noms


def test_retention_supprime_les_archives_les_plus_anciennes(tmp_path, base_sqlite_factice, monkeypatch):
    monkeypatch.setattr(sauvegarde_service.settings, "database_url", f"sqlite:///{base_sqlite_factice}")
    monkeypatch.setattr(sauvegarde_service.settings, "storage_dir", str(tmp_path / "s"))
    dest = tmp_path / "sauvegardes"
    dest.mkdir()

    # 5 archives "anciennes" simulées + 1 vraie => rétention 3 doit en garder 3.
    for jour in range(1, 6):
        (dest / f"sheq-sauvegarde-2026-01-0{jour}_00h00").mkdir()

    sauvegarde_service.sauvegarder(dest, retention=3)

    restantes = sorted(p.name for p in dest.glob("sheq-sauvegarde-*"))
    assert len(restantes) == 3
    # Les plus récentes par ordre de nom (l'archive fraîche, horodatée 2026-09…, en tête).
    assert restantes[0] == "sheq-sauvegarde-2026-01-04_00h00"
    assert restantes[1] == "sheq-sauvegarde-2026-01-05_00h00"
