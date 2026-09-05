# Journal d'avancement

Suivi du lotissement défini dans `docs/CDC-SHEQ-001.docx` (chapitre 13) et dans
`PROMPTS_DEVELOPPEMENT.md`. Un module à la fois, chaque ligne cochée correspond à
un prompt terminé, testé et commité.

## LOT 0 — Fondations

- [x] 0.1 — Initialisation du dépôt (squelette backend/frontend, docker-compose, README)
- [ ] 0.2 — Modèle de données (14 entités SQLAlchemy + migration Alembic initiale)
- [ ] 0.3 — Authentification et rôles (JWT, argon2, matrice des droits)

## LOT 1 — MVP (signalements, actions, tableau de bord, hors connexion)

- [ ] 1.1 — API des signalements
- [ ] 1.2 — API du plan d'action
- [ ] 1.3 — Interface mobile : saisie d'un signalement
- [ ] 1.4 — Mode hors connexion et synchronisation
- [ ] 1.5 — Tableau de bord
- [ ] 1.6 — Recette du lot 1

## LOT 2 — Travaux en hauteur

- [ ] 2.1 — API des EPI
- [ ] 2.2 — SLAM et permis, avec la règle de blocage
- [ ] 2.3 — Interfaces SLAM et permis
- [ ] 2.4 — Inspections

## LOT 3 — Parc, configurations et coffre-fort

- [ ] 3.1 — Parc d'équipements
- [ ] 3.2 — Fiches de configuration par marque
- [ ] 3.3 — Coffre-fort d'identifiants

## LOT 4 — Pilotage et modules complémentaires

- [ ] 4.1 — Risques
- [ ] 4.2 — Formations, audits et revues
- [ ] 4.3 — Documents, visiteurs, déchets, satisfaction
- [ ] 4.4 — Notifications

## LOT 5 — Finalisation

- [ ] 5.1 — Génération des PDF
- [ ] 5.2 — Sécurité et revue finale
- [ ] 5.3 — Documentation et déploiement

---

### Détail — Prompt 0.1 (terminé le 2026-09-05)

Créé, sans logique métier :

- `backend/` : structure FastAPI (`app/core`, `models`, `schemas`, `api/v1`,
  `services`, `db`), `main.py` exposant `/health`, configuration par variables
  d'environnement (`pydantic-settings`, aucun secret par défaut), `.env.example`,
  `requirements.txt`, `Dockerfile`, test pytest sur `/health` (passe).
- `frontend/` : Vue 3 + Vite, écran d'accueil unique qui interroge `/health` pour
  prouver la liaison front/back, variables CSS de la charte (point 8 de CLAUDE.md,
  affinées avec les maquettes) dans `src/style.css`.
- `docker-compose.yml` : services `api`, `db` (postgres:16-alpine), `frontend`.
- `.gitignore` Python + Node, `README.md` d'installation.
- `docs/` : copie de `CDC-SHEQ-001.docx`, des deux maquettes HTML et des 5 diagrammes.

**Écarts par rapport au prompt d'origine, à signaler :**
- Ajout de `vue-router` et `pinia` dès ce prompt (non listés dans le tableau du
  point 3 de CLAUDE.md, mais les dossiers `router/` et `stores/` figurent dans
  l'arborescence du point 4 — sans ces paquets ils seraient vides et inutiles).
- `pytest`, `pytest-cov` et `httpx` ajoutés au `requirements.txt` unique du backend
  (pas de fichier séparé de dépendances de développement) : CLAUDE.md demande des
  tests écrits en même temps que le code, donc pytest est nécessaire dès ce prompt.
- Les fiches de configuration confidentielles (FOR-SHEQ-006 à 009) n'ont pas été
  copiées dans `docs/formulaires/` : elles sont classées accès restreint dans le
  SMI documentaire. Voir `docs/formulaires/LISEZ-MOI.txt` — à traiter au prompt 3.2
  en lisant les sources sans les versionner.
- Deux exemplaires du CDC existent dans le SMI documentaire (un à la racine du
  poste, un dans `02-Pilotage`) ; c'est la version de `02-Pilotage`
  (`CDC-SHEQ-001_Cahier_des_Charges_Application.docx`) qui a été copiée ici. À
  confirmer avec la liste maîtresse des documents que c'est bien la version en
  vigueur.

**Vérifié en conditions réelles :** `pytest` passe (1/1), le serveur démarre avec
`uvicorn` et répond `{"status":"ok"}` sur `/health`, `/docs` répond 200.
