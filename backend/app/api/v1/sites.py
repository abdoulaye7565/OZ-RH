"""Routes de l'entité SITE (hors dictionnaire, chapitre 5.2.3 du CDC).

Consultation ouverte à tout le personnel (résolution d'un site_id en nom
affichable : équipements, permis, inspections, déchets, visiteurs). Création,
modification et archivage réservés à l'administrateur — ajout du 2026-09-10
(retour direct de l'utilisateur : « on a un seul site alors que nous
intervenons sur plusieurs sites »).
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.site import Site
from app.models.utilisateur import Utilisateur
from app.schemas.site import SiteCreation, SiteMiseAJour, SiteSortie
from app.services import site_service

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteSortie])
def lister_sites_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Site]:
    """Liste les sites non archivés."""
    return site_service.lister_sites(db)


@router.post("", response_model=SiteSortie, status_code=status.HTTP_201_CREATED)
def creer_site_route(
    payload: SiteCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SITES)),
) -> Site:
    """Crée un site (siège ou site client)."""
    return site_service.creer_site(db, payload, cree_par_id=utilisateur.id)


@router.patch("/{site_id}", response_model=SiteSortie)
def modifier_site_route(
    site_id: int,
    payload: SiteMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SITES)),
) -> Site:
    """Modifie le nom, le type ou l'adresse d'un site."""
    site = site_service.obtenir_site(db, site_id)
    return site_service.modifier_site(db, site, payload, modifie_par_id=utilisateur.id)


@router.post("/{site_id}/archiver", response_model=SiteSortie)
def archiver_site_route(
    site_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_SITES)),
) -> Site:
    """Archive un site (jamais de suppression). Refusé s'il reste des
    équipements rattachés ou des permis en cours."""
    site = site_service.obtenir_site(db, site_id)
    return site_service.archiver_site(db, site, modifie_par_id=utilisateur.id)
