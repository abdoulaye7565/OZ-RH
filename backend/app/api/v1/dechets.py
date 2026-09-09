"""Routes du module Déchets (prompt 4.3, section 5.3.6 du CDC)."""
from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.fichiers import enregistrer_justificatifs
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.dechet import Dechet
from app.models.utilisateur import Utilisateur
from app.schemas.dechet import DechetCreation, DechetSortie
from app.services.dechet_service import creer_dechet, enregistrer_enlevement, lister_dechets, obtenir_dechet

router = APIRouter(prefix="/dechets", tags=["dechets"])


@router.post("", response_model=DechetSortie, status_code=status.HTTP_201_CREATED)
def creer_dechet_route(
    payload: DechetCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DECHETS)),
) -> Dechet:
    """Enregistre un lot de déchets produit."""
    return creer_dechet(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[DechetSortie])
def lister_dechets_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Dechet]:
    """Liste les lots de déchets enregistrés."""
    return lister_dechets(db)


@router.post("/{dechet_id}/enlevement", response_model=DechetSortie)
async def enregistrer_enlevement_route(
    dechet_id: int,
    date_enlevement: date = Form(...),
    justificatif: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_DECHETS)),
) -> Dechet:
    """Enregistre l'enlèvement d'un lot de déchets, avec justificatif optionnel."""
    dechet = obtenir_dechet(db, dechet_id)
    chemin = (await enregistrer_justificatifs([justificatif], sous_dossier="dechets"))[0] if justificatif else None
    return enregistrer_enlevement(db, dechet, date_enlevement, chemin, modifie_par_id=utilisateur.id)
