"""Routes d'authentification (prompt 0.3)."""
import logging
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.core.security import creer_access_token, creer_refresh_token, decoder_jeton
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.auth import (
    AccesSortie,
    ConnexionEntree,
    JetonSortie,
    RafraichissementEntree,
    UtilisateurCreation,
    UtilisateurSortie,
)
from app.services.auth_service import authentifier, creer_utilisateur

logger = logging.getLogger("app.securite")

router = APIRouter(prefix="/auth", tags=["authentification"])


@router.post("/connexion", response_model=JetonSortie)
def connexion(payload: ConnexionEntree, db: Session = Depends(get_db)) -> JetonSortie:
    utilisateur = authentifier(db, payload.identifiant, payload.mot_de_passe)
    if utilisateur is None:
        logger.warning("Échec de connexion pour l'identifiant %s", payload.identifiant)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiant ou mot de passe incorrect")

    utilisateur.derniere_connexion = datetime.now(timezone.utc)
    db.commit()

    logger.info(
        "Connexion réussie : %s (id=%s, rôle=%s)", utilisateur.identifiant, utilisateur.id, utilisateur.role.value
    )

    return JetonSortie(
        access_token=creer_access_token(utilisateur.id, utilisateur.role.value),
        refresh_token=creer_refresh_token(utilisateur.id),
    )


@router.post("/rafraichissement", response_model=AccesSortie)
def rafraichissement(payload: RafraichissementEntree, db: Session = Depends(get_db)) -> AccesSortie:
    exception_jeton = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton de rafraîchissement invalide ou expiré"
    )
    try:
        contenu = decoder_jeton(payload.refresh_token)
    except jwt.InvalidTokenError as exc:
        raise exception_jeton from exc

    if contenu.get("type") != "refresh":
        raise exception_jeton

    try:
        utilisateur_id = int(contenu["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise exception_jeton from exc

    utilisateur = db.get(Utilisateur, utilisateur_id)
    if utilisateur is None or utilisateur.archive or not utilisateur.actif:
        raise exception_jeton

    return AccesSortie(access_token=creer_access_token(utilisateur.id, utilisateur.role.value))


@router.post(
    "/utilisateurs",
    response_model=UtilisateurSortie,
    status_code=status.HTTP_201_CREATED,
)
def creer_utilisateur_route(
    payload: UtilisateurCreation,
    db: Session = Depends(get_db),
    createur: Utilisateur = Depends(require_role(*Permissions.GERER_UTILISATEURS)),
) -> Utilisateur:
    existe = db.scalar(select(Utilisateur).where(Utilisateur.identifiant == payload.identifiant))
    if existe is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet identifiant est déjà utilisé")
    return creer_utilisateur(db, payload, createur)


@router.get("/moi", response_model=UtilisateurSortie)
def moi(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    return utilisateur
