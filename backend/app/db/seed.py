"""Amorçage d'un compte administrateur de démonstration.

Nécessaire car POST /api/v1/auth/utilisateurs exige déjà un administrateur
connecté : sans ce script, impossible de créer le tout premier compte via l'API.
Idempotent — ne fait rien si un administrateur existe déjà. Données fictives
uniquement (point 10, CLAUDE.md) : à ne jamais utiliser tel quel en production.

Usage : python -m app.db.seed
"""
from sqlalchemy import select

from app.core.security import hacher_mot_de_passe
from app.db.session import SessionLocal
from app.models.enums import RoleUtilisateur, TypeSite
from app.models.site import Site
from app.models.utilisateur import Utilisateur

IDENTIFIANT_DEMO = "admin"
MOT_DE_PASSE_DEMO = "ChangezMoi!2026"


def seed() -> None:
    db = SessionLocal()
    try:
        existant = db.scalar(select(Utilisateur).where(Utilisateur.role == RoleUtilisateur.ADMINISTRATEUR))
        if existant is not None:
            print(f"Un administrateur existe déjà ({existant.identifiant}) — rien à faire.")
            return

        site = db.scalar(select(Site))
        if site is None:
            site = Site(nom="Siège Bamako (démo)", type=TypeSite.SIEGE)
            db.add(site)
            db.flush()

        admin = Utilisateur(
            nom="Admin",
            prenom="Démo",
            identifiant=IDENTIFIANT_DEMO,
            mot_de_passe=hacher_mot_de_passe(MOT_DE_PASSE_DEMO),
            role=RoleUtilisateur.ADMINISTRATEUR,
            site_id=site.id,
        )
        db.add(admin)
        db.commit()

        print("Administrateur de démonstration créé :")
        print(f"  identifiant   : {IDENTIFIANT_DEMO}")
        print(f"  mot de passe  : {MOT_DE_PASSE_DEMO}")
        print("À changer ou supprimer avant toute mise en production.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
