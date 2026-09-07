"""Logique métier du module SLAM (prompt 2.2, section 5.2.2 du CDC)."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evaluation_slam import EvaluationSlam
from app.models.enums import DecisionSlam
from app.schemas.evaluation_slam import EvaluationSlamCreation
from app.services.notification_service import notifier_decision_no_go

logger = logging.getLogger("app.slam")


def creer_evaluation(db: Session, donnees: EvaluationSlamCreation, utilisateur_id: int) -> EvaluationSlam:
    evaluation = EvaluationSlam(
        utilisateur_id=utilisateur_id,
        etapes_validees=donnees.etapes_validees,
        decision=donnees.decision,
        motif=donnees.motif,
        date=datetime.now(timezone.utc),
        cree_par_id=utilisateur_id,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    # Règle 5.2.2 : une décision NO GO "ne peut faire l'objet d'une validation
    # hiérarchique : elle est enregistrée telle quelle et notifiée au
    # responsable" (tableau 3, chapitre 6.3 — prompt 4.4).
    if donnees.decision == DecisionSlam.NO_GO:
        notifier_decision_no_go(db, evaluation)
        logger.info(
            "NO GO enregistré par utilisateur id=%s (motif : %s) — responsable notifié",
            utilisateur_id,
            donnees.motif,
        )
    else:
        logger.info("GO enregistré par utilisateur id=%s", utilisateur_id)

    return evaluation
