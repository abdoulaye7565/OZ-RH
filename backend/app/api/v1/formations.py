"""Routes du module Formations (prompt 4.2, section 5.3.3 du CDC)."""
from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.competence import Competence
from app.models.enums import RoleUtilisateur
from app.models.question_quiz import QuestionQuiz
from app.models.seance import Seance
from app.models.utilisateur import Utilisateur
from app.schemas.formation import (
    AlerteRecyclageSortie,
    CompetenceCreation,
    CompetenceSortie,
    DetailReponseSortie,
    EmargementEntree,
    EmargementSortie,
    HabilitationCreation,
    HabilitationSortie,
    QuestionQuizAdminSortie,
    QuestionQuizCreation,
    QuestionQuizSortie,
    SeanceCreation,
    SeanceSortie,
    TentativeQuizEntree,
    TentativeQuizSortie,
)
from app.services.formation_service import (
    alertes_recyclage,
    cloturer_seance,
    creer_competence,
    creer_habilitation,
    creer_question,
    creer_seance,
    emarger,
    lister_competences,
    lister_questions,
    lister_seances,
    matrice_competences,
    obtenir_seance,
    passer_quiz,
)

router = APIRouter(prefix="/formations", tags=["formations"])

# Rôles ayant une vue d'ensemble (matrice complète, alertes) : "direction" du
# CDC rapprochée de RESPONSABLE/ADMINISTRATEUR, plus le référent SHEQ qui gère
# le module — voir Permissions.GERER_FORMATIONS pour le même rapprochement.
ROLES_VUE_ENSEMBLE = (*Permissions.GERER_FORMATIONS, RoleUtilisateur.RESPONSABLE)


def _recuperer_seance(db: Session, seance_id: int) -> Seance:
    return obtenir_seance(db, seance_id)


@router.post("/competences", response_model=CompetenceSortie, status_code=status.HTTP_201_CREATED)
def creer_competence_route(
    payload: CompetenceCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_FORMATIONS)),
) -> Competence:
    return creer_competence(db, payload, cree_par_id=utilisateur.id)


@router.get("/competences", response_model=list[CompetenceSortie])
def lister_competences_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Competence]:
    return lister_competences(db)


@router.post("/habilitations", response_model=HabilitationSortie, status_code=status.HTTP_201_CREATED)
def creer_habilitation_route(
    payload: HabilitationCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_FORMATIONS)),
):
    return creer_habilitation(db, payload, cree_par_id=utilisateur.id)


@router.get("/matrice", response_model=list[HabilitationSortie])
def matrice_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*ROLES_VUE_ENSEMBLE)),
):
    return matrice_competences(db)


@router.get("/mes-habilitations", response_model=list[HabilitationSortie])
def mes_habilitations_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
):
    # Section 5.3.3, Acteurs : "chaque collaborateur pour ses propres
    # compétences" — ouvert à tous, restreint à ses propres lignes.
    return matrice_competences(db, utilisateur_id=utilisateur.id)


@router.get("/alertes-recyclage", response_model=list[AlerteRecyclageSortie])
def alertes_recyclage_route(
    horizon_jours: int = 30,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*ROLES_VUE_ENSEMBLE)),
):
    habilitations = alertes_recyclage(db, horizon_jours)
    competences = {c.id: c for c in lister_competences(db)}
    return [
        AlerteRecyclageSortie(
            habilitation_id=h.id,
            utilisateur_id=h.utilisateur_id,
            competence_id=h.competence_id,
            libelle_competence=competences[h.competence_id].libelle if h.competence_id in competences else "?",
            date_expiration=h.date_expiration,
            jours_restants=(h.date_expiration - date.today()).days,
            due=True,
        )
        for h in habilitations
    ]


@router.post("/seances", response_model=SeanceSortie, status_code=status.HTTP_201_CREATED)
def creer_seance_route(
    payload: SeanceCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_FORMATIONS)),
) -> Seance:
    return creer_seance(db, payload, cree_par_id=utilisateur.id)


@router.get("/seances", response_model=list[SeanceSortie])
def lister_seances_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Seance]:
    return lister_seances(db)


@router.get("/seances/{seance_id}", response_model=SeanceSortie)
def lire_seance_route(
    seance_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Seance:
    return _recuperer_seance(db, seance_id)


@router.post("/seances/{seance_id}/emargement", response_model=EmargementSortie)
def emarger_route(
    seance_id: int,
    payload: EmargementEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_FORMATIONS)),
):
    seance = _recuperer_seance(db, seance_id)
    return emarger(db, seance, payload, cree_par_id=utilisateur.id)


@router.post("/seances/{seance_id}/cloturer", response_model=SeanceSortie)
def cloturer_seance_route(
    seance_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_FORMATIONS)),
) -> Seance:
    seance = _recuperer_seance(db, seance_id)
    return cloturer_seance(db, seance, modifie_par_id=utilisateur.id)


@router.post("/questions-quiz", response_model=QuestionQuizAdminSortie, status_code=status.HTTP_201_CREATED)
def creer_question_route(
    payload: QuestionQuizCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_FORMATIONS)),
) -> QuestionQuiz:
    return creer_question(
        db,
        enonce=payload.enonce,
        choix=[c.model_dump() for c in payload.choix],
        reponse_correcte=payload.reponse_correcte,
        cree_par_id=utilisateur.id,
    )


@router.get("/questions-quiz", response_model=list[QuestionQuizSortie])
def lister_questions_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[QuestionQuiz]:
    # Jamais reponse_correcte ici (QuestionQuizSortie ne l'expose pas) : c'est
    # l'écran que voit le participant avant de répondre.
    return lister_questions(db)


@router.post("/seances/{seance_id}/quiz", response_model=TentativeQuizSortie)
def passer_quiz_route(
    seance_id: int,
    payload: TentativeQuizEntree,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
):
    seance = _recuperer_seance(db, seance_id)
    tentative, details = passer_quiz(db, seance, payload, participant_id=utilisateur.id)
    sortie = TentativeQuizSortie.model_validate(tentative)
    sortie.details = [DetailReponseSortie(**d) for d in details]
    return sortie
