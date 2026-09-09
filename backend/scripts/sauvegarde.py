"""Sauvegarde de la base de données et des pièces jointes (prompt 5.3).

Produit une archive horodatée contenant :
- un export de la base (copie sûre du fichier SQLite en développement,
  `pg_dump` au format personnalisé en production PostgreSQL) ;
- une copie compressée de `storage/` (photos, documents, fiches de
  configuration, justificatifs — tout ce qui vit hors base) ;
- un manifeste JSON (horodatage, type de base, contenu).

Ne sauvegarde JAMAIS `.env` : les secrets (`JWT_SECRET_KEY`, `FERNET_MASTER_KEY`)
ne doivent jamais se retrouver dans une archive de sauvegarde (CLAUDE.md,
règle 4). Ils se conservent séparément (gestionnaire de secrets de
l'organisation) — leur perte rend le coffre-fort applicatif irrécupérable,
la sauvegarde de la base seule ne suffit pas à restaurer l'accès aux secrets
qu'elle contient.

Usage :
    python scripts/sauvegarde.py [--destination DOSSIER]

Exécuté par un administrateur système, hors de l'application (pas une route API :
une sauvegarde n'est pas une action métier tracée en base, elle protège la base
elle-même).
"""
import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402


def _horodatage() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%Hh%M")


def _sauvegarder_sqlite(url: str, destination: Path) -> str:
    chemin_source = Path(url.removeprefix("sqlite:///"))
    if not chemin_source.exists():
        raise FileNotFoundError(f"Base SQLite introuvable : {chemin_source}")
    nom_fichier = "base.sqlite3"
    # sqlite3.Connection.backup() : copie cohérente même si l'API écrit en
    # parallèle (contrairement à une copie de fichier brute, qui risquerait de
    # capturer un fichier mi-écrit — la base n'est jamais verrouillée pour la
    # durée de la sauvegarde côté application).
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
    # DATABASE_URL utilise le pilote psycopg (« postgresql+psycopg:// ») pour
    # SQLAlchemy ; pg_dump attend le schéma standard « postgresql:// ».
    url_pg_dump = url.replace("postgresql+psycopg://", "postgresql://", 1)
    nom_fichier = "base.dump"
    resultat = subprocess.run(
        ["pg_dump", "--format=custom", f"--file={destination / nom_fichier}", url_pg_dump],
        capture_output=True, text=True,
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


def sauvegarder(dossier_destination: Path) -> Path:
    horodatage = _horodatage()
    destination = dossier_destination / f"sheq-sauvegarde-{horodatage}"
    destination.mkdir(parents=True, exist_ok=False)

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
    (destination / "manifeste.json").write_text(json.dumps(manifeste, indent=2, ensure_ascii=False), encoding="utf-8")

    return destination


if __name__ == "__main__":
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--destination", default="./sauvegardes", help="Dossier parent des sauvegardes.")
    arguments = analyseur.parse_args()

    dossier = sauvegarder(Path(arguments.destination))
    print(f"Sauvegarde créée : {dossier}")
