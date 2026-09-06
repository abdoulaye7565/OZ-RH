"""Schémas Pydantic du module Documents (prompt 4.3, section 5.3.5 du CDC)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import ConfidentialiteDocument, StatutDocument


class DocumentCreation(BaseModel):
    reference: str
    intitule: str
    niveau: int
    confidentialite: ConfidentialiteDocument = ConfidentialiteDocument.NORMAL
    date_revue: date | None = None

    @field_validator("niveau")
    @classmethod
    def _niveau_1_a_4(cls, v: int) -> int:
        if not (1 <= v <= 4):
            raise ValueError("le niveau documentaire doit être compris entre 1 et 4")
        return v


class AccuseLecture(BaseModel):
    utilisateur_id: int
    date: datetime


class DocumentSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    intitule: str
    niveau: int
    version: str
    redacteur_id: int
    approbateur_id: int | None
    statut: StatutDocument
    date_revue: date | None
    confidentialite: ConfidentialiteDocument
    fichier: str | None
    accuses_lecture: list[AccuseLecture] = []
    archive: bool
    cree_le: datetime
    modifie_le: datetime

    @field_validator("accuses_lecture", mode="before")
    @classmethod
    def _liste_jamais_nulle(cls, v: list | None) -> list:
        # La colonne est nullable en base (JSON, valeur initiale None tant
        # qu'aucun accusé n'existe) : jamais exposé comme null dans l'API,
        # toujours une liste, éventuellement vide.
        return v or []


class AlerteRevueDocumentSortie(BaseModel):
    document_id: int
    reference: str
    intitule: str
    date_revue: date
    jours_restants: int
    due: bool
