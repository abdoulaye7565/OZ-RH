"""Routes du module Actions (prompt 1.2)."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, not_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.pagination import Pagination, pagination
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.action import Action
from app.models.enums import StatutAction
from app.models.utilisateur import Utilisateur
from app.schemas.action import (
    ActionCreation,
    ActionModification,
    ActionSortie,
    AvancementMiseAJour,
    StatutMiseAJour,
    SyntheseActions,
)
from app.services.action_service import (
    calculer_synthese,
    changer_statut,
    creer_action,
    mettre_a_jour_avancement,
    modifier_action,
)

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
    """Crée une action corrective ou préventive. Doit être rattachée à exactement
    une origine (risque, signalement, inspection, cotation d'audit ou réponse de
    satisfaction) — validé côté serveur."""
    return creer_action(db, payload, cree_par_id=utilisateur.id)


@router.get("", response_model=list[ActionSortie])
def lister(
    statut: StatutAction | None = None,
    responsable_id: int | None = None,
    en_retard: bool | None = None,
    page: Pagination = Depends(pagination),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Action]:
    """Liste les actions non archivées, avec filtres optionnels par statut,
    responsable et retard, et pagination (`limite`/`decalage`). Consultation
    ouverte à tout le personnel, sans restriction de visibilité par rôle,
    contrairement aux signalements."""
    requete = select(Action).where(Action.archive.is_(False))
    if statut is not None:
        requete = requete.where(Action.statut == statut)
    if responsable_id is not None:
        requete = requete.where(Action.responsable_id == responsable_id)
    if en_retard is not None:
        # `en_retard` est calculé (statut != clôturée ET échéance dépassée) —
        # exprimé ici en SQL pour que la pagination reste juste, plutôt que de
        # tout charger puis filtrer en Python.
        condition = and_(Action.statut != StatutAction.CLOTUREE, Action.echeance < date.today())
        requete = requete.where(condition if en_retard else not_(condition))

    requete = page.appliquer(requete.order_by(Action.echeance.asc()))
    return list(db.scalars(requete))


@router.get("/synthese", response_model=SyntheseActions)
def synthese(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> SyntheseActions:
    """Renvoie les indicateurs agrégés sur les actions (répartition par statut,
    retards, etc.)."""
    return calculer_synthese(db)


@router.get("/{action_id}", response_model=ActionSortie)
def lire(
    action_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    """Récupère une action par son identifiant."""
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    return action


@router.patch("/{action_id}", response_model=ActionSortie)
def modifier_route(
    action_id: int,
    payload: ActionModification,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    """Corrige le libellé, le type de mesure, le responsable ou l'échéance d'une
    action (faute de saisie, réaffectation). Réservé au responsable désigné ou
    à un rôle de gestion globale ; refusé sur une action clôturée."""
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    if not _peut_gerer(action, utilisateur):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return modifier_action(db, action, payload, modifie_par_id=utilisateur.id)


@router.patch("/{action_id}/avancement", response_model=ActionSortie)
def mettre_a_jour(
    action_id: int,
    payload: AvancementMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    """Met à jour l'avancement (pourcentage, indicateur) d'une action. Réservé au
    responsable désigné de l'action ou à un rôle de gestion globale des actions."""
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    if not _peut_gerer(action, utilisateur):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return mettre_a_jour_avancement(db, action, payload.avancement, payload.indicateur, modifie_par_id=utilisateur.id)


@router.patch("/{action_id}/statut", response_model=ActionSortie)
def mettre_a_jour_statut(
    action_id: int,
    payload: StatutMiseAJour,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Action:
    """Change le statut d'une action (par exemple clôture). Réservé au responsable
    désigné de l'action ou à un rôle de gestion globale des actions."""
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    if not _peut_gerer(action, utilisateur):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return changer_statut(db, action, payload.statut, modifie_par_id=utilisateur.id)
