"""Routes du module Satisfaction client (prompt 4.3, section 5.3.6 du CDC).

Les deux routes `/questionnaire/{jeton}` sont volontairement PUBLIQUES (aucune
dépendance `get_current_user`) : section 5.3.6, "envoi par lien public sans
compte". Le jeton (secrets.token_urlsafe, voir app/models/enquete_satisfaction.py)
est la seule protection — toute entrée y est validée côté serveur sans aucune
confiance dans l'appelant (point 10, CLAUDE.md)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.enquete_satisfaction import EnqueteSatisfaction
from app.models.reponse_satisfaction import ReponseSatisfaction
from app.models.utilisateur import Utilisateur
from app.schemas.satisfaction import (
    EnqueteCreation,
    EnqueteSortie,
    QuestionnaireSortie,
    ReponseEntree,
    ReponseSortie,
)
from app.services.satisfaction_service import (
    CRITERES,
    creer_enquete,
    lister_enquetes,
    obtenir_par_jeton,
    obtenir_reponse,
    repondre,
    reponses_a_traiter,
)

router = APIRouter(prefix="/satisfaction", tags=["satisfaction"])


@router.post("/enquetes", response_model=EnqueteSortie, status_code=status.HTTP_201_CREATED)
def creer_enquete_route(
    payload: EnqueteCreation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.ENVOYER_ENQUETE_SATISFACTION)),
) -> EnqueteSatisfaction:
    return creer_enquete(db, payload, cree_par_id=utilisateur.id)


@router.get("/enquetes", response_model=list[EnqueteSortie])
def lister_enquetes_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> list[EnqueteSatisfaction]:
    return lister_enquetes(db)


@router.get("/a-traiter", response_model=list[ReponseSortie])
def reponses_a_traiter_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> list[ReponseSatisfaction]:
    return reponses_a_traiter(db)


@router.get("/reponses/{reponse_id}", response_model=ReponseSortie)
def lire_reponse_route(
    reponse_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> ReponseSatisfaction:
    return obtenir_reponse(db, reponse_id)


@router.get("/questionnaire/{jeton}", response_model=QuestionnaireSortie)
def lire_questionnaire_route(jeton: str, db: Session = Depends(get_db)) -> dict:
    enquete = obtenir_par_jeton(db, jeton)
    return {"client": enquete.client, "intervention": enquete.intervention, "criteres": CRITERES}


@router.post("/questionnaire/{jeton}", response_model=ReponseSortie, status_code=status.HTTP_201_CREATED)
def repondre_route(jeton: str, payload: ReponseEntree, db: Session = Depends(get_db)) -> ReponseSatisfaction:
    enquete = obtenir_par_jeton(db, jeton)
    return repondre(db, enquete, payload)
