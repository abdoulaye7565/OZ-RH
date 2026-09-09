"""Schémas Pydantic de l'entité SITE (hors dictionnaire, chapitre 5.2.3 du CDC)."""
from pydantic import BaseModel, ConfigDict

from app.models.enums import TypeSite


class SiteSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    type: TypeSite
    adresse: str | None
