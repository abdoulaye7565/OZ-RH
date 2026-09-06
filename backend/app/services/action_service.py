"""Logique métier du module Actions (prompt 1.2, section 5.2.5 du CDC)."""
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.action import Action
from app.models.enums import StatutAction
from app.models.signalement import Signalement
from app.schemas.action import ActionCreation, SyntheseActions

# OUVERTE -> CLOTUREE directement est autorisé (une action rapide n'a pas besoin
# de transiter par EN_COURS) ; aucun retour en arrière possible.
TRANSITIONS_AUTORISEES: dict[StatutAction, set[StatutAction]] = {
    StatutAction.OUVERTE: {StatutAction.EN_COURS, StatutAction.CLOTUREE},
    StatutAction.EN_COURS: {StatutAction.CLOTUREE},
    StatutAction.CLOTUREE: set(),
}


def creer_action(db: Session, donnees: ActionCreation, cree_par_id: int) -> Action:
    action = Action(
        libelle=donnees.libelle,
        risque_id=donnees.risque_id,
        signalement_id=donnees.signalement_id,
        inspection_id=donnees.inspection_id,
        cotation_audit_id=donnees.cotation_audit_id,
        reponse_satisfaction_id=donnees.reponse_satisfaction_id,
        type_mesure=donnees.type_mesure,
        responsable_id=donnees.responsable_id,
        echeance=donnees.echeance,
        avancement=0,
        statut=StatutAction.OUVERTE,
        cree_par_id=cree_par_id,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def mettre_a_jour_avancement(
    db: Session, action: Action, avancement: int, indicateur: str | None, modifie_par_id: int
) -> Action:
    if not 0 <= avancement <= 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'avancement doit être compris entre 0 et 100")
    action.avancement = avancement
    if indicateur is not None:
        action.indicateur = indicateur
    action.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(action)
    return action


def changer_statut(db: Session, action: Action, nouveau_statut: StatutAction, modifie_par_id: int) -> Action:
    autorises = TRANSITIONS_AUTORISEES[action.statut]
    if nouveau_statut not in autorises:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Transition invalide : impossible de passer de « {action.statut.value} » "
                f"à « {nouveau_statut.value} »"
            ),
        )
    if nouveau_statut == StatutAction.CLOTUREE and not action.indicateur:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de clôturer une action sans indicateur de réalisation renseigné",
        )
    action.statut = nouveau_statut
    action.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(action)
    return action


def calculer_synthese(db: Session, site_id: int | None = None) -> SyntheseActions:
    """Agrégations SQL (GROUP BY / COUNT), pas de chargement de toutes les lignes
    en mémoire Python — revu au prompt 1.5 ("attention aux performances").

    `site_id` : filtre optionnel, ajouté pour le tableau de bord (prompt 1.5).
    ACTION n'a pas de site propre ; seules les actions issues d'un signalement
    peuvent être rattachées à un site (via une jointure). Les actions issues
    d'un risque ou d'une inspection ne sont donc jamais comptées quand ce
    filtre est actif — RISQUE et INSPECTION n'ont pas non plus de site direct
    dans le modèle. Limite assumée, à signaler.
    """

    def _filtrer_par_site(requete):
        if site_id is None:
            return requete
        return requete.join(Signalement, Action.signalement_id == Signalement.id).where(
            Signalement.site_id == site_id
        )

    requete_par_statut = _filtrer_par_site(
        select(Action.statut, func.count().label("nombre")).where(Action.archive.is_(False))
    ).group_by(Action.statut)

    par_statut = {s.value: 0 for s in StatutAction}
    for statut, nombre in db.execute(requete_par_statut):
        par_statut[statut.value] = nombre

    total = sum(par_statut.values())
    nombre_cloturees = par_statut[StatutAction.CLOTUREE.value]
    # Formule du chapitre 7.3.2 du CDC : actions clôturées / total, PAS la moyenne
    # des avancements individuels.
    taux = (nombre_cloturees / total) if total else 0.0

    requete_en_retard = _filtrer_par_site(
        select(func.count()).select_from(Action).where(
            Action.archive.is_(False),
            Action.statut != StatutAction.CLOTUREE,
            Action.echeance < date.today(),
        )
    )
    nombre_en_retard = db.scalar(requete_en_retard)

    return SyntheseActions(par_statut=par_statut, nombre_en_retard=nombre_en_retard, taux_avancement_global=taux)


def echeances_proches(db: Session, horizon_jours: int = 30, site_id: int | None = None, limite: int = 10) -> list[Action]:
    """Actions non clôturées dont l'échéance tombe entre aujourd'hui et
    `horizon_jours` — utilisé par le tableau de bord (prompt 1.5)."""
    requete = select(Action).where(
        Action.archive.is_(False),
        Action.statut != StatutAction.CLOTUREE,
        Action.echeance <= date.today() + timedelta(days=horizon_jours),
    )
    if site_id is not None:
        requete = requete.join(Signalement, Action.signalement_id == Signalement.id).where(
            Signalement.site_id == site_id
        )
    requete = requete.order_by(Action.echeance.asc()).limit(limite)
    return list(db.scalars(requete))
