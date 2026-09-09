# SHEQ Management

Application de gestion du système de management SHEQ (Sécurité, Santé, Environnement,
Qualité) pour **Hirondelles IT Lab**. Digitalise les 36 documents papier du SMI
(voir `docs/CDC-SHEQ-001.docx`).

Le contexte complet du projet (contraintes, stack, règles métier, charte visuelle)
est dans `CLAUDE.md` à la racine — à lire avant toute contribution.

## Stack

- **Backend** : Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, SQLite (dev) / PostgreSQL (prod)
- **Frontend** : Vue 3 (Composition API) + Vite, Pinia, Vue Router
- **Mobile terrain** : PWA (service worker + IndexedDB, pas d'app native)
- **Conteneurs** : Docker + docker-compose

## Installation — développement

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
copy .env.example .env          # Windows : copy — Linux/macOS : cp
```

Compléter `.env` :
- `JWT_SECRET_KEY` : `python -c "import secrets; print(secrets.token_hex(32))"`
- `FERNET_MASTER_KEY` : `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

Lancer l'API :

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur http://localhost:8000, la documentation interactive
(Swagger, avec description de chaque route et des règles métier non triviales)
sur http://localhost:8000/docs, et l'état de santé sur http://localhost:8000/health.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env          # Windows : copy — Linux/macOS : cp
npm run dev
```

L'interface est disponible sur http://localhost:5173. Elle affiche l'état de
connexion à l'API sur l'écran d'accueil.

### Avec Docker (développement)

```bash
docker compose up --build
```

Démarre la base PostgreSQL, l'API (port 8000) et le frontend (port 5173), avec
rechargement à chaud (code source monté en volume). Nécessite un fichier
`backend/.env` déjà renseigné (voir ci-dessus).

## Tests

```bash
cd backend
pytest
```

Aucun test automatisé côté frontend pour l'instant (Vitest est dans la pile
technique prévue, mais aucune des 8 vues livrées n'a encore de test — limite
connue, voir `docs/JOURNAL.md`, prompt 5.3).

## Données de démonstration

```bash
cd backend
python scripts/donnees_demo.py
```

Peuple une base **vide** (refuse de s'exécuter si des utilisateurs existent déjà)
avec des données fictives couvrant la plupart des modules — sites, un compte par
rôle, risques, EPI, un équipement et sa fiche de configuration, signalements
(dont un anonyme), SLAM et permis (y compris une démonstration de la règle de
blocage), inspection, formation, audit, revue de direction, document, visiteur,
déchet. Le mot de passe commun et les identifiants générés s'affichent en fin
d'exécution. Utilise l'API réelle (pas d'insertion SQL directe, hormis les
sites et le premier compte administrateur — voir l'en-tête du script).

## Manuel utilisateur

Voir `docs/MANUEL_UTILISATEUR.md`, avec captures d'écran réelles par profil.

## Sauvegarde et restauration

```bash
cd backend
python scripts/sauvegarde.py --destination ./sauvegardes
python scripts/restaurer.py ./sauvegardes/sheq-sauvegarde-AAAA-MM-JJ_HHhMM --confirmer
```

Sauvegarde la base (copie sûre SQLite ou `pg_dump` PostgreSQL selon
`DATABASE_URL`) et le dossier `storage/` (pièces jointes). Ne sauvegarde
jamais `.env` : les secrets se conservent séparément (CLAUDE.md, règle 4).
Procédure testée de bout en bout (sauvegarde → incident simulé → restauration
→ vérification) sur SQLite ; le chemin PostgreSQL (`pg_dump`/`pg_restore`) suit
la même logique mais n'a pas pu être exercé dans l'environnement de
développement (ni Docker ni PostgreSQL disponibles localement).

## Déploiement en production

```bash
cp .env.prod.example .env              # variables du compose (Postgres, URLs publiques)
cp backend/.env.example backend/.env   # secrets applicatifs (JWT, Fernet, SMTP)
docker compose -f docker-compose.prod.yml up --build -d
```

Différences avec le compose de développement : images construites une fois
(aucun montage du code source, aucun rechargement à chaud), frontend compilé
et servi par Nginx (pas le serveur de développement Vite), aucun mot de passe
par défaut (`docker compose` refuse de démarrer si une variable requise est
absente plutôt que de se rabattre sur une valeur faible). Voir les commentaires
de `docker-compose.prod.yml` et `.env.prod.example` pour le détail de chaque
variable.

## Structure du dépôt

Voir le point 4 de `CLAUDE.md` pour le détail de l'arborescence et sa justification.

## Documentation de référence

- `docs/CDC-SHEQ-001.docx` — cahier des charges complet
- `docs/maquettes/` — maquettes interactives (mobile et desktop), référence visuelle
  et ergonomique : tout écran livré doit s'y conformer
- `docs/diagrammes/` — cas d'utilisation, séquence, activité, MCD, architecture

## État d'avancement

Voir `docs/JOURNAL.md`.
