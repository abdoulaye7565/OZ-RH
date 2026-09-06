"""Schémas Pydantic du module Inspections (prompt 2.4, section 5.3.1 du CDC)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import CotationPoint, StatutInspection, TypeInspection


class PointInspectionEntree(BaseModel):
    point_checklist_id: int
    cotation: CotationPoint
    observation: str | None = None


class InspectionCreation(BaseModel):
    modele: TypeInspection
    site_id: int
    points: list[PointInspectionEntree]

    @field_validator("points")
    @classmethod
    def _au_moins_un_point(cls, v: list[PointInspectionEntree]) -> list[PointInspectionEntree]:
        if not v:
            raise ValueError("Une inspection doit comporter au moins un point coté")
        return v


class PointInspectionMiseAJour(BaseModel):
    points: list[PointInspectionEntree]


class PointInspectionSortie(BaseModel):
    point_checklist_id: int
    libelle: str
    cotation: CotationPoint
    observation: str | None = None
    photo: str | None = None


class InspectionSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    modele: TypeInspection
    site_id: int
    inspecteur_id: int
    date: date
    points: list[PointInspectionSortie]
    statut: StatutInspection
    archive: bool
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None
    # Calculé (Inspection.taux_conformite) : jamais stocké, voir app/models/inspection.py.
    taux_conformite: float | None = None


class PlanificationSortie(BaseModel):
    site_id: int
    modele: TypeInspection
    derniere_inspection_le: date
    prochaine_prevue_le: date
    jours_restants: int
    due: bool
