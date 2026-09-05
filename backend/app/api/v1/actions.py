"""Routes du module Actions (prompt 1.2)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.action import Action
from app.models.enums import StatutAction
from app.models.utilisateur import Utilisateur
from app.schemas.action import ActionCreation, ActionSortie, AvancementMiseAJour, StatutMiseAJour, SyntheseActions
from app.services.action_service import calculer_synthese, changer_statut, creer_action, mettre_a_jour_avancement

router = APIRouter(prefix="/actions", tags=["actions"])


def _peut_gerer(action: Action, utilisateur: Utilisateur) -> bool:
    """Rédaction/gestion globale : référent SHEQ et administrateur (section 5.2.5,
    Acteurs). Le responsable désigné d'UNE action peut aussi en suivre l'avancement
    et la clôturer — c'est lui qui l'exécute sur le terrain."""
    if utilisateur.role in Permissions.GERER_ACTIONS:
        return True
    return action.responsable_id == utilisateur.id


@router.post("", response_model=ActionSortie, status_code=status.HTTP_201_CREATED)
def creer(
    payload: ActionCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_ACTIONS)),
) -> Action:
    return creer_action(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[ActionSortie])
def lister(
    statut: StatutAction | None = None,
    responsable_id: int | None = None,
    en_retard: bool | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Action]:
    # Consultation ouverte à tout le personnel (section 5.2.5, Acteurs) : aucune
    # restriction de visibilité par rôle, contrairement aux signalements.
    requete = select(Action).where(Action.archive.is_(False))
    if statut is not None:
        requete = requete.where(Action.statut == statut)
    if responsable_id is not None:
        requete = requete.where(Action.responsable_id == responsable_id)

    actions = list(db.scalars(requete.order_by(Action.echeance.asc())))
    if en_retard is not None:
        actions = [a for a in actions if a.en_retard == en_retard]
    return actions


@router.get("/synthese", response_model=SyntheseActions)
def synthese(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> SyntheseActions:
    return calculer_synthese(db)


@router.get("/{action_id}", response_model=ActionSortie)
def lire(
    action_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    return action


@router.patch("/{action_id}/avancement", response_model=ActionSortie)
def mettre_a_jour(
    action_id: int,
    payload: AvancementMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    if not _peut_gerer(action, utilisateur):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return mettre_a_jour_avancement(db, action, payload.avancement, payload.indicateur)


@router.patch("/{action_id}/statut", response_model=ActionSortie)
def mettre_a_jour_statut(
    action_id: int,
    payload: StatutMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    if not _peut_gerer(action, utilisateur):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return changer_statut(db, action, payload.statut)
