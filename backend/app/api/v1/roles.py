"""Rôles et permissions réelles (revue d'ensemble 2026-09-10 — retour direct
de l'utilisateur : « je ne vois pas la gestion des rôles »).

La matrice existait déjà dans `app/core/permissions.py` (son en-tête dit
littéralement : « utile par exemple pour un futur écran "gestion des
rôles" » — jamais construit jusqu'ici) mais n'était exposée par aucune
route : l'écran Utilisateurs affichait une copie statique et peu détaillée
du tableau CLAUDE.md §6 (5 lignes, une par rôle), pas les permissions
RÉELLEMENT vérifiées par les routes (`Depends(require_role(*Permissions.X))`,
~20 permissions). Ce endpoint lit `Permissions` par introspection : toute
permission ajoutée au fil d'un futur module apparaît automatiquement ici,
sans double maintenance ni risque de désynchronisation avec le code qui
l'applique réellement.

Lecture seule, même logique que Paramètres : les rôles sont un ensemble
fermé de 5 valeurs (CLAUDE.md §6) et les permissions sont du code, pas des
données de configuration — les rendre éditables en base serait un
changement d'architecture (RBAC dynamique), pas un correctif d'affichage."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.permissions import PERIMETRE_PAR_ROLE, Permissions
from app.models.enums import RoleUtilisateur
from app.models.utilisateur import Utilisateur

router = APIRouter(prefix="/roles", tags=["roles"])

LIBELLE_ROLE: dict[RoleUtilisateur, str] = {
    RoleUtilisateur.ADMINISTRATEUR: "Administrateur",
    RoleUtilisateur.REFERENT_SHEQ: "Référent SHEQ",
    RoleUtilisateur.RESPONSABLE: "Responsable",
    RoleUtilisateur.TECHNICIEN: "Technicien",
    RoleUtilisateur.COLLABORATEUR: "Collaborateur",
}

# Libellé lisible de chaque permission réelle (app/core/permissions.py). Seule
# duplication assumée : le LIBELLÉ d'affichage — les rôles qui la détiennent
# sont lus par introspection juste en dessous, jamais recopiés à la main.
LIBELLE_PERMISSION: dict[str, str] = {
    "GERER_UTILISATEURS": "Gérer les comptes utilisateurs",
    "GERER_SITES": "Gérer les sites",
    "TRAITER_SIGNALEMENTS": "Traiter les signalements",
    "GERER_ACTIONS": "Créer et piloter le plan d'action",
    "CONSULTER_TABLEAU_BORD": "Consulter le tableau de bord",
    "GERER_EPI": "Gérer les EPI",
    "VALIDER_PERMIS": "Valider les permis de travail en hauteur",
    "GERER_CHECKLISTS": "Gérer les référentiels de checklist",
    "GERER_PARC": "Gérer le parc d'équipements",
    "IMPORTER_PARC": "Importer le parc d'équipements",
    "GERER_RISQUES": "Gérer le registre des risques",
    "GERER_FORMATIONS": "Gérer les formations",
    "GERER_AUDITS": "Gérer les audits internes",
    "GERER_REVUES": "Gérer les revues de direction",
    "GERER_DOCUMENTS": "Gérer les documents (SMI)",
    "APPROUVER_DOCUMENTS": "Approuver les documents",
    "GERER_DECHETS": "Gérer le registre des déchets",
    "ENVOYER_ENQUETE_SATISFACTION": "Envoyer une enquête de satisfaction",
    "TRAITER_SATISFACTION": "Traiter les réponses de satisfaction",
    "GERER_SECRETS": "Gérer le coffre-fort",
    "CONSULTER_JOURNAL_SECRETS": "Consulter le journal d'accès au coffre-fort",
}


class RoleSortie(BaseModel):
    valeur: str
    libelle: str
    perimetre: str


class PermissionSortie(BaseModel):
    cle: str
    libelle: str
    roles: list[str]


class RolesSortie(BaseModel):
    roles: list[RoleSortie]
    permissions: list[PermissionSortie]


@router.get("", response_model=RolesSortie)
def obtenir_roles(
    utilisateur: Utilisateur = Depends(get_current_user),
) -> RolesSortie:
    """Les 5 rôles fixes (CLAUDE.md §6) et les permissions réellement
    appliquées par les routes — lues par introspection de `Permissions`.
    Ouvert à tout utilisateur authentifié (comme la table CLAUDE.md §6
    qu'il remplace) : connaître les périmètres n'est pas un privilège
    sensible, contrairement à la gestion des comptes eux-mêmes."""
    roles = [
        RoleSortie(valeur=r.value, libelle=LIBELLE_ROLE[r], perimetre=PERIMETRE_PAR_ROLE[r])
        for r in RoleUtilisateur
    ]
    permissions = [
        PermissionSortie(
            cle=cle,
            libelle=LIBELLE_PERMISSION.get(cle, cle.replace("_", " ").capitalize()),
            roles=[r.value for r in valeur],
        )
        for cle, valeur in vars(Permissions).items()
        if not cle.startswith("_") and isinstance(valeur, tuple)
    ]
    return RolesSortie(roles=roles, permissions=permissions)
