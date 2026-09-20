"""CLI de sauvegarde de la base et des pièces jointes (prompt 5.3).

La logique vit dans `app/services/sauvegarde_service.py` (partagée avec le
planificateur qui l'exécute une fois par jour — voir app/core/scheduler.py).
Ce script reste utile pour une sauvegarde manuelle à la demande, par un
administrateur système.

Ne sauvegarde JAMAIS `.env` : les secrets (`JWT_SECRET_KEY`,
`FERNET_MASTER_KEY`) ne se retrouvent jamais dans une archive (CLAUDE.md §4).

Usage :
    python Scripts/sauvegarde.py [--destination DOSSIER] [--retention N]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.sauvegarde_service import sauvegarder  # noqa: E402

if __name__ == "__main__":
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--destination", default=None, help="Dossier parent des sauvegardes (défaut : settings.sauvegarde_dir).")
    analyseur.add_argument("--retention", type=int, default=None, help="Nombre d'archives à conserver (défaut : settings.sauvegarde_retention).")
    arguments = analyseur.parse_args()

    dossier = sauvegarder(arguments.destination, arguments.retention)
    print(f"Sauvegarde créée : {dossier}")
