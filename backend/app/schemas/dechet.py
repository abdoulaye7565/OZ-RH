"""Schémas Pydantic du module Déchets (prompt 4.3, section 5.3.6 du CDC,
REG-SHEQ-005)."""
import datetime as _dt
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DechetCreation(BaseModel):
    date: date
    type: str
    description: str
    quantite: str
    site_id: int
    filiere: str


class DechetModification(BaseModel):
    """Correction d'un lot de déchets (faute de saisie) — revue d'ensemble
    2026-09-10. Modification partielle (`exclude_unset`). L'enlèvement et son
    justificatif se traitent par leur route dédiée, pas ici.

    Le champ `date` porte le même nom que le type `datetime.date` ; comme il a
    une valeur par défaut, ce nom masquerait le type au moment où Pydantic
    résout l'annotation (évaluation différée, Python 3.14). On qualifie donc
    par `_dt.date` ici — sans effet sur le nom du champ côté API.
    """

    date: _dt.date | None = None
    type: str | None = None
    description: str | None = None
    quantite: str | None = None
    site_id: int | None = None
    filiere: str | None = None


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
