"""Schémas Pydantic du module Déchets (prompt 4.3, section 5.3.6 du CDC,
REG-SHEQ-005)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DechetCreation(BaseModel):
    date: date
    type: str
    description: str
    quantite: str
    site_id: int
    filiere: str


class DechetSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    type: str
    description: str
    quantite: str
    site_id: int
    filiere: str
    date_enlevement: date | None
    justificatif: str | None
    archive: bool
    cree_le: datetime
