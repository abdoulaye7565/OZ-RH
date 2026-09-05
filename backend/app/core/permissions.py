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
    # Section 5.2.5 du CDC, "Acteurs" : "Rédaction et mise à jour : référent SHEQ".
    # La mise à jour de l'avancement d'une action reste ouverte au responsable
    # désigné de cette action précise (vérifié route par route, pas ici) : cette
    # constante ne couvre que la création et les actions globales sur le plan.
    GERER_ACTIONS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Le tableau de bord agrège TOUS les signalements, y compris ceux qu'un
    # technicien/collaborateur ne peut normalement pas voir individuellement
    # (visibilité restreinte à ses propres saisies, prompt 1.1) : ouvrir le
    # tableau de bord à ces deux rôles ferait fuir cette agrégation. Restreint
    # aux rôles de consultation large déjà identifiés dans le CDC (5.2.1, 5.2.5).
    CONSULTER_TABLEAU_BORD: tuple[R, ...] = (R.ADMINISTRATEUR, R.REFERENT_SHEQ, R.RESPONSABLE)
    # Section 5.3.2 du CDC, "Acteurs" : "Gestion : référent SHEQ."
    GERER_EPI: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
