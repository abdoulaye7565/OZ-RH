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
    lister_reponses,
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
    """Crée une enquête de satisfaction et génère le jeton public à envoyer au
    client pour accéder au questionnaire."""
    return creer_enquete(db, payload, cree_par_id=utilisateur.id)


@router.get("/enquetes", response_model=list[EnqueteSortie])
def lister_enquetes_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> list[EnqueteSatisfaction]:
    """Liste les enquêtes de satisfaction envoyées."""
    return lister_enquetes(db)


@router.get("/a-traiter", response_model=list[ReponseSortie])
def reponses_a_traiter_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> list[ReponseSatisfaction]:
    """Liste les réponses de satisfaction reçues qui restent à traiter."""
    return reponses_a_traiter(db)


@router.get("/reponses", response_model=list[ReponseSortie])
def lister_reponses_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> list[ReponseSatisfaction]:
    """Liste toutes les réponses reçues (pas seulement celles à traiter) —
    sert au calcul de la moyenne de satisfaction sur l'écran de pilotage."""
    return lister_reponses(db)


@router.get("/reponses/{reponse_id}", response_model=ReponseSortie)
def lire_reponse_route(
    reponse_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.TRAITER_SATISFACTION)),
) -> ReponseSatisfaction:
    """Récupère une réponse de satisfaction par son identifiant."""
    return obtenir_reponse(db, reponse_id)


@router.get("/questionnaire/{jeton}", response_model=QuestionnaireSortie)
def lire_questionnaire_route(jeton: str, db: Session = Depends(get_db)) -> dict:
    """Récupère le contenu d'un questionnaire de satisfaction via son jeton.
    Route volontairement publique (sans authentification) : le client externe y
    accède par lien, sans compte — le jeton est la seule protection."""
    enquete = obtenir_par_jeton(db, jeton)
    return {"client": enquete.client, "intervention": enquete.intervention, "criteres": CRITERES}


@router.post("/questionnaire/{jeton}", response_model=ReponseSortie, status_code=status.HTTP_201_CREATED)
def repondre_route(jeton: str, payload: ReponseEntree, db: Session = Depends(get_db)) -> ReponseSatisfaction:
    """Enregistre la réponse du client au questionnaire. Route publique elle
    aussi : toute entrée est validée côté serveur sans confiance dans
    l'appelant."""
    enquete = obtenir_par_jeton(db, jeton)
    return repondre(db, enquete, payload)
