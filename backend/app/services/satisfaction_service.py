"""Logique métier du module Satisfaction client (prompt 4.3, section 5.3.6 du
CDC, FOR-SHEQ-018)."""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enquete_satisfaction import EnqueteSatisfaction
from app.models.reponse_satisfaction import ReponseSatisfaction
from app.schemas.satisfaction import EnqueteCreation, ReponseEntree
from app.services.notification_service import notifier_satisfaction_faible

# Six critères réels de FOR-SHEQ-018, repris tels quels — le CDC ne les
# déclare pas "paramétrables" (à la différence du quiz de sensibilisation ou
# du référentiel de checklists), traités comme une constante Python plutôt
# qu'une table de référence supplémentaire hors dictionnaire.
CRITERES = [
    "Qualité de l'installation / de la prestation",
    "Respect des délais annoncés",
    "Propreté et sécurité du chantier (balisage, rangement)",
    "Comportement et professionnalisme des techniciens",
    "Clarté des explications et de la documentation remise",
    "Fonctionnement de la solution après intervention",
]

# Règle 5.3.6 : "toute note inférieure ou égale à deux sur cinq déclenche une
# notification et l'ouverture d'une analyse".
SEUIL_ALERTE_NOTE = 2


def creer_enquete(db: Session, donnees: EnqueteCreation, cree_par_id: int) -> EnqueteSatisfaction:
    enquete = EnqueteSatisfaction(
        client=donnees.client,
        site_id=donnees.site_id,
        intervention=donnees.intervention,
        technicien_id=donnees.technicien_id,
        envoyee_le=datetime.now(timezone.utc),
        cree_par_id=cree_par_id,
    )
    db.add(enquete)
    db.commit()
    db.refresh(enquete)
    return enquete


def obtenir_par_jeton(db: Session, jeton: str) -> EnqueteSatisfaction:
    """404 générique que le jeton soit invalide ou déjà utilisé — ne jamais
    distinguer les deux cas à un appelant non authentifié (surface d'attaque
    minimale sur une route publique, point 10 de CLAUDE.md : valider tout
    côté serveur, ne rien présumer d'un client anonyme)."""
    enquete = db.scalar(select(EnqueteSatisfaction).where(EnqueteSatisfaction.jeton == jeton))
    if enquete is None or enquete.repondu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire introuvable ou déjà rempli")
    return enquete


def repondre(db: Session, enquete: EnqueteSatisfaction, donnees: ReponseEntree) -> ReponseSatisfaction:
    criteres_recus = {n.critere for n in donnees.notes}
    if criteres_recus != set(CRITERES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le questionnaire doit être répondu intégralement, un critère ne peut être omis ni ajouté",
        )

    necessite_analyse = any(n.note <= SEUIL_ALERTE_NOTE for n in donnees.notes)

    reponse = ReponseSatisfaction(
        enquete_id=enquete.id,
        notes=[n.model_dump() for n in donnees.notes],
        recommandation=donnees.recommandation,
        remarques=donnees.remarques,
        necessite_analyse=necessite_analyse,
        date_reponse=datetime.now(timezone.utc),
    )
    enquete.repondu = True
    db.add(reponse)
    db.commit()
    db.refresh(reponse)

    # Tableau 3, chapitre 6.3 — prompt 4.4 : "Note de satisfaction faible" (à
    # exécuter après le commit, l'id de la réponse doit exister pour la
    # rattacher à la notification).
    if necessite_analyse:
        notifier_satisfaction_faible(db, reponse)

    return reponse


def lister_enquetes(db: Session) -> list[EnqueteSatisfaction]:
    return list(db.scalars(select(EnqueteSatisfaction).order_by(EnqueteSatisfaction.envoyee_le.desc())))


def reponses_a_traiter(db: Session) -> list[ReponseSatisfaction]:
    return list(
        db.scalars(
            select(ReponseSatisfaction)
            .where(ReponseSatisfaction.necessite_analyse.is_(True))
            .order_by(ReponseSatisfaction.date_reponse.desc())
        )
    )


def obtenir_reponse(db: Session, reponse_id: int) -> ReponseSatisfaction:
    reponse = db.get(ReponseSatisfaction, reponse_id)
    if reponse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réponse introuvable")
    return reponse
