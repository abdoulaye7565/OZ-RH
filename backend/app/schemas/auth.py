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


class UtilisateurModification(BaseModel):
    """Modification du profil d'un compte existant (2026-09-09). `identifiant`
    et `mot_de_passe` volontairement absents — compromis assumé : le premier
    sert de clé de connexion et de repère dans tout l'historique/les journaux,
    le changer mériterait son propre flux dédié (pas un champ parmi d'autres) ;
    le second est sensible par nature (réinitialisation de mot de passe), à
    traiter séparément plutôt que noyé dans une modification de profil
    générale. Tous les champs optionnels : seuls ceux réellement envoyés sont
    appliqués (`exclude_unset`, service auth_service.modifier_utilisateur) —
    permet d'effacer intentionnellement `site_id`/`courriel` (envoyé à `null`)
    sans confondre ce cas avec "champ non fourni, à laisser tel quel"."""

    nom: str | None = None
    prenom: str | None = None
    role: RoleUtilisateur | None = None
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
    # Chemin relatif de la photo de profil (2026-09-10) — jamais l'URL
    # complète : le front construit l'appel authentifié
    # GET /auth/utilisateurs/{id}/photo, comme pour les autres pièces
    # jointes de l'app. None si l'utilisateur n'en a pas déposé.
    photo: str | None = None
    actif: bool
    derniere_connexion: datetime | None = None
