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
from app.services.auth_service import activer_utilisateur, authentifier, creer_utilisateur, desactiver_utilisateur

logger = logging.getLogger("app.securite")

router = APIRouter(prefix="/auth", tags=["authentification"])


@router.post("/connexion", response_model=JetonSortie)
def connexion(payload: ConnexionEntree, db: Session = Depends(get_db)) -> JetonSortie:
    """Authentifie un utilisateur par identifiant et mot de passe, et renvoie un
    couple access_token / refresh_token JWT."""
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
    """Renouvelle l'access token à partir d'un refresh token valide, sans nouvelle
    saisie du mot de passe."""
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
    """Crée un compte utilisateur. Réservé aux administrateurs."""
    existe = db.scalar(select(Utilisateur).where(Utilisateur.identifiant == payload.identifiant))
    if existe is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet identifiant est déjà utilisé")
    return creer_utilisateur(db, payload, createur)


@router.get("/moi", response_model=UtilisateurSortie)
def moi(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    """Renvoie le profil de l'utilisateur actuellement authentifié."""
    return utilisateur


@router.get("/utilisateurs", response_model=list[UtilisateurSortie])
def lister_utilisateurs_route(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[Utilisateur]:
    """Liste les comptes non archivés (actifs et désactivés confondus — le
    champ `actif` distingue les deux) — sert à résoudre un identifiant
    (porteur d'EPI, responsable d'action, animateur de formation...) en nom
    affichable côté écran ; ouvert à tout utilisateur authentifié, ces
    informations étant déjà visibles de tous dans l'organisation papier."""
    return list(db.scalars(select(Utilisateur).where(Utilisateur.archive.is_(False)).order_by(Utilisateur.nom)))


def _recuperer_utilisateur(db: Session, utilisateur_id: int) -> Utilisateur:
    cible = db.get(Utilisateur, utilisateur_id)
    if cible is None or cible.archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    return cible


@router.post("/utilisateurs/{utilisateur_id}/desactiver", response_model=UtilisateurSortie)
def desactiver_utilisateur_route(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_role(*Permissions.GERER_UTILISATEURS)),
) -> Utilisateur:
    """Désactive un compte (jamais de suppression physique, point 2 de
    CLAUDE.md) : un compte désactivé ne peut plus se connecter, mais reste
    visible partout où il est déjà référencé."""
    cible = _recuperer_utilisateur(db, utilisateur_id)
    try:
        return desactiver_utilisateur(db, cible, admin)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/utilisateurs/{utilisateur_id}/activer", response_model=UtilisateurSortie)
def activer_utilisateur_route(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_role(*Permissions.GERER_UTILISATEURS)),
) -> Utilisateur:
    """Réactive un compte précédemment désactivé."""
    cible = _recuperer_utilisateur(db, utilisateur_id)
    return activer_utilisateur(db, cible, admin)
