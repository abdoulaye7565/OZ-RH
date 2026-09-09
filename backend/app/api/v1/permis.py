"""Routes du module Permis (prompt 2.2)."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enums import StatutPermis
from app.models.permis import Permis
from app.models.site import Site
from app.models.utilisateur import Utilisateur
from app.schemas.permis import PermisCreation, PermisSortie, RefusEntree
from app.services.permis_service import cloturer, creer_permis, generer_pdf, refuser, valider

router = APIRouter(prefix="/permis", tags=["permis"])


def _recuperer(db: Session, permis_id: int) -> Permis:
    permis = db.get(Permis, permis_id)
    if permis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permis introuvable")
    return permis


@router.post("", response_model=PermisSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: PermisCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Permis:
    """Crée un permis de travail, ouvert à tout utilisateur authentifié. Le
    permis n'est réellement utilisable qu'une fois validé : la règle de
    blocage (EPI non conforme, absence de SLAM GO, absence de surveillant,
    surveillant parmi les intervenants) est évaluée côté serveur à la
    validation, pas à la création."""
    return creer_permis(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[PermisSortie])
def lister(
    statut: StatutPermis | None = None,
    site_id: int | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Permis]:
    """Liste les permis non archivés, avec filtres optionnels par statut et
    site."""
    requete = select(Permis).where(Permis.archive.is_(False))
    if statut is not None:
        requete = requete.where(Permis.statut == statut)
    if site_id is not None:
        requete = requete.where(Permis.site_id == site_id)
    return list(db.scalars(requete.order_by(Permis.debut_validite.desc())))


@router.get("/{permis_id}", response_model=PermisSortie)
def lire(
    permis_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Permis:
    """Récupère un permis par son identifiant."""
    return _recuperer(db, permis_id)


@router.get("/{permis_id}/export-pdf")
def exporter_pdf(
    permis_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Response:
    """Génère le PDF d'un permis."""
    permis = _recuperer(db, permis_id)
    site = db.get(Site, permis.site_id)
    surveillant = db.get(Utilisateur, permis.surveillant_id) if permis.surveillant_id else None
    validateur = db.get(Utilisateur, permis.validateur_id) if permis.validateur_id else None
    contenu = generer_pdf(permis, site, surveillant, validateur)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{permis.reference}.pdf"'},
    )


@router.post("/{permis_id}/valider", response_model=PermisSortie)
def valider_route(
    permis_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.VALIDER_PERMIS)),
) -> Permis:
    """Valide un permis, réservé aux rôles habilités à valider. C'est ici
    qu'est évaluée la règle de blocage : la validation est refusée si un EPI
    affecté à un intervenant n'est pas conforme, si un intervenant n'a pas
    d'évaluation SLAM GO, si aucun surveillant n'est désigné, ou si le
    surveillant figure parmi les intervenants — la réponse liste les conditions
    non satisfaites."""
    permis = _recuperer(db, permis_id)
    return valider(db, permis, validateur_id=utilisateur.id)


@router.post("/{permis_id}/refuser", response_model=PermisSortie)
def refuser_route(
    permis_id: int,
    payload: RefusEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.VALIDER_PERMIS)),
) -> Permis:
    """Refuse un permis avec un motif obligatoire, réservé aux rôles habilités à
    valider."""
    permis = _recuperer(db, permis_id)
    return refuser(db, permis, payload.motif, modifie_par_id=utilisateur.id)


@router.post("/{permis_id}/cloturer", response_model=PermisSortie)
def cloturer_route(
    permis_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.VALIDER_PERMIS)),
) -> Permis:
    """Clôture un permis, réservé aux rôles habilités à valider."""
    permis = _recuperer(db, permis_id)
    return cloturer(db, permis, modifie_par_id=utilisateur.id)
