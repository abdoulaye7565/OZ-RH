"""Schémas Pydantic de l'authentification.

Champs nommés en français (identifiant/mot_de_passe), pas au format du formulaire
OAuth2 standard (username/password) : cohérent avec le reste de l'API et avec le
dictionnaire de données (chapitre 7.2.1), au prix de l'auto-complétion du bouton
"Authorize" de Swagger — voir la note dans core/deps.py."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import RoleUtilisateur


class ConnexionEntree(BaseModel):
    identifiant: str
    mot_de_passe: str


class JetonSortie(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RafraichissementEntree(BaseModel):
    refresh_token: str


class AccesSortie(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UtilisateurCreation(BaseModel):
    nom: str
    prenom: str
    identifiant: str
    mot_de_passe: str
    role: RoleUtilisateur
    site_id: int | None = None
    courriel: str | None = None


class UtilisateurSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    identifiant: str
    role: RoleUtilisateur
    site_id: int | None
    courriel: str | None
    actif: bool
    derniere_connexion: datetime | None = None
