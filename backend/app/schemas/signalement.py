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
    # Traçabilité (règle 3, CLAUDE.md ; cas de recette 13, CDC chapitre 14) :
    # horodatage et auteur de la création et de la dernière modification.
    # cree_par_id reste vide si le signalement est anonyme (jamais l'inverse
    # pour modifie_par_id : qui le TRAITE ensuite n'a pas à rester anonyme).
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None


class StatutMiseAJour(BaseModel):
    statut: StatutSignalement
