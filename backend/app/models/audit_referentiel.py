"""Contenu réel des 22 exigences d'audit, reprises telles quelles de
FOR-SHEQ-017 « Grille d'audit interne du système SHEQ (base ISO 45001
simplifiée) » — 6 chapitres réels (en-têtes de section du classeur), pas
inventés. Module partagé entre la migration de données (alembic) et les
fixtures de test (tests/conftest.py), pour ne jamais diverger — même principe
que checklist_referentiel.py (prompt 2.4)."""

LIGNES_AUDIT_REFERENTIEL: list[dict] = [
    {"numero": 1, "chapitre": "Contexte et leadership", "libelle": "La politique SHEQ est signée, affichée et connue du personnel"},
    {"numero": 2, "chapitre": "Contexte et leadership", "libelle": "Les rôles et responsabilités SHEQ sont définis (référent, direction, salariés)"},
    {"numero": 3, "chapitre": "Contexte et leadership", "libelle": "Le personnel est consulté et participe (signalements, suggestions)"},
    {"numero": 4, "chapitre": "Planification", "libelle": "Le registre des risques est complet et à jour (REG-SHEQ-001)"},
    {"numero": 5, "chapitre": "Planification", "libelle": "Le plan d'action est tenu à jour avec responsables et échéances (PLA-SHEQ-001)"},
    {"numero": 6, "chapitre": "Planification", "libelle": "Les exigences légales applicables sont identifiées (dossier 08)"},
    {"numero": 7, "chapitre": "Support", "libelle": "Les compétences et habilitations sont suivies (MAT-SHEQ-001)"},
    {"numero": 8, "chapitre": "Support", "libelle": "Les EPI sont fournis, adaptés et suivis (REG-SHEQ-003)"},
    {"numero": 9, "chapitre": "Support", "libelle": "Les sensibilisations planifiées sont réalisées et tracées (PLA-SHEQ-003, FOR-SHEQ-014/015)"},
    {"numero": 10, "chapitre": "Support", "libelle": "La documentation est maîtrisée : versions, liste maîtresse, archives (PRO-SHEQ-004)"},
    {"numero": 11, "chapitre": "Réalisation des activités", "libelle": "Les travaux en hauteur respectent la procédure (permis, SLAM, surveillant) (PRO-SHEQ-002)"},
    {"numero": 12, "chapitre": "Réalisation des activités", "libelle": "Les configurations sont tracées et sauvegardées (PRO-SHEQ-003, fiches FOR-SHEQ-006 à 009)"},
    {"numero": 13, "chapitre": "Réalisation des activités", "libelle": "Les achats/réceptions suivent la procédure (PRO-SHEQ-005)"},
    {"numero": 14, "chapitre": "Réalisation des activités", "libelle": "Le plan de sauvetage en hauteur est connu et exercé (PLA-SHEQ-002)"},
    {"numero": 15, "chapitre": "Réalisation des activités", "libelle": "L'accueil sécurité des nouveaux et visiteurs est réalisé (FOR-SHEQ-003, REG-SHEQ-004)"},
    {"numero": 16, "chapitre": "Évaluation des performances", "libelle": "Les inspections périodiques sont réalisées (FOR-SHEQ-005/010/011)"},
    {"numero": 17, "chapitre": "Évaluation des performances", "libelle": "Les incidents sont déclarés, enregistrés et analysés (PRO-SHEQ-001, REG-SHEQ-002)"},
    {"numero": 18, "chapitre": "Évaluation des performances", "libelle": "Le tableau de bord est renseigné et analysé (TDB-SHEQ-001)"},
    {"numero": 19, "chapitre": "Évaluation des performances", "libelle": "La revue de direction se tient et est documentée (FOR-SHEQ-016)"},
    {"numero": 20, "chapitre": "Amélioration", "libelle": "Les actions correctives sont soldées dans les délais"},
    {"numero": 21, "chapitre": "Amélioration", "libelle": "Les enseignements des événements sont partagés (retours d'expérience)"},
    {"numero": 22, "chapitre": "Amélioration", "libelle": "Le système évolue (nouvelles procédures, mises à jour du registre des risques)"},
]


def lignes_a_semer() -> list[dict]:
    return list(LIGNES_AUDIT_REFERENTIEL)
