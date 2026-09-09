"""Routes de l'entité SITE (hors dictionnaire, chapitre 5.2.3 du CDC).

Aucune route de création n'existe : les sites sont peu nombreux et créés
directement en base à ce stade (voir docs/JOURNAL.md, prompt 5.3) — seule la
consultation est nécessaire pour l'instant, pour résoudre un site_id en nom
affichable côté écran (équipements, permis, inspections, déchets, visiteurs)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.site import Site
from app.models.utilisateur import Utilisateur
from app.schemas.site import SiteSortie

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteSortie])
def lister_sites_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Site]:
    """Liste les sites non archivés."""
    return list(db.scalars(select(Site).where(Site.archive.is_(False)).order_by(Site.nom)))
