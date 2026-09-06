"""Référentiel des 4 étapes SLAM, repris tel quel de la maquette de référence
(docs/maquettes/Maquettes_SHEQ_Management_v2.html, écran #s-slam, script `const S`).
Ce n'est pas un modèle SQLAlchemy — ni ÉTAPE_SLAM ni POINT_SLAM ne figurent parmi
les 14 entités demandées (décision actée au prompt 0.2) : ce référentiel est une
constante Python, utilisée pour valider la forme des évaluations soumises."""

ETAPES_SLAM = [
    {
        "lettre": "S",
        "titre": "S'arrêter",
        "sous_titre": "Avant de monter, prenez une minute",
        "points": [
            "Je connais la tâche et le mode opératoire",
            "Je suis apte : pas de fatigue ni de vertige",
            "Le permis de travail est validé",
            "Le surveillant au sol est présent",
        ],
    },
    {
        "lettre": "L",
        "titre": "Observer",
        "sous_titre": "Inspectez la zone et repérez les dangers",
        "points": [
            "Météo favorable : ni vent fort ni orage",
            "Structure et points d'ancrage vérifiés",
            "Distances aux lignes électriques respectées",
            "Zone au sol balisée",
        ],
    },
    {
        "lettre": "A",
        "titre": "Évaluer",
        "sous_titre": "Ces risques sont-ils maîtrisables ?",
        "points": [
            "Risque de chute maîtrisé par l'ancrage",
            "Outils attachés contre la chute d'objets",
            "Moyens d'alerte et plan de sauvetage connus",
            "Chaleur et durée prises en compte",
        ],
    },
    {
        "lettre": "M",
        "titre": "Maîtriser",
        "sous_titre": "Dernier contrôle avant la montée",
        "points": [
            "Harnais et longe double vérifiés",
            "Casque à jugulaire porté",
            "Ancrage 100 % du temps, même en déplacement",
            "Contact testé avec le surveillant",
        ],
    },
]

NOMBRE_ETAPES = len(ETAPES_SLAM)
NOMBRE_POINTS_PAR_ETAPE = 4
