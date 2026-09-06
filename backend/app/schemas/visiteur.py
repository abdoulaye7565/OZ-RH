"""Schémas Pydantic du module Visiteurs (prompt 4.3, section 5.3.6 du CDC,
REG-SHEQ-004)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class VisiteurCreation(BaseModel):
    nom: str
    societe: str | None = None
    motif: str
    personne_visitee: str | None = None
    # Règle 5.3.6 : "un visiteur ne peut être enregistré sans validation de la
    # lecture des consignes de sécurité" — obligatoire et doit être vrai (pas
    # seulement présent), vérifié une seconde fois côté service.
    consignes_lues: bool

    @field_validator("consignes_lues")
    @classmethod
    def _consignes_obligatoires(cls, v: bool) -> bool:
        if not v:
            raise ValueError("les consignes de sécurité doivent être lues et validées avant tout enregistrement")
        return v


class VisiteurSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    societe: str | None
    motif: str
    personne_visitee: str | None
    heure_arrivee: datetime
    heure_depart: datetime | None
    consignes_lues: bool
    # Calculé (règle 6, CLAUDE.md) : voir Visiteur.present.
    present: bool
