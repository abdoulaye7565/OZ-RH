"""Schémas Pydantic du module Audits (prompt 4.2, section 5.3.4 du CDC)."""
# Alias nécessaire : ces schémas ont un champ nommé littéralement `date` (comme
# la fiche papier FOR-SHEQ-017, "Date : ..........") — pydantic évalue les
# annotations dans l'espace de noms de la classe, où l'attribut `date = None`
# (valeur par défaut du champ) masquerait le type importé `date` du module
# datetime, faisant échouer la résolution de type ("unsupported operand type(s)
# for |: 'NoneType' and 'NoneType'"). L'alias `dt` évite toute collision.
import datetime as dt
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import StatutInspection


class ExigenceAuditSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    chapitre: str
    libelle: str
    archive: bool


class CampagneCreation(BaseModel):
    date: dt.date | None = None


class CotationEntree(BaseModel):
    exigence_id: int
    cotation: int
    constat: str | None = None
    ecart: str | None = None

    @field_validator("cotation")
    @classmethod
    def _entre_0_et_2(cls, v: int) -> int:
        if not (0 <= v <= 2):
            raise ValueError("la cotation doit être 0 (absent), 1 (partiel) ou 2 (conforme)")
        return v


class CotationSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campagne_id: int
    exigence_id: int
    cotation: int
    constat: str | None
    ecart: str | None


class CampagneSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: dt.date
    auditeur_id: int
    statut: StatutInspection
    archive: bool
    cree_le: datetime


class ScoreParChapitre(BaseModel):
    chapitre: str
    score: int
    score_maximal: int
    taux_pourcent: float


class CampagneDetailSortie(CampagneSortie):
    cotations: list[CotationSortie] = []
    score_total: int
    score_maximal: int
    taux_conformite_pourcent: float
    # Interprétation indicative reprise de FOR-SHEQ-017 : "≥ 80 % système mature
    # | 50-79 % en construction | < 50 % prioriser les écarts".
    interpretation: str
    score_par_chapitre: list[ScoreParChapitre]


class EvolutionChapitre(BaseModel):
    chapitre: str
    taux_reference_pourcent: float
    taux_compare_pourcent: float
    evolution_points: float


class ComparaisonCampagnes(BaseModel):
    """Comparaison entre deux campagnes successives (section 5.3.4) — présentation
    soignée demandée par le prompt 4.2 : structure prête pour un graphique
    (delta signé, par chapitre) plutôt qu'un simple diff textuel."""

    campagne_reference: CampagneSortie
    campagne_comparee: CampagneSortie
    taux_reference_pourcent: float
    taux_compare_pourcent: float
    evolution_points: float
    par_chapitre: list[EvolutionChapitre]
