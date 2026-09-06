"""Schémas Pydantic du module Satisfaction client (prompt 4.3, section 5.3.6
du CDC, FOR-SHEQ-018)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import Recommandation


class EnqueteCreation(BaseModel):
    client: str
    site_id: int | None = None
    intervention: str
    technicien_id: int | None = None


class EnqueteSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    jeton: str
    client: str
    site_id: int | None
    intervention: str
    technicien_id: int | None
    envoyee_le: datetime
    repondu: bool


class QuestionnaireSortie(BaseModel):
    """Vue publique, sans authentification : uniquement ce qu'il faut pour
    afficher le formulaire (section 5.3.6 : "envoi par lien public sans
    compte")."""

    client: str
    intervention: str
    criteres: list[str]


class NoteCritereEntree(BaseModel):
    critere: str
    note: int

    @field_validator("note")
    @classmethod
    def _note_1_a_5(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError("la note doit être comprise entre 1 et 5")
        return v


class ReponseEntree(BaseModel):
    notes: list[NoteCritereEntree]
    recommandation: Recommandation
    remarques: str | None = None


class NoteCritereSortie(BaseModel):
    critere: str
    note: int


class ReponseSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enquete_id: int
    notes: list[NoteCritereSortie]
    recommandation: Recommandation
    remarques: str | None
    necessite_analyse: bool
    date_reponse: datetime
