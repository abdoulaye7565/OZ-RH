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
    # Les sites (lieux d'intervention) relèvent des « paramètres » du périmètre
    # administrateur (tableau des rôles, CLAUDE.md §6). La consultation reste
    # ouverte à tout le personnel (résolution d'un site_id en nom).
    GERER_SITES: tuple[R, ...] = (R.ADMINISTRATEUR,)
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
    # Section 5.2.2 du CDC, "Acteurs" : "Validation : responsable ou chef
    # d'équipe" — pas de rôle "chef d'équipe" distinct dans la matrice (point 6
    # de CLAUDE.md), couvert par "responsable".
    VALIDER_PERMIS: tuple[R, ...] = (R.RESPONSABLE, R.ADMINISTRATEUR)
    # Section 5.3.1 du CDC ne nomme pas d'acteur unique pour la gestion du
    # référentiel de checklists ; traité comme les autres référentiels
    # SHEQ (EPI, documents) : propriété du référent SHEQ.
    GERER_CHECKLISTS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.2.3 du CDC, "Acteurs" : "Saisie : techniciens." La matrice de
    # rôles (point 6 de CLAUDE.md) n'a pas de rôle "responsable technique" ni
    # "direction" distinct : l'administrateur couvre "Tout" par son propre
    # périmètre.
    GERER_PARC: tuple[R, ...] = (R.TECHNICIEN, R.ADMINISTRATEUR)
    # Section 5.2.3, "Acteurs" : "consultation et administration : responsable
    # technique, direction". Aucun rôle "responsable technique"/"direction"
    # dans la matrice : rapproché du rôle RESPONSABLE existant, le plus proche
    # sémantiquement — à confirmer avec le référent SHEQ. L'import initial est
    # un acte d'administration du référentiel (reprise de données), pas une
    # saisie de terrain : distinct de GERER_PARC, plus restrictif.
    IMPORTER_PARC: tuple[R, ...] = (R.RESPONSABLE, R.ADMINISTRATEUR)
    # Section 5.2.5 du CDC, "Acteurs" : "Rédaction et mise à jour : référent
    # SHEQ." Couvre création, réévaluation et import du registre — le CDC ne
    # distingue pas d'acteur "administration" séparé pour ce module (à la
    # différence de 5.2.3) : une seule constante suffit ici.
    GERER_RISQUES: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.3.3 du CDC, "Acteurs" : "Gestion : référent SHEQ." Couvre
    # compétences, habilitations, séances et référentiel de quiz.
    GERER_FORMATIONS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.3.4, "Acteurs" : "Audit : référent SHEQ ou auditeur désigné."
    # Aucun rôle "auditeur" distinct dans la matrice (point 6, CLAUDE.md) :
    # couvert par référent SHEQ, comme pour les autres référentiels SHEQ.
    GERER_AUDITS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.3.4, "Acteurs" : "Revue : direction." Aucun rôle "direction"
    # distinct dans la matrice : rapproché du rôle RESPONSABLE, même
    # interprétation que pour le parc (5.2.3). Référent SHEQ ajouté malgré
    # l'absence de mention explicite dans les Acteurs : FOR-SHEQ-016 (le
    # formulaire réel) le désigne comme rédacteur et cosignataire du compte
    # rendu — à confirmer avec le référent SHEQ si ce rapprochement est trop
    # large.
    GERER_REVUES: tuple[R, ...] = (R.REFERENT_SHEQ, R.RESPONSABLE, R.ADMINISTRATEUR)
    # Section 5.3.5, "Acteurs" : "Rédaction : référent SHEQ." Couvre dépôt,
    # nouvelle version et accusé de lecture (l'accusé est en réalité ouvert à
    # tout utilisateur pour SA PROPRE lecture — vérifié route par route).
    GERER_DOCUMENTS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.3.5, "Acteurs" : "Approbation : direction." Même rapprochement
    # que GERER_REVUES.
    APPROUVER_DOCUMENTS: tuple[R, ...] = (R.RESPONSABLE, R.ADMINISTRATEUR)
    # Section 5.3.6, "Acteurs" : "Déchets : référent SHEQ."
    GERER_DECHETS: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.3.6, "Acteurs" : "Satisfaction : clients, avec traitement par
    # le référent SHEQ" — l'envoi d'une enquête n'est pas réservé au seul
    # référent SHEQ dans le texte (un technicien termine une intervention et
    # peut vouloir l'envoyer immédiatement) : ouvert au technicien également,
    # à la différence du traitement des réponses (réservé au référent SHEQ).
    ENVOYER_ENQUETE_SATISFACTION: tuple[R, ...] = (R.TECHNICIEN, R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    TRAITER_SATISFACTION: tuple[R, ...] = (R.REFERENT_SHEQ, R.ADMINISTRATEUR)
    # Section 5.3.6, "Acteurs" : "Visiteurs : accueil" — aucun rôle "accueil"
    # distinct dans la matrice : ouvert à tout utilisateur authentifié plutôt
    # que restreint, l'accueil des visiteurs n'étant pas un privilège
    # sensible comparable aux autres référentiels SHEQ.
    # Section 5.2.4, "Acteurs" : "Création et modification : responsable
    # technique et administrateur." La CONSULTATION, elle, n'est pas une
    # permission globale : elle dépend du `role_requis` de chaque secret
    # (référent SHEQ et collaborateur toujours exclus — voir
    # secret_service.NIVEAU_ROLE_SECRET) et n'utilise donc pas cette
    # constante, vérifiée directement dans le service.
    GERER_SECRETS: tuple[R, ...] = (R.RESPONSABLE, R.ADMINISTRATEUR)
    # Le CDC ne précise pas qui peut consulter le journal des accès à un
    # secret (par opposition au secret lui-même) — rapproché des mêmes rôles
    # que sa gestion, décision confirmée avec l'utilisateur (2026-09-08).
    CONSULTER_JOURNAL_SECRETS: tuple[R, ...] = (R.RESPONSABLE, R.ADMINISTRATEUR)
