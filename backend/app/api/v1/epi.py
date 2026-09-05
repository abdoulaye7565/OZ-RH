"""Routes du module EPI (prompt 2.1)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enums import StatutEpi, TypeEpi
from app.models.epi import Epi
from app.models.utilisateur import Utilisateur
from app.schemas.epi import (
    AffectationMiseAJour,
    EpiCreation,
    EpiSortie,
    ReformeEntree,
    VerificationAvantUtilisationEntree,
    VerificationPeriodiqueEntree,
)
from app.services.epi_service import (
    creer_epi,
    enregistrer_verification_avant_utilisation,
    enregistrer_verification_periodique,
    modifier_affectation,
    reformer,
    retirer,
    verifications_dues,
)

router = APIRouter(prefix="/epi", tags=["epi"])


def _recuperer(db: Session, epi_id: int) -> Epi:
    epi = db.get(Epi, epi_id)
    if epi is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="EPI introuvable")
    return epi


@router.post("", response_model=EpiSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: EpiCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_EPI)),
) -> Epi:
    return creer_epi(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[EpiSortie])
def lister(
    type: TypeEpi | None = None,
    statut: StatutEpi | None = None,
    porteur_id: int | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Epi]:
    # Consultation ouverte (section 5.3.2, Acteurs : "porteurs et responsables") :
    # pas de restriction de visibilité par rôle, comme pour les actions.
    requete = select(Epi).where(Epi.archive.is_(False))
    if type is not None:
        requete = requete.where(Epi.type == type)
    if statut is not None:
        requete = requete.where(Epi.statut == statut)
    if porteur_id is not None:
        requete = requete.where(Epi.porteur_id == porteur_id)
    return list(db.scalars(requete.order_by(Epi.numero)))


@router.get("/verifications-dues", response_model=list[EpiSortie])
def lister_verifications_dues(
    horizon_jours: int = 30,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Epi]:
    return verifications_dues(db, horizon_jours)


@router.get("/{epi_id}", response_model=EpiSortie)
def lire(
    epi_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Epi:
    return _recuperer(db, epi_id)


@router.patch("/{epi_id}/affectation", response_model=EpiSortie)
def affecter(
    epi_id: int,
    payload: AffectationMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_EPI)),
) -> Epi:
    epi = _recuperer(db, epi_id)
    return modifier_affectation(db, epi, payload.porteur_id, modifie_par_id=utilisateur.id)


@router.post("/{epi_id}/verification-periodique", response_model=EpiSortie)
def verification_periodique(
    epi_id: int,
    payload: VerificationPeriodiqueEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_EPI)),
) -> Epi:
    epi = _recuperer(db, epi_id)
    return enregistrer_verification_periodique(db, epi, payload.conforme, modifie_par_id=utilisateur.id)


@router.post("/{epi_id}/verification-avant-utilisation", response_model=EpiSortie)
def verification_avant_utilisation(
    epi_id: int,
    payload: VerificationAvantUtilisationEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Epi:
    # Depuis le mobile, par le porteur lui-même avant de monter : pas réservé
    # au référent SHEQ, contrairement à la vérification périodique.
    epi = _recuperer(db, epi_id)
    return enregistrer_verification_avant_utilisation(db, epi, payload.conforme, modifie_par_id=utilisateur.id)


@router.post("/{epi_id}/retirer", response_model=EpiSortie)
def retirer_route(
    epi_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_EPI)),
) -> Epi:
    epi = _recuperer(db, epi_id)
    return retirer(db, epi, modifie_par_id=utilisateur.id)


@router.post("/{epi_id}/reformer", response_model=EpiSortie)
def reformer_route(
    epi_id: int,
    payload: ReformeEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_EPI)),
) -> Epi:
    epi = _recuperer(db, epi_id)
    return reformer(db, epi, payload.motif, modifie_par_id=utilisateur.id)
