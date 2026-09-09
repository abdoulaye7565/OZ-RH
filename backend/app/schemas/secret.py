"""Schémas Pydantic du module Coffre-fort (CDC section 5.2.4).

Distinction volontaire entre deux schémas de sortie : `SecretSortie` (liste,
fiche) ne porte jamais la valeur déchiffrée — seulement ses métadonnées,
conformément à "masqué par défaut" (5.2.4). Seule `SecretConsultationSortie`
(renvoyée par la route de consultation, qui écrit dans le journal des accès)
porte la valeur en clair — jamais mise en cache, jamais renvoyée par une
autre route.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import ActionJournal, RoleUtilisateur, TypeAcces

# Le CDC (5.2.4) ne mentionne le coffre-fort que pour technicien ("limité"),
# responsable ("lecture · création") et administrateur ("tout") ; le référent
# SHEQ en est explicitement exclu ("sa fonction ne le justifie pas") et le
# collaborateur n'y figure pas du tout. `role_requis` ne peut donc désigner
# que l'un des trois rôles réellement concernés par ce module — accepter
# n'importe quel RoleUtilisateur ici créerait des secrets structurellement
# invisibles de tous (voir NIVEAU_ROLE_SECRET, secret_service.py).
ROLES_SECRET_VALIDES = {RoleUtilisateur.TECHNICIEN, RoleUtilisateur.RESPONSABLE, RoleUtilisateur.ADMINISTRATEUR}


class SecretCreation(BaseModel):
    libelle: str
    equipement_id: int | None = None
    type_acces: TypeAcces
    identifiant: str | None = None
    valeur: str  # en clair à l'entrée seule ; jamais journalisé, jamais renvoyé tel quel
    role_requis: RoleUtilisateur = RoleUtilisateur.RESPONSABLE

    @field_validator("role_requis")
    @classmethod
    def _role_requis_valide(cls, v: RoleUtilisateur) -> RoleUtilisateur:
        if v not in ROLES_SECRET_VALIDES:
            raise ValueError(
                "role_requis doit être technicien, responsable ou administrateur "
                "(le référent SHEQ et le collaborateur n'ont jamais accès au coffre-fort)"
            )
        return v

    @field_validator("valeur")
    @classmethod
    def _valeur_non_vide(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La valeur du secret ne peut pas être vide")
        return v


class SecretModification(BaseModel):
    """Une vraie modification en place, à la différence de CONFIGURATION
    (immuable, une correction crée une nouvelle fiche) : un secret représente
    l'état ACTUEL d'un mot de passe, pas un historique à conserver — le CDC
    liste "modification" comme fonctionnalité à part entière, pas comme une
    nouvelle version. Tous les champs optionnels : seuls les champs fournis
    changent."""

    libelle: str | None = None
    equipement_id: int | None = None
    type_acces: TypeAcces | None = None
    identifiant: str | None = None
    valeur: str | None = None
    role_requis: RoleUtilisateur | None = None

    @field_validator("role_requis")
    @classmethod
    def _role_requis_valide(cls, v: RoleUtilisateur | None) -> RoleUtilisateur | None:
        if v is not None and v not in ROLES_SECRET_VALIDES:
            raise ValueError("role_requis doit être technicien, responsable ou administrateur")
        return v


class SecretSortie(BaseModel):
    """Jamais la valeur déchiffrée — voir le docstring du module."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str
    equipement_id: int | None
    type_acces: TypeAcces
    identifiant: str | None
    role_requis: RoleUtilisateur
    archive: bool
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None


class SecretConsultationSortie(BaseModel):
    """Renvoyée uniquement par POST /secrets/{id}/consulter — chaque appel
    écrit une ligne dans le journal des accès avant de renvoyer la valeur."""

    id: int
    libelle: str
    valeur: str


class GenerationMotDePasseEntree(BaseModel):
    longueur: int = 20
    inclure_symboles: bool = True

    @field_validator("longueur")
    @classmethod
    def _longueur_raisonnable(cls, v: int) -> int:
        if not (12 <= v <= 128):
            raise ValueError("La longueur doit être comprise entre 12 et 128 caractères")
        return v


class GenerationMotDePasseSortie(BaseModel):
    mot_de_passe: str


class EntreeJournalAccesSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    secret_id: int
    utilisateur_id: int
    horodatage: datetime
    action: ActionJournal
