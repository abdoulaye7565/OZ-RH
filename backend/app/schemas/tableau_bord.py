"""Schémas Pydantic du tableau de bord (prompt 1.5, section 5.4 du CDC)."""
from datetime import datetime

from pydantic import BaseModel

from app.schemas.action import ActionSortie, SyntheseActions
from app.schemas.signalement import SignalementSortie


class SignalementParMois(BaseModel):
    annee: int
    mois: int
    nombre: int


class SignalementsResume(BaseModel):
    total_periode: int
    par_mois: list[SignalementParMois]
    nombre_a_traiter: int
    a_traiter: list[SignalementSortie]


class Periode(BaseModel):
    debut: datetime | None
    fin: datetime | None


class TableauBordSortie(BaseModel):
    periode: Periode
    site_id: int | None
    signalements: SignalementsResume
    actions: SyntheseActions
    echeances_proches: list[ActionSortie]
    # Familles d'indicateurs prévues au chapitre 5.4 du CDC mais dont le module
    # source n'existe pas encore (EPI : lot 2.1, inspections : lot 2.4,
    # formations/documents/environnement/satisfaction : lot 4). Listées plutôt
    # que simulées par une valeur inventée — "aucune donnée saisie manuellement"
    # s'applique aussi à "aucune donnée fabriquée".
    modules_non_disponibles: list[str]
