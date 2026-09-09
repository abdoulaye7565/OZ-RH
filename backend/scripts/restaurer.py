"""Restauration d'une sauvegarde produite par `scripts/sauvegarde.py` (prompt 5.3).

Écrase la base de données et le dossier `storage/` courants : opération destructrice,
refusée sans confirmation explicite. Ne restaure jamais `.env` (jamais inclus dans une
sauvegarde, voir `sauvegarde.py`) — les secrets (`JWT_SECRET_KEY`, `FERNET_MASTER_KEY`)
doivent déjà être en place dans l'environnement cible avant de restaurer, sans quoi
l'application ne démarre pas et le contenu du coffre-fort reste illisible même restauré
(chiffré avec une clé différente).

Usage :
    python scripts/restaurer.py DOSSIER_SAUVEGARDE --confirmer
"""
import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import tarfile
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402


def _restaurer_sqlite(fichier_sauvegarde: Path, url: str) -> None:
    chemin_cible = Path(url.removeprefix("sqlite:///"))
    source = sqlite3.connect(str(fichier_sauvegarde))
    cible = sqlite3.connect(str(chemin_cible))
    try:
        source.backup(cible)
    finally:
        cible.close()
        source.close()


def _restaurer_postgresql(fichier_sauvegarde: Path, url: str) -> None:
    if shutil.which("pg_restore") is None:
        raise RuntimeError("pg_restore introuvable dans le PATH — requis pour restaurer PostgreSQL.")
    url_pg_restore = url.replace("postgresql+psycopg://", "postgresql://", 1)
    resultat = subprocess.run(
        ["pg_restore", "--clean", "--if-exists", f"--dbname={url_pg_restore}", str(fichier_sauvegarde)],
        capture_output=True, text=True,
    )
    if resultat.returncode != 0:
        raise RuntimeError(f"Échec de pg_restore : {resultat.stderr.strip()}")


def _restaurer_stockage(archive_stockage: Path, dossier_stockage: Path) -> None:
    if dossier_stockage.exists():
        shutil.rmtree(dossier_stockage)
    with tarfile.open(archive_stockage, "r:gz") as archive:
        archive.extractall(dossier_stockage.parent, filter="data")


def restaurer(dossier_sauvegarde: Path) -> None:
    manifeste = json.loads((dossier_sauvegarde / "manifeste.json").read_text(encoding="utf-8"))

    type_base = urlparse(settings.database_url).scheme.split("+")[0]
    if type_base != manifeste["type_base"]:
        raise ValueError(
            f"Sauvegarde issue d'une base {manifeste['type_base']}, "
            f"restauration demandée vers une base {type_base} — non pris en charge."
        )

    if type_base == "sqlite":
        _restaurer_sqlite(dossier_sauvegarde / manifeste["fichier_base"], settings.database_url)
    elif type_base == "postgresql":
        _restaurer_postgresql(dossier_sauvegarde / manifeste["fichier_base"], settings.database_url)
    else:
        raise ValueError(f"Type de base non pris en charge pour la restauration : {type_base}")

    if manifeste["fichier_stockage"]:
        _restaurer_stockage(dossier_sauvegarde / manifeste["fichier_stockage"], Path(settings.storage_dir))


if __name__ == "__main__":
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("dossier_sauvegarde", help="Dossier produit par sauvegarde.py")
    analyseur.add_argument(
        "--confirmer", action="store_true",
        help="Obligatoire : la restauration écrase la base et le stockage courants.",
    )
    arguments = analyseur.parse_args()

    if not arguments.confirmer:
        print(
            "Restauration annulée : cette opération écrase la base et le stockage courants. "
            "Relancer avec --confirmer pour continuer.",
            file=sys.stderr,
        )
        sys.exit(1)

    restaurer(Path(arguments.dossier_sauvegarde))
    print("Restauration terminée.")
