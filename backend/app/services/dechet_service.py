"""Logique métier du module Déchets (prompt 4.3, section 5.3.6 du CDC,
REG-SHEQ-005)."""
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dechet import Dechet
from app.schemas.dechet import DechetCreation, DechetModification


def creer_dechet(db: Session, donnees: DechetCreation, cree_par_id: int) -> Dechet:
    dechet = Dechet(
        date=donnees.date,
        type=donnees.type,
        description=donnees.description,
        quantite=donnees.quantite,
        site_id=donnees.site_id,
        filiere=donnees.filiere,
        cree_par_id=cree_par_id,
    )
    db.add(dechet)
    db.commit()
    db.refresh(dechet)
    return dechet


def obtenir_dechet(db: Session, dechet_id: int) -> Dechet:
    dechet = db.get(Dechet, dechet_id)
    if dechet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Déchet introuvable")
    return dechet


def lister_dechets(db: Session) -> list[Dechet]:
    return list(db.scalars(select(Dechet).where(Dechet.archive.is_(False)).order_by(Dechet.date.desc())))


def modifier_dechet(db: Session, dechet: Dechet, donnees: DechetModification, modifie_par_id: int) -> Dechet:
    """Corrige les champs d'un lot (revue d'ensemble 2026-09-10). Modification
    partielle ; l'enlèvement se traite par sa route dédiée."""
    for champ, valeur in donnees.model_dump(exclude_unset=True).items():
        setattr(dechet, champ, valeur)
    dechet.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(dechet)
    return dechet


def archiver_dechet(db: Session, dechet: Dechet, modifie_par_id: int) -> Dechet:
    """Archivage logique (jamais de suppression, CLAUDE.md §2)."""
    dechet.archive = True
    dechet.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(dechet)
    return dechet


def enregistrer_enlevement(
    db: Session, dechet: Dechet, date_enlevement: date, justificatif: str | None, modifie_par_id: int
) -> Dechet:
    dechet.date_enlevement = date_enlevement
    if justificatif is not None:
        dechet.justificatif = justificatif
    dechet.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(dechet)
    return dechet
