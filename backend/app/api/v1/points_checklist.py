"""Routes du référentiel de checklists (prompt 2.4)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enums import TypeInspection
from app.models.point_checklist import PointChecklist
from app.models.utilisateur import Utilisateur
from app.schemas.point_checklist import PointChecklistCreation, PointChecklistSortie
from app.services.point_checklist_service import archiver_point, creer_point, lister_points

router = APIRouter(prefix="/points-checklist", tags=["checklists"])


@router.get("", response_model=list[PointChecklistSortie])
def lister(
    type_inspection: TypeInspection,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[PointChecklist]:
    return lister_points(db, type_inspection)


@router.post("", response_model=PointChecklistSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: PointChecklistCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_CHECKLISTS)),
) -> PointChecklist:
    return creer_point(db, payload, cree_par_id=utilisateur.id)


@router.post("/{point_id}/archiver", response_model=PointChecklistSortie)
def archiver(
    point_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_CHECKLISTS)),
) -> PointChecklist:
    point = db.get(PointChecklist, point_id)
    if point is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Point de checklist introuvable")
    return archiver_point(db, point, modifie_par_id=utilisateur.id)
