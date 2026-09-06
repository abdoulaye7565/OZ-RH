"""Schémas Pydantic du module Formations (prompt 4.2, section 5.3.3 du CDC)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

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
