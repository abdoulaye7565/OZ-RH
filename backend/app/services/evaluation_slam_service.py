"""Logique métier du module SLAM (prompt 2.2, section 5.2.2 du CDC)."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.evaluation_slam import EvaluationSlam
from app.models.enums import DecisionSlam
from app.models.slam_referentiel import ETAPES_SLAM
from app.schemas.evaluation_slam import EvaluationSlamCreation
from app.services.notification_service import notifier_decision_no_go
from app.services.reference_service import obtenir_ou_generer_reference

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


def generer_pdf(db: Session, evaluation: EvaluationSlam, intervenant) -> bytes:
    """Export PDF (chapitre 14 du CDC, cas de test 12 ; FOR-SHEQ-004 « Fiche
    SLAM »). Reprend les 4 étapes et 16 points du référentiel réellement
    utilisé par l'application (app/models/slam_referentiel.py) — le formulaire
    papier original en compte davantage par étape (5/7/6/7, source
    FOR-SHEQ-004) mais l'application, depuis le prompt 2.2, s'appuie sur une
    version simplifiée à 4 points par étape ; l'export reflète fidèlement les
    données réellement saisies dans l'application, pas le formulaire papier
    intégral non repris jusqu'ici — écart déjà existant, pas introduit par cet
    export."""
    reference = obtenir_ou_generer_reference(db, evaluation, EvaluationSlam)
    pdf = DocumentPDF("FICHE SLAM – ÉVALUATION AVANT TRAVAUX EN HAUTEUR", reference)

    pdf.section(
        "Intervention",
        [
            ("Date et heure", evaluation.date.strftime("%d/%m/%Y %H:%M")),
            ("Intervenant", f"{intervenant.prenom} {intervenant.nom}"),
        ],
    )

    for etape, points_valides in zip(ETAPES_SLAM, evaluation.etapes_validees):
        pdf.tableau(
            f"{etape['lettre']} — {etape['titre']}",
            ["Point de contrôle", "Validé"],
            [[libelle, "Oui" if valide else "Non"] for libelle, valide in zip(etape["points"], points_valides)],
        )

    pdf.section(
        "Décision",
        [("Décision", evaluation.decision.value), ("Motif", evaluation.motif or "—")],
    )

    pdf.pied_de_page(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), f"{intervenant.prenom} {intervenant.nom}")
    return pdf.construire()
