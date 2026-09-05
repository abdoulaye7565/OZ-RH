"""Route du tableau de bord (prompt 1.5)."""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.tableau_bord import TableauBordSortie
from app.services.tableau_bord_service import construire_tableau_de_bord

router = APIRouter(prefix="/tableau-de-bord", tags=["tableau de bord"])


@router.get("", response_model=TableauBordSortie)
def obtenir(
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    site_id: int | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.CONSULTER_TABLEAU_BORD)),
) -> TableauBordSortie:
    return construire_tableau_de_bord(db, date_debut=date_debut, date_fin=date_fin, site_id=site_id)
