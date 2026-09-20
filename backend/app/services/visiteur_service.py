"""Logique métier du module Visiteurs (prompt 4.3, section 5.3.6 du CDC,
REG-SHEQ-004)."""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.visiteur import Visiteur
from app.schemas.visiteur import VisiteurCreation


def enregistrer_visiteur(db: Session, donnees: VisiteurCreation, cree_par_id: int) -> Visiteur:
    """`donnees.consignes_lues` est déjà validé booléen vrai par le schéma
    (règle 5.3.6) — revérifié ici en défense en profondeur, jamais confiance
    exclusive en la validation côté client ni même côté schéma seul."""
    if not donnees.consignes_lues:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Les consignes de sécurité doivent être lues et validées avant tout enregistrement",
        )
    visiteur = Visiteur(
        nom=donnees.nom,
        societe=donnees.societe,
        motif=donnees.motif,
        personne_visitee=donnees.personne_visitee,
        heure_arrivee=datetime.now(timezone.utc),
        consignes_lues=True,
        cree_par_id=cree_par_id,
    )
    db.add(visiteur)
    db.commit()
    db.refresh(visiteur)
    return visiteur


def obtenir_visiteur(db: Session, visiteur_id: int) -> Visiteur:
    visiteur = db.get(Visiteur, visiteur_id)
    if visiteur is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visiteur introuvable")
    return visiteur


def enregistrer_depart(db: Session, visiteur: Visiteur, modifie_par_id: int) -> Visiteur:
    if visiteur.heure_depart is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Le départ de ce visiteur est déjà enregistré")
    visiteur.heure_depart = datetime.now(timezone.utc)
    visiteur.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(visiteur)
    return visiteur


def lister_visiteurs(db: Session) -> list[Visiteur]:
    # archive.is_(False) : trouvé manquant en ajoutant archiver_visiteur()
    # (2026-09-09) — sans ce filtre, un visiteur archivé restait visible
    # dans le registre général, l'archivage n'aurait servi à rien.
    return list(
        db.scalars(select(Visiteur).where(Visiteur.archive.is_(False)).order_by(Visiteur.heure_arrivee.desc()))
    )


def archiver_visiteur(db: Session, visiteur: Visiteur, modifie_par_id: int) -> Visiteur:
    """Jamais de suppression physique (point 2, CLAUDE.md) — un visiteur
    archivé disparaît du registre général mais reste consultable en base
    (traçabilité intégrale, point 3). Réservé à un visiteur déjà parti :
    archiver quelqu'un encore présent le ferait disparaître de la liste
    d'évacuation (visiteurs_presents ne filtre pas sur `archive` — elle n'a
    pas besoin de le faire, mais un visiteur présent n'a de toute façon
    aucune raison légitime d'être archivé avant son départ)."""
    if visiteur.heure_depart is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'archiver un visiteur encore présent sur site",
        )
    visiteur.archive = True
    visiteur.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(visiteur)
    return visiteur


def visiteurs_presents(db: Session) -> list[Visiteur]:
    """Section 5.3.6 : "consulter la liste des personnes présentes sur le site,
    utilisable en cas d'évacuation" — pas de filtrage par site : un seul
    registre couvre l'ensemble des visiteurs, comme le classeur réel
    (REG-SHEQ-004) qui ne distingue pas de site non plus."""
    return list(db.scalars(select(Visiteur).where(Visiteur.heure_depart.is_(None)).order_by(Visiteur.heure_arrivee)))
