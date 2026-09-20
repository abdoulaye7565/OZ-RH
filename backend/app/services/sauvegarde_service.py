"""Sauvegarde de la base et des pièces jointes (prompt 5.3, planifiée à la
revue d'ensemble 2026-09-10).

Produit une archive horodatée contenant :
- un export de la base (copie SQLite cohérente en développement, `pg_dump`
  au format personnalisé en production PostgreSQL) ;
- une copie compressée de `storage/` (photos, documents, fiches de
  configuration, justificatifs) ;
- un manifeste JSON.

Ne sauvegarde JAMAIS `.env` : `JWT_SECRET_KEY` et `FERNET_MASTER_KEY` ne
doivent jamais se retrouver dans une archive (CLAUDE.md §4). Ils se
conservent séparément (gestionnaire de secrets de l'organisation). Les
secrets applicatifs stockés en base y sont chiffrés au repos (Fernet) : la
sauvegarde de la base ne les expose donc pas en clair, mais reste inutile
pour restaurer l'accès si la clé maîtresse est perdue.

Ce module contient la logique ; il est appelé :
- par le planificateur (`app/core/scheduler.py`), une fois par jour ;
- par le script CLI `Scripts/sauvegarde.py` (administrateur système).
"""
import json
import logging
import shutil
import sqlite3
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger("app.sauvegarde")

_PREFIXE = "sheq-sauvegarde-"


def _horodatage() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%Hh%M")


def _sauvegarder_sqlite(url: str, destination: Path) -> str:
    chemin_source = Path(url.removeprefix("sqlite:///"))
    if not chemin_source.exists():
        raise FileNotFoundError(f"Base SQLite introuvable : {chemin_source}")
    nom_fichier = "base.sqlite3"
    # sqlite3.Connection.backup() : copie cohérente même si l'API écrit en
    # parallèle, contrairement à une copie de fichier brute.
    source = sqlite3.connect(str(chemin_source))
    cible = sqlite3.connect(str(destination / nom_fichier))
    try:
        source.backup(cible)
    finally:
        cible.close()
        source.close()
    return nom_fichier


def _sauvegarder_postgresql(url: str, destination: Path) -> str:
    if shutil.which("pg_dump") is None:
        raise RuntimeError("pg_dump introuvable dans le PATH — requis pour sauvegarder PostgreSQL.")
    url_pg_dump = url.replace("postgresql+psycopg://", "postgresql://", 1)
    nom_fichier = "base.dump"
    resultat = subprocess.run(
        ["pg_dump", "--format=custom", f"--file={destination / nom_fichier}", url_pg_dump],
        capture_output=True,
        text=True,
    )
    if resultat.returncode != 0:
        raise RuntimeError(f"Échec de pg_dump : {resultat.stderr.strip()}")
    return nom_fichier


def _sauvegarder_stockage(dossier_stockage: Path, destination: Path) -> str | None:
    if not dossier_stockage.exists():
        return None
    nom_fichier = "storage.tar.gz"
    with tarfile.open(destination / nom_fichier, "w:gz") as archive:
        archive.add(dossier_stockage, arcname="storage")
    return nom_fichier


def purger_anciennes(dossier_destination: Path, retention: int) -> list[str]:
    """Garde les `retention` archives les plus récentes, supprime les autres.
    Retourne les noms supprimés."""
    if retention <= 0:
        return []
    archives = sorted(
        (p for p in dossier_destination.glob(f"{_PREFIXE}*") if p.is_dir()),
        key=lambda p: p.name,
    )
    a_supprimer = archives[:-retention] if len(archives) > retention else []
    supprimes = []
    for chemin in a_supprimer:
        shutil.rmtree(chemin, ignore_errors=True)
        supprimes.append(chemin.name)
    return supprimes


def sauvegarder(dossier_destination: Path | str | None = None, retention: int | None = None) -> Path:
    """Crée une archive de sauvegarde horodatée et purge les plus anciennes.
    Retourne le chemin de l'archive créée."""
    dossier_destination = Path(dossier_destination or settings.sauvegarde_dir)
    retention = settings.sauvegarde_retention if retention is None else retention

    destination = dossier_destination / f"{_PREFIXE}{_horodatage()}"
    destination.mkdir(parents=True, exist_ok=True)

    type_base = urlparse(settings.database_url).scheme.split("+")[0]
    if type_base == "sqlite":
        fichier_base = _sauvegarder_sqlite(settings.database_url, destination)
    elif type_base == "postgresql":
        fichier_base = _sauvegarder_postgresql(settings.database_url, destination)
    else:
        raise ValueError(f"Type de base non pris en charge pour la sauvegarde : {type_base}")

    fichier_stockage = _sauvegarder_stockage(Path(settings.storage_dir), destination)

    manifeste = {
        "horodatage_utc": datetime.now(timezone.utc).isoformat(),
        "type_base": type_base,
        "fichier_base": fichier_base,
        "fichier_stockage": fichier_stockage,
        "avertissement": "Ne contient aucun secret : .env n'est jamais inclus dans une sauvegarde.",
    }
    (destination / "manifeste.json").write_text(
        json.dumps(manifeste, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    supprimes = purger_anciennes(dossier_destination, retention)
    if supprimes:
        logger.info("Sauvegardes purgées (rétention %d) : %s", retention, ", ".join(supprimes))
    return destination
