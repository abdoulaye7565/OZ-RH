"""Schémas Pydantic du module Revues de direction (prompt 4.2, section 5.3.4
du CDC, FOR-SHEQ-016)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatutDecisionRevue


class RevueCreation(BaseModel):
    date: date
    lieu: str | None = None
    periode_debut: date
    periode_fin: date
    participants: str | None = None


class DecisionCreation(BaseModel):
    libelle: str
    responsable_id: int
    echeance: date


class CommentaireEntree(BaseModel):
    texte: str


class DecisionSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    revue_id: int
    libelle: str
    responsable_id: int
    echeance: date
    statut: StatutDecisionRevue


class RevueSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str | None
    date: date
    lieu: str | None
    redacteur_id: int
    periode_debut: date
    periode_fin: date
    participants: str | None
    # Instantané assemblé à la création (voir app/models/revue_direction.py) :
    # indicateurs de la période + décisions non soldées reportées.
    donnees_entree: dict
    # Prompt 6.4 : commentaire de synthèse pré-rédigé, brouillon tant que
    # commentaire_valide vaut False (voir app/models/revue_direction.py).
    commentaire_ia: str | None
    commentaire_valide: bool
    archive: bool
    cree_le: datetime


class RevueDetailSortie(RevueSortie):
    decisions: list[DecisionSortie] = []
