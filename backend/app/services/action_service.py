"""Logique métier du module Actions (prompt 1.2, section 5.2.5 du CDC)."""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action import Action
from app.models.enums import StatutAction
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


def mettre_a_jour_avancement(db: Session, action: Action, avancement: int, indicateur: str | None) -> Action:
    if not 0 <= avancement <= 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'avancement doit être compris entre 0 et 100")
    action.avancement = avancement
    if indicateur is not None:
        action.indicateur = indicateur
    db.commit()
    db.refresh(action)
    return action


def changer_statut(db: Session, action: Action, nouveau_statut: StatutAction) -> Action:
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
    db.commit()
    db.refresh(action)
    return action


def calculer_synthese(db: Session) -> SyntheseActions:
    actions = list(db.scalars(select(Action).where(Action.archive.is_(False))))

    par_statut = {s.value: 0 for s in StatutAction}
    for a in actions:
        par_statut[a.statut.value] += 1

    total = len(actions)
    nombre_cloturees = par_statut[StatutAction.CLOTUREE.value]
    # Formule du chapitre 7.3.2 du CDC : actions clôturées / total, PAS la moyenne
    # des avancements individuels.
    taux = (nombre_cloturees / total) if total else 0.0

    nombre_en_retard = sum(1 for a in actions if a.en_retard)

    return SyntheseActions(par_statut=par_statut, nombre_en_retard=nombre_en_retard, taux_avancement_global=taux)
