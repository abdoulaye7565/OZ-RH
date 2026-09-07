"""Schémas Pydantic du module Notifications (prompt 4.4, chapitre 6.3 du CDC,
tableau 3)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import CanalNotification, TypeNotification


class NotificationSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destinataire_id: int
    type: TypeNotification
    message: str
    objet_type: str | None
    objet_id: int | None
    canal: CanalNotification
    lue: bool
    lue_le: datetime | None
    courriel_envoye: bool | None
    courriel_erreur: str | None
    cree_le: datetime


class CompteurNonLuesSortie(BaseModel):
    non_lues: int


class RapportTachesPlanifieesSortie(BaseModel):
    """Résumé d'une exécution du planificateur (chapitre 6.3) — utile pour la
    route de déclenchement manuel et pour les journaux d'exploitation."""

    actions_notifiees: int
    epi_notifies: int
    inspections_notifiees: int
    documents_notifies: int
