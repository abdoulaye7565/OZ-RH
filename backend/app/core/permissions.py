"""Matrice des droits par rôle — module unique de référence (CLAUDE.md point 6).

Les routes protégées utilisent `Depends(require_role(*Permissions.X))` avec les
constantes ci-dessous plutôt que de répéter des tuples de rôles dans chaque route.

`Permissions` ne contient pour l'instant que ce qui est réellement utilisé :
complétée module par module (lots 1 à 4), jamais par anticipation spéculative,
conformément au point 9 de CLAUDE.md ("un module à la fois").
"""
from app.models.enums import RoleUtilisateur as R

# Reprise littérale du tableau du point 6 de CLAUDE.md, à titre de documentation et
# d'introspection (utile par exemple pour un futur écran "gestion des rôles").
PERIMETRE_PAR_ROLE: dict[R, str] = {
    R.ADMINISTRATEUR: "Tout, y compris utilisateurs et paramètres",
    R.REFERENT_SHEQ: (
        "Risques, actions, inspections, formations, documents — aucun accès au coffre-fort"
    ),
    R.RESPONSABLE: "Valide les permis, consulte les registres, accède au coffre-fort",
    R.TECHNICIEN: (
        "Saisit : signalements, SLAM, configurations, inspections, vérifications EPI ; "
        "coffre-fort limité"
    ),
    R.COLLABORATEUR: "Signalements, consultation de la politique, quiz",
}


class Permissions:
    GERER_UTILISATEURS: tuple[R, ...] = (R.ADMINISTRATEUR,)
    # Section 5.2.1 du CDC, "Acteurs" : "Traitement : référent SHEQ". L'administrateur
    # est ajouté par application du principe "Tout" de son propre périmètre (point 6
    # de CLAUDE.md), pas par une mention explicite de la section 5.2.1.
    TRAITER_SIGNALEMENTS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
