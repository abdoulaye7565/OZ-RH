"""Schémas Pydantic du module Formations (prompt 4.2, section 5.3.3 du CDC)."""
import datetime as _dt
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import StatutSeance


class CompetenceCreation(BaseModel):
    libelle: str
    periodicite_mois: int


class CompetenceSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str
    periodicite_mois: int
    archive: bool


class HabilitationCreation(BaseModel):
    utilisateur_id: int
    competence_id: int
    date_obtention: date


class HabilitationSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    utilisateur_id: int
    competence_id: int
    date_obtention: date
    date_expiration: date
    # Calculé (règle 5.3.3) : voir Habilitation.expiree.
    expiree: bool


class SeanceCreation(BaseModel):
    theme: str
    date: date
    lieu: str
    animateur_id: int
    competence_id: int | None = None


class SeanceModification(BaseModel):
    """Correction d'une séance encore planifiée (revue d'ensemble
    2026-09-10) — refusé une fois la séance réalisée (règle de service).
    Partielle. `date` qualifié `_dt.date` : le champ porte le même nom que le
    type et a une valeur par défaut (piège d'évaluation différée, Python 3.14)."""

    theme: str | None = None
    date: _dt.date | None = None
    lieu: str | None = None
    animateur_id: int | None = None
    competence_id: int | None = None

    @field_validator("theme", "lieu")
    @classmethod
    def _non_vide(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("ce champ ne peut pas être vide")
        return v.strip() if v is not None else None


class SeanceSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    theme: str
    date: date
    lieu: str
    animateur_id: int
    competence_id: int | None
    statut: StatutSeance
    archive: bool


class EmargementEntree(BaseModel):
    participant_id: int
    present: bool = True


class EmargementSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seance_id: int
    participant_id: int
    present: bool
    signe_le: datetime


class ChoixQuestionSortie(BaseModel):
    lettre: str
    texte: str


class QuestionQuizCreation(BaseModel):
    enonce: str
    choix: list[ChoixQuestionSortie]
    reponse_correcte: str


class QuestionQuizSortie(BaseModel):
    """Ne renvoie jamais `reponse_correcte` : cette sortie est celle que voit le
    participant avant de répondre — la sortie complète (référentiel géré par le
    référent SHEQ) utilise QuestionQuizAdminSortie."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    enonce: str
    choix: list[ChoixQuestionSortie]
    archive: bool


class QuestionQuizAdminSortie(QuestionQuizSortie):
    reponse_correcte: str


class ReponseEntree(BaseModel):
    question_id: int
    reponse: str


class TentativeQuizEntree(BaseModel):
    seance_id: int
    reponses: list[ReponseEntree]


class DetailReponseSortie(BaseModel):
    question_id: int
    correcte: bool


class TentativeQuizSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seance_id: int
    participant_id: int
    score: int
    total_questions: int
    reussi: bool
    date_passation: datetime
    # Calculé à la volée par le service (pas stocké : reponses/score suffisent
    # à le reconstituer, éviter une colonne redondante).
    details: list[DetailReponseSortie] = []


class LigneMatriceCompetence(BaseModel):
    utilisateur_id: int
    competence_id: int
    libelle_competence: str
    date_obtention: date | None
    date_expiration: date | None
    expiree: bool


class AlerteRecyclageSortie(BaseModel):
    habilitation_id: int
    utilisateur_id: int
    competence_id: int
    libelle_competence: str
    date_expiration: date
    jours_restants: int
    due: bool
