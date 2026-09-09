"""Routes du module Visiteurs (prompt 4.3, section 5.3.6 du CDC)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.models.visiteur import Visiteur
from app.schemas.visiteur import VisiteurCreation, VisiteurSortie
from app.services.visiteur_service import (
    enregistrer_depart,
    enregistrer_visiteur,
    lister_visiteurs,
    obtenir_visiteur,
    visiteurs_presents,
)

router = APIRouter(prefix="/visiteurs", tags=["visiteurs"])

# Section 5.3.6, "Acteurs" : "Visiteurs : accueil" — aucun rôle "accueil"
# distinct dans la matrice (point 6, CLAUDE.md) : ouvert à tout utilisateur
# authentifié plutôt que restreint (voir app/core/permissions.py).


@router.post("", response_model=VisiteurSortie, status_code=status.HTTP_201_CREATED)
def enregistrer_visiteur_route(
    payload: VisiteurCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Visiteur:
    """Enregistre l'arrivée d'un visiteur sur site."""
    return enregistrer_visiteur(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[VisiteurSortie])
def lister_visiteurs_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Visiteur]:
    """Liste l'ensemble des visiteurs enregistrés, présents et partis."""
    return lister_visiteurs(db)


@router.get("/presents", response_model=list[VisiteurSortie])
def visiteurs_presents_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Visiteur]:
    """Liste les visiteurs actuellement présents sur site, sans départ enregistré
    — utilisable en cas d'évacuation."""
    # Section 5.3.6 : "liste des personnes présentes sur le site, utilisable
    # en cas d'évacuation" — déclarée avant "/{visiteur_id}" pour ne pas être
    # capturée par cette route paramétrée.
    return visiteurs_presents(db)


@router.post("/{visiteur_id}/depart", response_model=VisiteurSortie)
def enregistrer_depart_route(
    visiteur_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Visiteur:
    """Enregistre le départ d'un visiteur."""
    visiteur = obtenir_visiteur(db, visiteur_id)
    return enregistrer_depart(db, visiteur, modifie_par_id=utilisateur.id)
