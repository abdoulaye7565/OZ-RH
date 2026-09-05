# Journal d'avancement

Suivi du lotissement défini dans `docs/CDC-SHEQ-001.docx` (chapitre 13) et dans
`PROMPTS_DEVELOPPEMENT.md`. Un module à la fois, chaque ligne cochée correspond à
un prompt terminé, testé et commité.

## LOT 0 — Fondations

- [x] 0.1 — Initialisation du dépôt (squelette backend/frontend, docker-compose, README)
- [x] 0.2 — Modèle de données (14 entités SQLAlchemy + migration Alembic initiale)
- [x] 0.3 — Authentification et rôles (JWT, argon2, matrice des droits)

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

### Détail — Prompt 0.2 (terminé le 2026-09-05)

Sources lues : chapitre 7 du CDC (dictionnaire, entier), chapitre 5 (spécifications
fonctionnelles, entier), chapitre 4 (rôles), et `docs/diagrammes/mcd.png` — le
chapitre 7.2 ne détaille que 8 des 14 entités ; les 6 autres (SITE, ACTION,
EVALUATION_SLAM, INSPECTION, DOCUMENT) ont été reconstituées depuis le MCD et les
sections fonctionnelles correspondantes. Complété par une lecture directe de
`docs/REG-SHEQ-001_Registre_des_Risques.xlsx` pour les valeurs réelles de
`categorie` (RISQUE) et les seuils de criticité, absents du CDC.

**Tableau récapitulatif**

| Table | Colonnes | Origine |
|---|---|---|
| utilisateur | 16 | dictionnaire 7.2.1 |
| site | 10 | reconstituée (MCD + 5.2.3) |
| risque | 20 | dictionnaire 7.2.2 |
| action | 17 | reconstituée (MCD + 5.2.5) |
| signalement | 21 | dictionnaire 7.2.3 |
| equipement | 17 | dictionnaire 7.2.4 |
| configuration | 19 | dictionnaire 7.2.5 |
| epi | 17 | dictionnaire 7.2.6 |
| permis | 18 | dictionnaire 7.2.7 (+ table d'association `permis_intervenants`) |
| secret | 13 | dictionnaire 7.2.8 |
| journal_acces | 8 | dictionnaire 7.2.8 |
| evaluation_slam | 12 | reconstituée (MCD + 5.2.2) |
| inspection | 14 | reconstituée (MCD + 5.3.1) |
| document | 18 | reconstituée (MCD + 5.3.5) |

16 tables SQL au total (14 entités + `permis_intervenants` + `alembic_version`).
Migration initiale : `alembic/versions/0ecd676d66b6_creation_des_14_entites_metier.py`,
testée en upgrade **et** downgrade sur SQLite.

**Points du dictionnaire interprétés — à valider avec le référent SHEQ/CDC :**

1. **PK `id` générique, pas `id_<entite>`.** Le prompt exige explicitement une
   classe de base commune portant une colonne `id` ; le dictionnaire (chapitre 7)
   nomme chaque PK `id_utilisateur`, `id_risque`, etc. Les deux sources se
   contredisent sur ce point précis — la classe de base commune l'emporte, comme
   demandé par le prompt lui-même.
2. **Rôle `referent_sheq` vs `referent`.** CDC chapitre 4/7.2.1 écrit `referent` ;
   CLAUDE.md (point 6, matrice des droits) écrit `referent_sheq`. Retenu :
   `referent_sheq`, car c'est la source qui détaille les permissions par rôle.
3. **JOURNAL_ACCES n'hérite pas de la classe de base commune.** Il n'a ni
   `modifie_le`, ni `modifie_par_id`, ni `archive` — leur seule présence
   suggérerait qu'une entrée peut être modifiée ou archivée, ce que la règle 4
   de CLAUDE.md interdit explicitement ("aucune route ne permet de le modifier ou
   de le supprimer, même pour un administrateur"). C'est l'écart le plus visible
   par rapport à "toutes les tables portent..." — assumé délibérément.
4. **`categorie` de RISQUE : 12 valeurs réelles, pas "dix" comme l'annonce le
   CDC.** Reprises telles quelles du registre Excel en service, avec deux
   libellés proches non harmonisés dans le classeur source ("Incendie" et
   "Incendie / Urgences") conservés séparément par fidélité à la donnée réelle.
   À trancher avec le référent SHEQ avant l'import prévu au prompt 4.1.
5. **`reference` de SIGNALEMENT et PERMIS rendue nullable**, alors que le
   dictionnaire la marque "Oui" (obligatoire). Nécessaire : ces références sont
   attribuées à la synchronisation, pas à la saisie hors ligne (CLAUDE.md règle 7)
   — une contrainte NOT NULL empêcherait toute création hors connexion.
6. **`intervenants` de PERMIS modélisé en table d'association** (many-to-many
   réel avec UTILISATEUR) plutôt qu'en liste JSON d'identifiants, pour garantir
   l'intégrité référentielle. Le dictionnaire le décrit comme type "Liste" sans
   trancher l'implémentation.
7. **EVALUATION_SLAM et INSPECTION stockent leurs sous-structures (étapes/points
   de contrôle, points de checklist) en JSON**, faute d'entités dédiées parmi les
   14 demandées. Fonctionnellement correct pour l'écriture/lecture, mais rend ces
   points impossibles à interroger individuellement côté SQL — à reconsidérer en
   tables séparées si le lot 2 (SLAM/permis, prompt 2.2) ou les checklists
   paramétrables (prompt 2.4) l'exigent.
8. **Aucun lien direct EVALUATION_SLAM → PERMIS dans le MCD fourni.** La règle de
   blocage "un intervenant n'a pas de SLAM en GO" devra donc chercher la
   évaluation la plus récente de l'intervenant plutôt que suivre une clé
   étrangère — la définition exacte de "la plus récente" (fenêtre de validité)
   reste à trancher au prompt 2.2, pas résolue ici.
9. **Cycle SITE ↔ UTILISATEUR résolu par `use_alter=True`** sur `cree_par_id`/
   `modifie_par_id` (avec convention de nommage explicite pour les contraintes
   générées). Sans ce report de contrainte, la création du schéma échouerait sur
   PostgreSQL (SQLite est plus permissif et n'aurait rien signalé).
10. **`type_mesure` (ACTION), `statut` (ACTION, DOCUMENT, INSPECTION),
    `confidentialite` (DOCUMENT), `type` (SITE)** : énumérations non données par
    le CDC, définies par déduction du texte fonctionnel — à confirmer.

**Vérifié en conditions réelles :** migration appliquée sur SQLite (upgrade ET
downgrade), 7 tests pytest passent, dont un test qui insère un utilisateur et un
site en exploitant réellement le cycle de clés étrangères, et un test qui vérifie
qu'une probabilité hors bornes (1-5) est rejetée par la contrainte CHECK.

### Détail — Prompt 0.3 (terminé le 2026-09-05)

Sources lues : chapitre 4 du CDC (utilisateurs et rôles) et point 6 de CLAUDE.md
(matrice des droits).

Implémenté : connexion (`POST /api/v1/auth/connexion`), rafraîchissement
(`POST /api/v1/auth/rafraichissement`), création d'utilisateur réservée à
l'administrateur (`POST /api/v1/auth/utilisateurs`), lecture du compte courant
(`GET /api/v1/auth/moi`) ; mots de passe hachés argon2 (passlib) ; JWT access
(15 min) + refresh (7 jours) avec un claim `type` qui empêche explicitement
qu'un jeton serve à la place de l'autre ; dépendances `get_current_user` et
`require_role(*roles)` (app/core/deps.py) ; matrice des droits centralisée dans
`app/core/permissions.py` ; journalisation des connexions réussies/échouées via
le logger applicatif `app.securite`, plus mise à jour de `derniere_connexion`.

**Compromis et écarts à signaler :**

1. **Pas de table de journal des connexions dédiée.** Les 14 entités ne prévoient
   pas d'entité pour ça (`JOURNAL_ACCES` est réservé au coffre-fort, chapitre
   7.2.8). Utilisé à la place : le champ `derniere_connexion` déjà présent au
   dictionnaire (7.2.1) + un log applicatif (`logger.info`/`logger.warning`,
   jamais le mot de passe). Si un historique complet et interrogeable des
   connexions est nécessaire (détection de tentatives suspectes, par exemple),
   une table dédiée devra être ajoutée explicitement — ce n'est pas ce qui est
   en place aujourd'hui.
2. **Refresh token sans révocation côté serveur.** Aucune table ne trace les
   refresh tokens émis : un jeton volé reste valable jusqu'à son expiration
   naturelle (7 jours), il n'existe pas de mécanisme de déconnexion qui
   l'invaliderait immédiatement. Accepté pour ce prompt (aucune table de
   session n'est demandée parmi les 14 entités) ; à reconsidérer explicitement
   si un écran de déconnexion ou de gestion des sessions est requis.
3. **Connexion en JSON français (`identifiant`/`mot_de_passe`), pas au format
   OAuth2 standard (`username`/`password`).** Cohérent avec le reste de l'API et
   le dictionnaire de données, mais casse l'auto-complétion du bouton
   "Authorize" de Swagger UI (qui poste un formulaire, pas du JSON). Pas
   bloquant : `/docs` reste utilisable en testant `/auth/connexion` directement
   puis en collant le jeton obtenu. À reconsidérer au prompt 5.3 (documentation
   API) si le confort de `/docs` devient gênant.
4. **`role_requis` de SECRET réutilise l'énumération `RoleUtilisateur`** (posé au
   prompt 0.2, confirmé ici) : la matrice des droits ne connaît donc qu'un seul
   jeu de rôles pour tout le système, cohérent avec le tableau du point 6 de
   CLAUDE.md.
5. **`Permissions` (app/core/permissions.py) ne contient qu'une seule entrée
   pour l'instant** (`GERER_UTILISATEURS`) : volontaire, pour ne pas deviner par
   avance les permissions de modules qui n'existent pas encore (lots 1 à 4).

**Vérifié en conditions réelles :** 24 tests pytest passent (7 précédents + 17
nouveaux), dont le cas de refus explicitement demandé par le prompt (un
technicien connecté qui tente `POST /auth/utilisateurs` reçoit 403), la
vérification qu'un refresh token ne permet pas d'accéder à `/auth/moi` et
réciproquement qu'un access token est refusé par `/auth/rafraichissement`, un
jeton expiré manuellement construit, un compte désactivé qui ne peut plus se
connecter, et le hachage argon2 du mot de passe stocké. Serveur démarré avec
`uvicorn`, 4 routes confirmées présentes dans le schéma OpenAPI.

**Le mécanisme du refresh token, expliqué :**

Un seul jeton, longue durée, poserait un dilemme sans issue : le rendre court
pour limiter les dégâts en cas de vol force à se reconnecter sans cesse (mauvaise
expérience terrain, justement là où la connexion est intermittente) ; le rendre
long pour le confort expose un jeton volé — via un appareil perdu, une capture
réseau, un log mal protégé — à un usage frauduleux pendant toute sa durée de vie,
sans aucun moyen de le renouveler à moindre risque entre-temps.

Deux jetons séparent ces deux besoins :
- **L'access token** est court (15 minutes ici) et voyage à chaque requête API —
  c'est le jeton le plus exposé, donc celui dont la fenêtre de nuisance en cas de
  vol doit être la plus étroite.
- **Le refresh token** est long (7 jours) mais ne sert qu'à une seule chose :
  obtenir un nouvel access token via `/auth/rafraichissement`. Il ne voyage donc
  qu'occasionnellement (pas à chaque requête métier), ce qui réduit fortement les
  occasions de l'intercepter.

Chaque jeton porte un claim `type` (`access` ou `refresh`) vérifié explicitement
des deux côtés : un refresh token présenté à `get_current_user` est rejeté, et un
access token présenté à `/auth/rafraichissement` l'est également (tests dédiés).
Sans cette distinction, un attaquant qui intercepte n'importe quel jeton pourrait
aussi bien s'en servir pour s'authentifier que pour en fabriquer de nouveaux à
volonté — ce qui viderait tout l'intérêt d'avoir deux jetons.

Limite actuelle, assumée et documentée ci-dessus : sans table de sessions, un
refresh token ne peut pas être révoqué avant son expiration naturelle. C'est un
compromis délibéré pour ce prompt, pas un oubli.
