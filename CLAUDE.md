# CLAUDE.md — Contexte du projet SHEQ Management

> Ce fichier est le contexte permanent du projet. Relis-le au début de chaque session.
> Il fait autorité : en cas de contradiction avec une demande ponctuelle, signale-le avant d'agir.

---

## 1. Le projet en une phrase

Application de gestion d'un système de management SHEQ (Sécurité, Santé, Environnement, Qualité)
pour **Hirondelles IT Lab**, entreprise malienne de services numériques dont les techniciens
interviennent sur pylônes et toitures. Elle digitalise 36 documents papier existants.

Référence du cahier des charges : **CDC-SHEQ-001**.

## 2. Contraintes fondatrices — ne jamais les contourner

1. **Le mode hors connexion est une exigence, pas une option.** Les techniciens travaillent
   sur des pylônes sans réseau. Toute fonctionnalité de terrain doit fonctionner hors ligne
   et se synchroniser au retour du réseau.
2. **Aucune suppression physique.** On archive, on désactive, jamais `DELETE`.
3. **Traçabilité intégrale.** Chaque création, modification, validation est horodatée avec son auteur.
4. **Les secrets ne sont jamais en clair.** Ni en base, ni dans les logs, ni dans les exports,
   ni dans les sauvegardes.
5. **L'interface est en français.** Code et commentaires en français également, UTF-8.

## 3. Stack technique imposée

| Couche | Technologie |
|---|---|
| API | Python 3.11+, **FastAPI**, Pydantic v2 |
| ORM | **SQLAlchemy 2.x** + Alembic (migrations) |
| Base | **SQLite** en développement, **PostgreSQL** en production |
| Frontend | **Vue.js 3** (Composition API) + Vite |
| Mobile | **PWA** : service worker + IndexedDB (pas d'app native) |
| Auth | **JWT** (access + refresh), mots de passe hachés avec bcrypt ou argon2 |
| Chiffrement | **Fernet** (bibliothèque `cryptography`), clé maîtresse hors base (variable d'environnement) |
| Conteneurs | **Docker** + docker-compose |
| Tests | **pytest** (backend), Vitest (frontend) |

Ne propose pas de changer cette pile. Si une contrainte technique la rend inadaptée sur un point
précis, signale-le et propose une solution dans le cadre existant.

## 4. Architecture du dépôt

```
sheq-management/
├── backend/
│   ├── app/
│   │   ├── main.py              # point d'entrée FastAPI
│   │   ├── core/                # config, sécurité, chiffrement, dépendances
│   │   ├── models/              # modèles SQLAlchemy
│   │   ├── schemas/             # schémas Pydantic
│   │   ├── api/v1/              # routes par module
│   │   ├── services/            # logique métier (règles de gestion)
│   │   └── db/                  # session, base, seed
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/               # une vue par écran
│   │   ├── components/
│   │   ├── stores/              # Pinia
│   │   ├── services/            # appels API, file d'attente hors ligne
│   │   └── router/
│   └── vite.config.js
├── docker-compose.yml
└── docs/                        # CDC, maquettes, diagrammes
```

## 5. Modèle de données — entités principales

`UTILISATEUR`, `SITE`, `RISQUE`, `ACTION`, `SIGNALEMENT`, `EQUIPEMENT`, `CONFIGURATION`,
`SECRET`, `JOURNAL_ACCES`, `EPI`, `PERMIS`, `EVALUATION_SLAM`, `INSPECTION`, `DOCUMENT`.

Toutes les tables portent : `id`, `cree_le`, `cree_par_id`, `modifie_le`, `modifie_par_id`,
`archive` (booléen), `organisation_id` (préparation multi-entreprises, non exploité en v1).

## 6. Rôles et droits

| Rôle | Périmètre |
|---|---|
| `administrateur` | Tout, y compris utilisateurs et paramètres |
| `referent_sheq` | Risques, actions, inspections, formations, documents — **aucun accès au coffre-fort** |
| `responsable` | Valide les permis, consulte les registres, accède au coffre-fort |
| `technicien` | Saisit : signalements, SLAM, configurations, inspections, vérifications EPI ; coffre-fort limité |
| `collaborateur` | Signalements, consultation de la politique, quiz |

Principe du moindre privilège. Séparation des responsabilités : un même utilisateur ne peut
demander **et** valider un permis.

## 7. Règles métier critiques — à implémenter côté serveur, jamais seulement côté interface

1. **Blocage du permis** : un permis ne peut être délivré si un EPI affecté à un intervenant est
   non conforme (vérification périodique dépassée, statut retiré ou réformé), ou si un intervenant
   n'a pas d'évaluation SLAM avec décision `GO`, ou si aucun surveillant n'est désigné.
   Le surveillant ne peut pas figurer parmi les intervenants.
2. **SLAM** : le passage à l'étape suivante est impossible tant que tous les points de l'étape
   courante ne sont pas validés. Une décision `NO_GO` s'enregistre sans validation hiérarchique
   et ne bloque rien pour l'intervenant.
3. **Anonymat** : un signalement anonyme ne référence aucun utilisateur, y compris dans les
   tables techniques et les logs.
4. **Journal du coffre-fort** : chaque consultation est enregistrée. Le journal est en écriture
   seule — aucune route ne permet de le modifier ou de le supprimer, même pour un administrateur.
5. **Immutabilité des configurations** : une fiche de configuration enregistrée ne peut être
   modifiée ; une correction crée une nouvelle fiche, l'historique reste consultable.
6. **Calculs automatiques** :
   - criticité d'un risque = probabilité × gravité ; niveau selon les seuils 4, 8, 15
   - taux de conformité d'une inspection = conformes ÷ (conformes + non conformes), les « sans objet » exclus
   - un point non conforme génère automatiquement une action corrective
   - prochaine vérification EPI = dernière vérification + 12 mois
7. **Nommage** : `SIG-AAAA-NNN` (signalements), `ENR-SHEQ-AAAA-NNN` (enregistrements),
   `SITE-IDENTITY-AAAAMMJJ` (fichiers de sauvegarde). Numéro attribué **à la synchronisation**,
   pas à la saisie hors ligne (référence provisoire locale entre-temps).

## 8. Charte visuelle

```
--navy:#16305B  --navy2:#25467E  --navy-soft:#EDF1F8
--gold:#B8901B  --gold-soft:#FBF3DC
--red:#B42318   --orange:#B54708  --green:#067647  --blue:#175CD3
--ink:#0F172A   --mut:#64748B     --line:#E2E6EC   --bg:#F5F6F8
```
Police **Inter**. Icônes SVG au trait (style Lucide), jamais d'emoji dans l'interface.
Codes couleur constants : vert = conforme/réalisé, orange = à surveiller/échéance proche,
rouge = non conforme/en retard, gris = archivé/sans objet.

Les maquettes de référence sont dans `docs/maquettes/` (41 écrans). L'écran livré doit
correspondre à sa maquette : contenu, enchaînement, messages.

## 9. Ta façon de travailler sur ce projet

- **Un module à la fois.** Ne génère jamais l'application entière d'un coup.
- **Explique avant de coder** quand tu introduis un mécanisme nouveau (synchronisation,
  chiffrement, migrations). Je dois comprendre ce que j'intègre.
- **Écris les tests en même temps que le code**, pas après.
- **Signale les compromis** que tu fais et ce qui reste à traiter.
- **Ne masque pas les erreurs** : pas de `try/except` silencieux, pas de valeur par défaut
  qui cache un problème.
- **Ne rajoute pas de dépendance** sans le dire et sans justifier.
- Si une demande contredit ce fichier ou le cahier des charges, **dis-le avant d'agir**.

## 10. Sécurité — points de vigilance

- Aucun secret réel, aucune donnée client dans le code, les tests ou les exemples : données fictives uniquement.
- Le fichier `.env` n'est jamais versionné ; fournis un `.env.example`.
- Valide toutes les entrées côté serveur, y compris celles déjà validées côté interface.
- Le coffre-fort et l'authentification font l'objet d'une revue de sécurité dédiée avant mise en production.
