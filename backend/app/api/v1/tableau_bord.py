"""Route du tableau de bord (prompt 1.5)."""
from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.tableau_bord import TableauBordSortie
from app.services.tableau_bord_service import construire_tableau_de_bord, generer_pdf

router = APIRouter(prefix="/tableau-de-bord", tags=["tableau de bord"])


@router.get("", response_model=TableauBordSortie)
def obtenir(
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    site_id: int | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.CONSULTER_TABLEAU_BORD)),
) -> TableauBordSortie:
    """Construit les indicateurs SHEQ agrégés du tableau de bord, filtrables par
    période et par site."""
    return construire_tableau_de_bord(db, date_debut=date_debut, date_fin=date_fin, site_id=site_id)


@router.get("/export-pdf")
def exporter_pdf(
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    site_id: int | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.CONSULTER_TABLEAU_BORD)),
) -> Response:
    """Génère le PDF du tableau de bord pour la période et le site donnés."""
    tableau = construire_tableau_de_bord(db, date_debut=date_debut, date_fin=date_fin, site_id=site_id)
    contenu = generer_pdf(tableau, utilisateur)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="tableau-de-bord.pdf"'},
    )
