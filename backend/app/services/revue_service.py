"""Logique métier du module Revues de direction (prompt 4.2, section 5.3.4 du
CDC, FOR-SHEQ-016)."""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cotation_risque import CotationRisque
from app.models.decision_revue import DecisionRevue
from app.models.enums import (
    StatutAction,
    StatutDecisionRevue,
    StatutInspection,
    StatutSeance,
    TypeSignalement,
)
from app.models.inspection import Inspection
from app.models.revue_direction import RevueDirection
from app.models.risque import Risque
from app.models.seance import Seance
from app.models.signalement import Signalement
from app.schemas.revue import DecisionCreation, RevueCreation
from app.services import action_service

_TYPES_ACCIDENT = (TypeSignalement.INCIDENT, TypeSignalement.ACCIDENT)


def _decisions_reportees(db: Session) -> list[dict]:
    """Règle 5.3.4 : "les décisions de revue non soldées sont automatiquement
    reportées en données d'entrée de la revue suivante" — reprend TOUTE
    décision encore ouverte, quelle que soit la revue d'origine, pas
    seulement celles de la revue immédiatement précédente (une décision peut
    rester ouverte sur plusieurs cycles)."""
    ouvertes = db.scalars(
        select(DecisionRevue).where(DecisionRevue.statut == StatutDecisionRevue.OUVERTE, DecisionRevue.archive.is_(False))
    )
    return [
        {
            "decision_id": d.id,
            "revue_origine_id": d.revue_id,
            "libelle": d.libelle,
            "responsable_id": d.responsable_id,
            "echeance": d.echeance.isoformat(),
        }
        for d in ouvertes
    ]


def _assembler_indicateurs(db: Session, periode_debut, periode_fin) -> dict:
    """Section 8 (bilan des indicateurs) de FOR-SHEQ-016, reconstituée avec les
    seules données réellement disponibles dans l'application à ce stade."""
    accidents_incidents = db.scalar(
        select(func.count())
        .select_from(Signalement)
        .where(
            Signalement.type.in_(_TYPES_ACCIDENT),
            Signalement.date_constat >= periode_debut,
            Signalement.date_constat <= periode_fin,
            Signalement.archive.is_(False),
        )
    )
    signalements_total = db.scalar(
        select(func.count())
        .select_from(Signalement)
        .where(
            Signalement.date_constat >= periode_debut,
            Signalement.date_constat <= periode_fin,
            Signalement.archive.is_(False),
        )
    )
    inspections_realisees = db.scalar(
        select(func.count())
        .select_from(Inspection)
        .where(
            Inspection.statut == StatutInspection.CLOTUREE,
            Inspection.date >= periode_debut,
            Inspection.date <= periode_fin,
            Inspection.archive.is_(False),
        )
    )
    # Note : le taux de conformité moyen des inspections n'est pas repris ici —
    # Inspection.taux_conformite est une propriété Python calculée à la volée
    # (prompt 2.4), pas une colonne, donc pas moyennable par une agrégation SQL
    # sans charger chaque inspection ; jugé disproportionné pour ce seul champ
    # du rapport, laissé de côté plutôt que fait au prix d'un N+1.

    risques_nouveaux = db.scalar(
        select(func.count())
        .select_from(Risque)
        .where(Risque.cree_le >= periode_debut, Risque.cree_le <= periode_fin, Risque.archive.is_(False))
    )
    reevaluations = db.scalar(
        select(func.count())
        .select_from(CotationRisque)
        .where(CotationRisque.date_evaluation >= periode_debut, CotationRisque.date_evaluation <= periode_fin)
    )
    seances_realisees = db.scalar(
        select(func.count())
        .select_from(Seance)
        .where(
            Seance.statut == StatutSeance.REALISEE,
            Seance.date >= periode_debut,
            Seance.date <= periode_fin,
            Seance.archive.is_(False),
        )
    )
    synthese_actions = action_service.calculer_synthese(db)

    return {
        "accidents_incidents": accidents_incidents,
        "signalements_total": signalements_total,
        "inspections_realisees": inspections_realisees,
        "risques_nouveaux": risques_nouveaux,
        "reevaluations_risques": reevaluations,
        "seances_realisees": seances_realisees,
        "avancement_plan_action": synthese_actions.model_dump(),
    }


def creer_revue(db: Session, donnees: RevueCreation, redacteur_id: int) -> RevueDirection:
    donnees_entree = {
        "indicateurs": _assembler_indicateurs(db, donnees.periode_debut, donnees.periode_fin),
        "decisions_reportees": _decisions_reportees(db),
    }
    revue = RevueDirection(
        date=donnees.date,
        lieu=donnees.lieu,
        redacteur_id=redacteur_id,
        periode_debut=donnees.periode_debut,
        periode_fin=donnees.periode_fin,
        participants=donnees.participants,
        donnees_entree=donnees_entree,
        cree_par_id=redacteur_id,
    )
    db.add(revue)
    db.commit()
    db.refresh(revue)
    return revue


def obtenir_revue(db: Session, revue_id: int) -> RevueDirection:
    revue = db.get(RevueDirection, revue_id)
    if revue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revue de direction introuvable")
    return revue


def decisions_de(db: Session, revue_id: int) -> list[DecisionRevue]:
    return list(db.scalars(select(DecisionRevue).where(DecisionRevue.revue_id == revue_id)))


def creer_decision(db: Session, revue: RevueDirection, donnees: DecisionCreation, cree_par_id: int) -> DecisionRevue:
    decision = DecisionRevue(
        revue_id=revue.id,
        libelle=donnees.libelle,
        responsable_id=donnees.responsable_id,
        echeance=donnees.echeance,
        statut=StatutDecisionRevue.OUVERTE,
        cree_par_id=cree_par_id,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


def obtenir_decision(db: Session, decision_id: int) -> DecisionRevue:
    decision = db.get(DecisionRevue, decision_id)
    if decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Décision introuvable")
    return decision


def solder_decision(db: Session, decision: DecisionRevue, modifie_par_id: int) -> DecisionRevue:
    if decision.statut == StatutDecisionRevue.SOLDEE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette décision est déjà soldée")
    decision.statut = StatutDecisionRevue.SOLDEE
    decision.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(decision)
    return decision
