"""Schémas Pydantic du module Signalements.

La création se fait en multipart/form-data (champs + photos dans la même
requête), pas en JSON : FastAPI ne permet pas de mélanger un modèle Pydantic et
des fichiers dans un même corps de requête. Les champs de saisie sont donc reçus
individuellement en paramètres Form() dans la route elle-même ; ce schéma sert à
la lecture (réponses) et à la mise à jour du statut."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatutSignalement, TypeSignalement


class SignalementSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str | None
    type: TypeSignalement
    site_id: int
    lieu: str
    description: str
    photos: list[str] | None
    anonyme: bool
    auteur_id: int | None
    date_constat: datetime
    date_saisie: datetime
    causes: str | None
    risque_id: int | None
    statut: StatutSignalement
    archive: bool


class StatutMiseAJour(BaseModel):
    statut: StatutSignalement
