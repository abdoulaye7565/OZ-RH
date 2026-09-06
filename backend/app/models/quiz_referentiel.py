"""Contenu réel des 10 questions du quiz de sensibilisation, reprises telles
quelles de FOR-SHEQ-015 « Quiz d'évaluation post-sensibilisation SHEQ »,
corrigé inclus dans le formulaire source lui-même (« Corrigé (à détacher pour
l'animateur) »). Module partagé entre la migration de données et les fixtures
de test — même principe que checklist_referentiel.py et audit_referentiel.py."""

LIGNES_QUIZ_REFERENTIEL: list[dict] = [
    {
        "enonce": "Que signifie SHEQ ?",
        "choix": [
            {"lettre": "a", "texte": "Sécurité, Hygiène, Équipement, Qualité"},
            {"lettre": "b", "texte": "Safety, Health, Environment and Quality (Sécurité, Santé, Environnement, Qualité)"},
            {"lettre": "c", "texte": "Système Harmonisé d'Évaluation de la Qualité"},
        ],
        "reponse_correcte": "b",
    },
    {
        "enonce": "Vous constatez un câble qui traverse un passage. Que faites-vous ?",
        "choix": [
            {"lettre": "a", "texte": "Je l'enjambe, quelqu'un d'autre s'en occupera"},
            {"lettre": "b", "texte": "Je le signale (fiche de signalement) et je participe à sa mise en sécurité"},
            {"lettre": "c", "texte": "J'attends l'inspection mensuelle"},
        ],
        "reponse_correcte": "b",
    },
    {
        "enonce": "Un presque-accident (sans blessure ni dégât) doit-il être signalé ?",
        "choix": [
            {"lettre": "a", "texte": "Oui, toujours : il permet d'éviter un vrai accident demain"},
            {"lettre": "b", "texte": "Non, il n'y a pas eu de conséquence"},
        ],
        "reponse_correcte": "a",
    },
    {
        "enonce": "Avant de monter sur un pylône, la méthode SLAM consiste à :",
        "choix": [
            {"lettre": "a", "texte": "S'arrêter, Observer, Évaluer, Maîtriser"},
            {"lettre": "b", "texte": "Monter vite pour finir avant la pluie"},
            {"lettre": "c", "texte": "Signaler, Lire, Attacher, Monter"},
        ],
        "reponse_correcte": "a",
    },
    {
        "enonce": "Pendant un travail en hauteur, on doit être attaché :",
        "choix": [
            {"lettre": "a", "texte": "Seulement au sommet"},
            {"lettre": "b", "texte": "100 % du temps, y compris pendant les déplacements"},
            {"lettre": "c", "texte": "Seulement si le vent se lève"},
        ],
        "reponse_correcte": "b",
    },
    {
        "enonce": "Un harnais qui a arrêté une chute :",
        "choix": [
            {"lettre": "a", "texte": "Peut être réutilisé s'il semble en bon état"},
            {"lettre": "b", "texte": "Est réformé définitivement"},
        ],
        "reponse_correcte": "b",
    },
    {
        "enonce": "En cas d'incendie sur un équipement électrique, on utilise :",
        "choix": [
            {"lettre": "a", "texte": "De l'eau"},
            {"lettre": "b", "texte": "Un extincteur CO2"},
        ],
        "reponse_correcte": "b",
    },
    {
        "enonce": "Un bon mot de passe d'équipement est :",
        "choix": [
            {"lettre": "a", "texte": "Le mot de passe par défaut du constructeur, plus simple à retenir"},
            {"lettre": "b", "texte": "Un mot de passe fort, unique, conservé dans un emplacement sécurisé"},
        ],
        "reponse_correcte": "b",
    },
    {
        "enonce": "Pour prévenir les TMS au poste informatique :",
        "choix": [
            {"lettre": "a", "texte": "Régler son poste (écran à hauteur des yeux) et faire des pauses régulières"},
            {"lettre": "b", "texte": "Travailler sans pause pour finir plus tôt"},
        ],
        "reponse_correcte": "a",
    },
    {
        "enonce": "Le droit de retrait permet :",
        "choix": [
            {"lettre": "a", "texte": "De refuser une tâche présentant un danger grave et imminent, sans sanction"},
            {"lettre": "b", "texte": "De quitter le travail quand on veut"},
        ],
        "reponse_correcte": "a",
    },
]


def lignes_a_semer() -> list[dict]:
    return [{"enonce": l["enonce"], "choix": l["choix"], "reponse_correcte": l["reponse_correcte"]} for l in LIGNES_QUIZ_REFERENTIEL]
