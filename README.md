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

L'API est disponible sur http://localhost:8000, la documentation interactive sur
http://localhost:8000/docs, et l'état de santé sur http://localhost:8000/health.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env          # Windows : copy — Linux/macOS : cp
npm run dev
```

L'interface est disponible sur http://localhost:5173. Elle affiche l'état de
connexion à l'API sur l'écran d'accueil.

### Avec Docker

```bash
docker compose up --build
```

Démarre la base PostgreSQL, l'API (port 8000) et le frontend (port 5173).
Nécessite un fichier `backend/.env` déjà renseigné (voir ci-dessus).

## Tests

```bash
cd backend
pytest
```

## Structure du dépôt

Voir le point 4 de `CLAUDE.md` pour le détail de l'arborescence et sa justification.

## Documentation de référence

- `docs/CDC-SHEQ-001.docx` — cahier des charges complet
- `docs/maquettes/` — maquettes interactives (mobile et desktop), référence visuelle
  et ergonomique : tout écran livré doit s'y conformer
- `docs/diagrammes/` — cas d'utilisation, séquence, activité, MCD, architecture

## État d'avancement

Voir `docs/JOURNAL.md`.
