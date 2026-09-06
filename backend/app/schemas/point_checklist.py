"""Schémas Pydantic du référentiel de checklists (prompt 2.4)."""
from pydantic import BaseModel, ConfigDict

from app.models.enums import TypeInspection


class PointChecklistCreation(BaseModel):
    type_inspection: TypeInspection
    categorie: str | None = None
    ordre: int
    libelle: str


class PointChecklistSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type_inspection: TypeInspection
    categorie: str | None
    ordre: int
    libelle: str
    archive: bool
