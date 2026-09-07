"""Routes du module SLAM (prompt 2.2)."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.evaluation_slam import EvaluationSlam
from app.models.slam_referentiel import ETAPES_SLAM
from app.models.utilisateur import Utilisateur
from app.schemas.evaluation_slam import EvaluationSlamCreation, EvaluationSlamSortie
from app.services.evaluation_slam_service import creer_evaluation, generer_pdf

router = APIRouter(prefix="/slam", tags=["slam"])


@router.get("/referentiel")
def referentiel() -> list[dict]:
    """Contenu canonique des 4 étapes — évite de dupliquer ce texte dans le
    client mobile (prompt 2.3)."""
    return ETAPES_SLAM


@router.post("", response_model=EvaluationSlamSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: EvaluationSlamCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> EvaluationSlam:
    # Toujours pour soi-même : aucun champ utilisateur_id dans le payload, pas
    # de risque qu'un intervenant enregistre un GO au nom d'un autre.
    return creer_evaluation(db, payload, utilisateur_id=utilisateur.id)


@router.get("/mes-evaluations", response_model=list[EvaluationSlamSortie])
def mes_evaluations(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[EvaluationSlam]:
    from sqlalchemy import select

    requete = (
        select(EvaluationSlam)
        .where(EvaluationSlam.utilisateur_id == utilisateur.id)
        .order_by(EvaluationSlam.date.desc())
    )
    return list(db.scalars(requete))


@router.get("/{evaluation_id}", response_model=EvaluationSlamSortie)
def lire(
    evaluation_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> EvaluationSlam:
    evaluation = db.get(EvaluationSlam, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Évaluation SLAM introuvable")
    return evaluation


@router.get("/{evaluation_id}/export-pdf")
def exporter_pdf(
    evaluation_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Response:
    evaluation = db.get(EvaluationSlam, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Évaluation SLAM introuvable")
    intervenant = db.get(Utilisateur, evaluation.utilisateur_id)
    contenu = generer_pdf(db, evaluation, intervenant)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{evaluation.reference}.pdf"'},
    )
