"""Hachage des mots de passe (argon2) et émission/vérification des jetons JWT.

Deux jetons distincts sont émis à la connexion — voir l'explication donnée à
l'utilisateur en fin de prompt 0.3, résumée ici : l'access token est court et
voyage à chaque requête (risque d'exposition plus élevé, donc durée de vie
courte) ; le refresh token est long mais ne sert qu'à en émettre un nouveau,
avec un usage bien plus rare.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return _pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, empreinte: str) -> bool:
    return _pwd_context.verify(mot_de_passe, empreinte)


def _creer_jeton(sub: str, type_jeton: str, duree: timedelta, extra: dict[str, Any] | None = None) -> str:
    maintenant = datetime.now(timezone.utc)
    payload: dict[str, Any] = {"sub": sub, "type": type_jeton, "iat": maintenant, "exp": maintenant + duree}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def creer_access_token(utilisateur_id: int, role: str) -> str:
    duree = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return _creer_jeton(str(utilisateur_id), "access", duree, {"role": role})


def creer_refresh_token(utilisateur_id: int) -> str:
    duree = timedelta(days=settings.jwt_refresh_token_expire_days)
    return _creer_jeton(str(utilisateur_id), "refresh", duree)


def decoder_jeton(jeton: str) -> dict[str, Any]:
    """Lève jwt.InvalidTokenError (ou une sous-classe, dont ExpiredSignatureError)
    si le jeton est invalide, expiré, ou signé avec une autre clé."""
    return jwt.decode(jeton, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
