"""Routes du module Notifications (prompt 4.4, chapitre 6.3 du CDC)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import RoleUtilisateur
from app.models.notification import Notification
from app.models.utilisateur import Utilisateur
from app.schemas.notification import CompteurNonLuesSortie, NotificationSortie, RapportTachesPlanifieesSortie
from app.services.notification_service import (
    compteur_non_lues,
    executer_taches_planifiees,
    lister_notifications,
    marquer_lue,
    marquer_toutes_lues,
    obtenir_notification,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationSortie])
def lister_notifications_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Notification]:
    """Liste les notifications de l'utilisateur connecté. La plupart sont
    générées automatiquement par les événements applicatifs et le planificateur,
    pas créées manuellement via l'API."""
    return lister_notifications(db, utilisateur.id)


@router.get("/compteur", response_model=CompteurNonLuesSortie)
def compteur_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> dict:
    """Renvoie le nombre de notifications non lues de l'utilisateur connecté."""
    return {"non_lues": compteur_non_lues(db, utilisateur.id)}


@router.post("/toutes-lues", response_model=CompteurNonLuesSortie)
def marquer_toutes_lues_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> dict:
    """Marque toutes les notifications de l'utilisateur connecté comme lues."""
    marquer_toutes_lues(db, utilisateur.id)
    return {"non_lues": 0}


@router.post("/{notification_id}/lue", response_model=NotificationSortie)
def marquer_lue_route(
    notification_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Notification:
    """Marque une notification de l'utilisateur connecté comme lue."""
    notification = obtenir_notification(db, notification_id, utilisateur.id)
    return marquer_lue(db, notification)


@router.post("/executer-taches", response_model=RapportTachesPlanifieesSortie)
def executer_taches_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(RoleUtilisateur.ADMINISTRATEUR)),
) -> dict:
    """Déclenche manuellement les tâches planifiées (alertes d'échéances, etc.)
    normalement exécutées chaque jour par le planificateur. Réservé à
    l'administrateur, utile en exploitation ou en débogage."""
    # Déclenchement manuel (exploitation/débogage) — le planificateur
    # (app/core/scheduler.py) appelle la même fonction de service
    # automatiquement chaque jour ; ce n'est pas un second chemin de code.
    return executer_taches_planifiees(db)
