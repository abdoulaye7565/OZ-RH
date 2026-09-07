"""Routes du module Inspections (prompt 2.4)."""
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.fichiers import enregistrer_photos
from app.db.session import get_db
from app.models.action import Action
from app.models.enums import StatutInspection, TypeInspection
from app.models.inspection import Inspection
from app.models.site import Site
from app.models.utilisateur import Utilisateur
from app.schemas.action import ActionSortie
from app.schemas.inspection import (
    InspectionCreation,
    InspectionSortie,
    PlanificationSortie,
    PointInspectionMiseAJour,
)
from app.services.inspection_service import (
    ajouter_photo,
    cloturer,
    creer_inspection,
    generer_pdf,
    mettre_a_jour_points,
    planification,
)

router = APIRouter(prefix="/inspections", tags=["inspections"])


def _recuperer(db: Session, inspection_id: int) -> Inspection:
    inspection = db.get(Inspection, inspection_id)
    if inspection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection introuvable")
    return inspection


@router.post("", response_model=InspectionSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: InspectionCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Inspection:
    return creer_inspection(db, payload, inspecteur_id=utilisateur.id)


@router.get("", response_model=list[InspectionSortie])
def lister(
    modele: TypeInspection | None = None,
    site_id: int | None = None,
    statut: StatutInspection | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Inspection]:
    requete = select(Inspection).where(Inspection.archive.is_(False))
    if modele is not None:
        requete = requete.where(Inspection.modele == modele)
    if site_id is not None:
        requete = requete.where(Inspection.site_id == site_id)
    if statut is not None:
        requete = requete.where(Inspection.statut == statut)
    return list(db.scalars(requete.order_by(Inspection.date.desc())))


@router.get("/planification", response_model=list[PlanificationSortie])
def planification_route(
    horizon_jours: int = 7,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[dict]:
    return planification(db, horizon_jours)


@router.get("/{inspection_id}", response_model=InspectionSortie)
def lire(
    inspection_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Inspection:
    return _recuperer(db, inspection_id)


@router.get("/{inspection_id}/export-pdf")
def exporter_pdf(
    inspection_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Response:
    inspection = _recuperer(db, inspection_id)
    inspecteur = db.get(Utilisateur, inspection.inspecteur_id)
    site = db.get(Site, inspection.site_id)
    contenu = generer_pdf(db, inspection, inspecteur, site)
    reference = inspection.reference or f"inspection-{inspection.id}"
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{reference}.pdf"'},
    )


@router.patch("/{inspection_id}/points", response_model=InspectionSortie)
def mettre_a_jour(
    inspection_id: int,
    payload: PointInspectionMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Inspection:
    inspection = _recuperer(db, inspection_id)
    return mettre_a_jour_points(db, inspection, payload.points, modifie_par_id=utilisateur.id)


@router.post("/{inspection_id}/points/{point_checklist_id}/photo", response_model=InspectionSortie)
async def deposer_photo(
    inspection_id: int,
    point_checklist_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Inspection:
    inspection = _recuperer(db, inspection_id)
    chemins = await enregistrer_photos([photo], sous_dossier="inspections", nombre_max=1)
    return ajouter_photo(db, inspection, point_checklist_id, chemins[0], modifie_par_id=utilisateur.id)


@router.post("/{inspection_id}/cloturer", response_model=InspectionSortie)
def cloturer_route(
    inspection_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Inspection:
    inspection = _recuperer(db, inspection_id)
    inspection, _actions = cloturer(db, inspection, modifie_par_id=utilisateur.id)
    return inspection


@router.get("/{inspection_id}/actions-generees", response_model=list[ActionSortie])
def actions_generees(
    inspection_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list:
    _recuperer(db, inspection_id)  # 404 si l'inspection n'existe pas
    return list(db.scalars(select(Action).where(Action.inspection_id == inspection_id)))
