"""Schémas Pydantic de l'entité SITE (hors dictionnaire, chapitre 5.2.3 du CDC)."""
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import TypeSite


class SiteCreation(BaseModel):
    nom: str
    type: TypeSite
    adresse: str | None = None

    @field_validator("nom")
    @classmethod
    def _nom_non_vide(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le nom du site est obligatoire")
        return v.strip()


class SiteMiseAJour(BaseModel):
    """Modification partielle : seuls les champs fournis sont appliqués."""

    nom: str | None = None
    type: TypeSite | None = None
    adresse: str | None = None

    @field_validator("nom")
    @classmethod
    def _nom_non_vide(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Le nom du site ne peut pas être vide")
        return v.strip() if v is not None else None


class SiteSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    type: TypeSite
    adresse: str | None
