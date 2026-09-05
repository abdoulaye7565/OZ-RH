"""Dépendances FastAPI transversales : identification du compte courant et
contrôle de rôle. Toute route protégée doit passer par `get_current_user` ou
`require_role`, jamais par une vérification de jeton ad hoc."""
from collections.abc import Sequence

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decoder_jeton
from app.db.session import get_db
from app.models.enums import RoleUtilisateur
from app.models.utilisateur import Utilisateur

# tokenUrl sert uniquement à documenter le schéma de sécurité dans OpenAPI ; la
# route /auth/connexion accepte un corps JSON (voir schemas/auth.py), pas le
# formulaire OAuth2 standard — le bouton "Authorize" de Swagger ne fonctionnera
# donc pas tel quel. Compromis assumé : voir docs/JOURNAL.md, prompt 0.3.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/connexion")


def get_current_user(jeton: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Utilisateur:
    exception_identifiants = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou expirés",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decoder_jeton(jeton)
    except jwt.InvalidTokenError as exc:
        raise exception_identifiants from exc

    if payload.get("type") != "access":
        raise exception_identifiants

    try:
        utilisateur_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise exception_identifiants from exc

    utilisateur = db.get(Utilisateur, utilisateur_id)
    if utilisateur is None or utilisateur.archive or not utilisateur.actif:
        raise exception_identifiants

    return utilisateur


def require_role(*roles: RoleUtilisateur | Sequence[RoleUtilisateur]):
    # Permet aussi bien require_role(Permissions.X) (un tuple) que
    # require_role(RoleUtilisateur.ADMINISTRATEUR, RoleUtilisateur.RESPONSABLE).
    roles_autorises: set[RoleUtilisateur] = set()
    for r in roles:
        if isinstance(r, RoleUtilisateur):
            roles_autorises.add(r)
        else:
            roles_autorises.update(r)

    def _dependency(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if utilisateur.role not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : rôle insuffisant pour cette action",
            )
        return utilisateur

    return _dependency
