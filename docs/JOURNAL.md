# Journal d'avancement

Suivi du lotissement défini dans `docs/CDC-SHEQ-001.docx` (chapitre 13) et dans
`PROMPTS_DEVELOPPEMENT.md`. Un module à la fois, chaque ligne cochée correspond à
un prompt terminé, testé et commité.

## LOT 0 — Fondations

- [x] 0.1 — Initialisation du dépôt (squelette backend/frontend, docker-compose, README)
- [x] 0.2 — Modèle de données (14 entités SQLAlchemy + migration Alembic initiale)
- [x] 0.3 — Authentification et rôles (JWT, argon2, matrice des droits)

## LOT 1 — MVP (signalements, actions, tableau de bord, hors connexion)

- [x] 1.1 — API des signalements
- [x] 1.2 — API du plan d'action
- [x] 1.3 — Interface mobile : saisie d'un signalement
- [ ] 1.4 — Mode hors connexion et synchronisation (stratégie présentée le 2026-09-05,
      en attente de validation — voir prompt d'appoint dans PROMPTS_DEVELOPPEMENT.md ;
      traité après le 1.5 à la demande explicite de l'utilisateur)
- [x] 1.5 — Tableau de bord
- [~] 1.6 — Recette du lot 1 (partielle : cas 11/13/14 couverts, cas 1/2/10
      explicitement `skip` — dépendent du prompt 1.4, non implémenté)

## LOT 2 — Travaux en hauteur

- [x] 2.1 — API des EPI
- [x] 2.2 — SLAM et permis, avec la règle de blocage
- [x] 2.3 — Interfaces SLAM et permis (hors connexion non traité, prompt 1.4 requis)
- [x] 2.4 — Inspections

## LOT 3 — Parc, configurations et coffre-fort

- [x] 3.1 — Parc d'équipements
- [x] 3.2 — Fiches de configuration par marque
- [x] 3.3 — Coffre-fort d'identifiants (conception présentée le 2026-09-06,
      validée par l'utilisateur le 2026-09-08 — voir détail dans "Chantier
      ouvert" plus bas)

## LOT 4 — Pilotage et modules complémentaires

- [x] 4.1 — Risques
- [x] 4.2 — Formations, audits et revues
- [x] 4.3 — Documents, visiteurs, déchets, satisfaction
- [x] 4.4 — Notifications

## LOT 5 — Finalisation

- [x] 5.1 — Génération des PDF
- [~] 5.2 — Sécurité et revue finale (rapport livré le 2026-09-07, classé par
      gravité ; consigne explicite « ne corrige rien avant validation » — les
      corrections listées restent en attente de l'accord de l'utilisateur)
- [x] 5.3 — Documentation et déploiement (terminé le 2026-09-07 ; a mis au jour
      un écart important entre backend et frontend, documenté plutôt que masqué
      — voir le détail ci-dessous)

## LOT 6 — Intelligence artificielle

> Gate du lot (chapitre 16.6 du CDC) explicitement non remplie : les lots 1-4 ne
> sont pas "en service" au sens propre (écart frontend/backend, prompt 5.3), et
> aucune validation budgétaire de la direction n'a eu lieu. Poursuite décidée
> explicitement par l'utilisateur le 2026-09-07, en connaissance de cause.

- [x] 6.1 — Socle technique de l'assistance (terminé le 2026-09-07 ; conception
      présentée et validée avant codage, comme demandé par le prompt)
- [x] 6.2 — Assistant documentaire (terminé le 2026-09-07 ; les 4 questions de
      test du prompt n'ont pas pu être posées à un vrai fournisseur — aucune
      clé API réelle dans cet environnement, voir le détail ci-dessous)
- [x] 6.4 — Pré-rédaction des rapports (terminé le 2026-09-07 ; 6.3 sauté une
      seconde fois par sélection directe de l'utilisateur, jugement propre
      cette fois — pas de dépendance technique identifiée entre 6.4 et 6.3,
      contrairement au premier saut 6.1→6.3 ; démonstration réelle sur les
      données de démonstration, voir le détail ci-dessous)

## Chantier ouvert — écrans manquants (hors plan initial)

> Constaté par l'utilisateur en testant l'application réellement (2026-09-07) :
> l'écart frontend/backend documenté au prompt 5.3 signifie concrètement que la
> plupart des modules n'ont aucun écran. Décision explicite de l'utilisateur :
> construire les écrans manquants, module par module, plutôt que de continuer
> la séquence de prompts. Référence visuelle : `docs/maquettes/` (les deux
> fichiers contiennent bien un écran, mobile et desktop, pour chacun des 14
> modules restants — jamais utilisés jusqu'ici).

- [x] EPI (mobile `/epi`, desktop `/gestion/epi`) — terminé le 2026-09-07
- [x] Risques (mobile `/risques`, desktop `/gestion/risques`) — terminé le
      2026-09-07
- [x] Actions (mobile `/actions`, desktop `/gestion/actions`) — terminé le
      2026-09-07 ; création limitée à une origine "risque" pour l'instant
      (voir compromis ci-dessous)
- [x] Ossature desktop refaite (`GestionLayout.vue`, barre latérale) —
      terminé le 2026-09-07, voir le détail ci-dessous
- [x] Parc d'équipements et fiches de configuration (mobile `/parc` +
      `/parc/:id`, desktop `/gestion/parc`, fiche desktop réutilise l'écran
      mobile) — terminé le 2026-09-07 ; formulaire de configuration limité à
      MikroTik pour l'instant (seule marque détaillée dans la maquette de
      référence)
- [x] Formations (mobile `/formations`, desktop `/gestion/formations`) —
      terminé le 2026-09-07 ; passage de quiz mobile uniquement (action
      individuelle, pas une vue de pilotage), testé avec les 10 vraies
      questions du référentiel FOR-SHEQ-015
- [x] Audits et revues de direction (mobile `/audits`, desktop
      `/gestion/audits`) — terminé le 2026-09-07 ; les deux modules
      regroupés en un seul écran (comme dans la barre latérale), testé avec
      les 22 vraies exigences FOR-SHEQ-017 réparties sur 6 chapitres
- [x] Documents (mobile `/documents`, desktop `/gestion/documents`) —
      terminé le 2026-09-07 ; cycle complet brouillon → approbation →
      vigueur → accusé de lecture testé en direct
- [x] Visiteurs (mobile `/visiteurs`, desktop `/gestion/visiteurs`) — terminé
      le 2026-09-07 ; a aussi révélé et corrigé un bug transverse
      d'affichage des erreurs de validation (voir détail ci-dessous)
- [x] Déchets (mobile `/dechets`, desktop `/gestion/dechets`) — terminé le
      2026-09-07 ; "Incidents environnement" (4e indicateur de la maquette
      desktop) affiché à 0 fixe, aucune entité dédiée côté backend
- [x] Satisfaction (questionnaire public `/satisfaction/:jeton` sans compte,
      pilotage desktop `/gestion/satisfaction`) — terminé le 2026-09-07 ;
      nouvelle route `GET /satisfaction/reponses` ajoutée (agrégation moyenne
      absente de l'API existante) ; a aussi révélé et corrigé un vrai bug
      Pinia (voir détail ci-dessous)
- [x] Notifications (cloche + panneau, composant transverse
      `NotificationsCloche.vue`, monté dans l'en-tête mobile de Signalements
      et dans l'en-tête desktop `GestionLayout.vue`) — terminé le 2026-09-07 ;
      voir détail ci-dessous (aucune des deux maquettes ne contient d'écran
      dédié, seulement le bouton d'en-tête)
- [x] Permis / SLAM & permis (mobile `/permis`, desktop `/gestion/permis`) —
      terminé le 2026-09-07 ; nouvelle route `GET /slam` (liste complète,
      réservée aux rôles de pilotage) ajoutée — voir détail ci-dessous
- [x] Coffre-fort (mobile `/coffre-fort`, desktop `/gestion/coffre-fort`) —
      terminé le 2026-09-08, conception validée par l'utilisateur avant
      codage (module sensible, chiffrement) — voir détail ci-dessous
- [x] Gestion des utilisateurs (écran admin desktop `/gestion/utilisateurs`,
      réservé au rôle administrateur) — terminé le 2026-09-07 ; nouvelles
      routes `POST /auth/utilisateurs/{id}/desactiver` et `.../activer`
      ajoutées (lacune signalée au prompt 5.2, comblée ici) — voir détail
      ci-dessous

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

### Détail — Prompt 1.1 (terminé le 2026-09-05)

Sources lues : section 5.2.1 du CDC (module Signalements et incidents, entière)
et point 7 de CLAUDE.md (règles métier critiques).

Implémenté : `POST /signalements` (création, multipart/form-data pour les
photos), `GET /signalements` (liste avec filtres statut/site/type/période),
`GET /signalements/{id}`, `PATCH /signalements/{id}/statut` (transitions
contrôlées), `POST /signalements/{id}/archiver`. Aucune route DELETE.

**Compromis et écarts à signaler :**

1. **Visibilité restreinte par rôle, ajoutée sans être explicitement demandée par
   le prompt 1.1** : technicien et collaborateur ne voient (liste et lecture)
   que leurs propres signalements non anonymes, conformément au chapitre 4 du
   CDC ("lecture de ses propres saisies" pour le technicien) et à la section
   5.2.1 ("Consultation : responsables et direction"). Sans cette règle, un
   technicien aurait pu lister les signalements de tout le monde via un simple
   `GET /signalements`, ce qui aurait été un vrai trou de sécurité au regard du
   principe du moindre privilège (CLAUDE.md point 6).
2. **`GET /signalements/{id}` renvoie 404, pas 403**, quand l'appelant n'a pas le
   droit de voir un signalement précis — pour ne pas confirmer son existence à
   quelqu'un qui n'y a pas droit (cohérent avec l'esprit de l'anonymat, mais pas
   une règle explicitement énoncée par le CDC).
3. **Workflow : `nouveau` → `clôturé` directement est refusé.** Le CDC autorise
   "clôturer un signalement, avec ou sans action", ce qui pourrait se lire comme
   une clôture possible dès `nouveau`. Interprété plus strictement : le
   signalement doit d'abord passer par `en_analyse` (le workflow décrit est
   "nouveau → en analyse → actions définies → clôturé", séquentiel). À confirmer
   avec le référent SHEQ si cette lecture est trop stricte pour l'usage réel.
4. **Notification du référent SHEQ = ligne de log applicatif, pas un
   enregistrement en base.** Le prompt dit littéralement "simple enregistrement
   en base" ; aucune entité NOTIFICATION n'existe parmi les 14 (le service de
   notifications complet est le lot 4.4). Créer une table dédiée maintenant
   risquerait d'être incompatible avec sa conception définitive au lot 4.4 — à
   corriger quand ce lot sera traité, pas avant.
5. **Limites de photos non données par le CDC, choisies par défaut** : 5 Mo par
   photo, JPEG/PNG/WebP uniquement. Le CDC dit seulement "5 maximum" et "contrôle
   du type et de la taille" sans chiffrer ces seuils.
6. **Nouvelle variable de configuration `STORAGE_DIR`** (`app/core/config.py`,
   `.env.example`) : nécessaire pour le stockage des photos hors base ; absente
   de CLAUDE.md, ajoutée avec un défaut (`./storage`) déjà anticipé dans
   `.gitignore` depuis le prompt 0.1.
7. **Bug trouvé et corrigé pendant la vérification manuelle, pas par les tests
   automatisés** : les chemins de photos étaient enregistrés avec des
   antislashs sous Windows (`Path.__str__`), ce qui les aurait rendus invalides
   une fois l'application déployée sous Linux (Docker, conforme à CLAUDE.md).
   Corrigé avec `.as_posix()`. Les tests pytest ne l'avaient pas détecté car ils
   tournent sur la même machine que l'écriture ; seul un test live avec un vrai
   fichier via `curl` l'a révélé — leçon pour la suite : les tests
   automatisés ne remplacent pas toujours une vérification en conditions
   réelles, en particulier pour tout ce qui touche au système de fichiers.

**Vérifié en conditions réelles :** 41 tests pytest passent (24 précédents + 17
nouveaux, dont le test explicitement demandé sur l'absence de toute trace d'un
signalement anonyme — y compris `cree_par_id`, lu en SQL brut, pas seulement
dans la réponse JSON). Serveur démarré avec `uvicorn` sur une base isolée,
séquence `SIG-2026-001` puis `SIG-2026-002` confirmée par deux créations
successives via `curl`, upload réel d'un fichier JPEG vérifié sur disque.

### Détail — Prompt 1.2 (terminé le 2026-09-05)

Source lue : section 5.2.5 du CDC (module Risques et plan d'action, partie
actions).

Implémenté : `POST /actions`, `GET /actions` (filtres statut/responsable_id/
en_retard), `GET /actions/{id}`, `PATCH /actions/{id}/avancement`,
`PATCH /actions/{id}/statut`, `GET /actions/synthese`.

**Compromis et écarts à signaler :**

1. **`audit_id` absent** : le prompt demande de rattacher une action "à un
   risque, un signalement, une inspection **ou un audit**", mais AUDIT ne fait
   pas partie des 14 entités (module Audits prévu au lot 4.2). Seules les trois
   origines déjà modélisées sont acceptées ; `audit_id` s'ajoutera par migration
   quand le module Audits existera — déjà anticipé dans le commentaire du
   modèle `Action` depuis le prompt 0.2.
2. **Exactement une origine exigée à la création** (ni zéro, ni deux) : validé
   par un `model_validator` Pydantic, renvoie 422. Le CDC ne le dit pas
   explicitement mais une action sans origine ni traçable à deux origines à la
   fois n'aurait pas de sens dans le registre.
3. **« En retard » est une propriété calculée** (`Action.en_retard`, jamais
   stockée) : `statut != clôturée ET échéance dépassée`. Choix déjà annoncé dans
   `docs/JOURNAL.md` au prompt 0.2. Testé explicitement : une action clôturée
   n'est plus jamais "en retard" même après son échéance.
4. **`taux_avancement_global` = clôturées / total**, PAS la moyenne des
   avancements individuels — formule exacte du chapitre 7.3.2 du CDC ("Avancement
   du plan d'action : nombre d'actions clôturées rapporté au nombre total
   d'actions"), retrouvée lors du prompt 0.2 et réappliquée ici sans
   réinterprétation.
5. **Autorisation à deux niveaux, non demandée explicitement mais nécessaire** :
   création et pilotage global réservés à référent SHEQ/administrateur (section
   5.2.5, "Rédaction et mise à jour : référent SHEQ"), MAIS le responsable
   désigné d'une action précise peut mettre à jour son propre avancement et la
   clôturer — c'est lui qui l'exécute sur le terrain. Sans cette exception, un
   technicien responsable d'une action n'aurait eu aucun moyen de rendre compte
   de son avancement.
6. **OUVERTE → CLOTURÉE directement autorisé** (pas besoin de transiter par
   EN_COURS), contrairement au workflow plus strict des signalements — une
   action rapide n'a pas besoin d'un état intermédiaire. Assumé, non stipulé
   explicitement par le CDC.
7. **Consultation ouverte à tout le personnel authentifié**, sans restriction de
   visibilité par rôle — contrairement aux signalements où technicien/
   collaborateur ne voient que leurs propres saisies. Cohérent avec la section
   5.2.5 ("Consultation : ensemble du personnel").

**Vérifié en conditions réelles :** 56 tests pytest passent (41 précédents + 15
nouveaux), dont le cas de refus explicitement demandé par le prompt (clôture
sans indicateur → 409). Serveur démarré avec `uvicorn` sur une base isolée,
création d'une action rattachée à un risque réel confirmée par `curl`, refus de
clôture sans indicateur confirmé en direct (409), synthèse vérifiée après une
clôture (`taux_avancement_global` et compteurs par statut corrects).

### Détail — Prompt 1.3 (terminé le 2026-09-05)

Source lue : `docs/maquettes/Maquettes_SHEQ_Management_v2.html`, écrans
`#s-newsig` et `#s-siglist` (figures A.3 et A.4 du CDC).

Implémenté : `NouveauSignalementView.vue`, `SignalementsView.vue`, store Pinia
`stores/signalements.js`, composants `Icone.vue`/`IconeSprite.vue` (icônes SVG
au trait reprises de la maquette) et `BandeauReseau.vue`, classes CSS des
composants de la maquette ajoutées à `style.css` (au-delà des seuls jetons de
couleur posés au prompt 0.1).

**Écarts et compromis à signaler — plusieurs sont substantiels :**

1. **Écran de connexion ajouté, non demandé par ce prompt.** Aucun prompt du
   lotissement ne couvre la connexion avant celui-ci ; sans elle, les deux
   écrans demandés ici sont impossibles à exercer (l'API exige un jeton).
   Ajout minimal : `ConnexionView.vue`, `stores/auth.js`, garde de route dans
   `router/index.js`. Cette question mérite d'être posée explicitement : faut-il
   un prompt dédié à l'authentification frontend avant de continuer le lot 1 ?
2. **Le formulaire n'affiche que 3 des 5 types de signalement** de l'énumération
   backend (`situation_dangereuse`, `presque_accident`, `anomalie`), à
   l'identique de la maquette — qui n'affiche pas `incident` ni `accident`.
   Respecté à la lettre ("respecte-les : contenu…"), mais cela signifie qu'un
   accident du travail ne peut pas être déclaré depuis cet écran. À trancher
   avec le référent SHEQ : la maquette est-elle incomplète, ou ces
   déclarations passent-elles par un autre circuit non encore maquetté ?
   **Tranché le 2026-09-05 : on garde 3 types**, fidèle à la maquette ; incident
   et accident seront traités plus tard si un circuit dédié s'avère nécessaire.
3. **`site_id` n'est pas un champ du formulaire** (la maquette n'en a pas) :
   rempli automatiquement avec le site de rattachement du compte connecté. Un
   technicien intervenant sur le site d'un client différent du sien ne peut
   donc pas le désigner ici — seul le champ texte libre "Lieu" existe pour ça.
4. **`date_constat` n'est pas un champ non plus** : fixée à l'instant de
   l'envoi, faute de sélecteur dans la maquette.
5. **Bandeau hors connexion du formulaire reformulé, PAS repris mot pour mot.**
   La maquette affirme que le signalement est "conservé sur l'appareil" et
   "part automatiquement à la reconnexion" hors ligne — or ce mécanisme
   (prompt 1.4) n'existe pas encore : le garder tel quel aurait promis à
   l'utilisateur une capacité que l'application n'a pas. Remplacé par un
   message qui dit explicitement que le mode hors connexion arrive au prompt
   suivant et qu'une connexion est nécessaire pour l'instant. Choix délibéré :
   honnêteté sur l'état réel plutôt que fidélité littérale au texte de la
   maquette sur ce point précis.
6. **Barre d'onglets réduite à Accueil/Signaux** : les trois autres destinations
   de la maquette (SLAM, Parc, Tableau de bord) n'ont pas encore d'écran (lots
   2, 3, 1.5) — omises plutôt que transformées en boutons qui ne mènent nulle
   part.
7. **L'auteur d'un signalement s'affiche "Utilisateur #12"**, pas son nom : l'API
   (`SignalementSortie`) ne renvoie que `auteur_id`, jamais nom/prénom. Pas
   corrigible côté frontend sans soit une jointure ajoutée à l'API, soit un
   appel supplémentaire par ligne (mauvaise pratique, N+1) — à traiter quand ce
   confort d'affichage sera jugé nécessaire.
8. **Validation client minimale** (lieu et description non vides) : la
   validation serveur reste seule autorité, toute erreur 422 qu'elle renvoie
   est affichée telle quelle, jamais présumée redondante avec la validation
   client.

**Vérifié en conditions réelles, dans un vrai navigateur (pas seulement à la
lecture du code) :** parcours complet automatisé — redirection vers /connexion
si non authentifié, connexion réussie, écran de liste (5 filtres affichés),
navigation vers le formulaire, refus d'envoi avec champs vides (2 messages
d'erreur affichés), envoi réussi avec redirection et apparition immédiate de la
ligne créée dans la liste. Zéro erreur console, zéro requête échouée. Build de
production (`npm run build`) propre.

**Un vrai bug d'infrastructure trouvé et corrigé pendant cette vérification,
sans lien avec le code de ce prompt** : le serveur backend de démonstration
(port 8000) tournait depuis le prompt 0.3 sans jamais avoir été redémarré — il
répondait donc 404 sur `/signalements` et `/actions`, absents du code chargé en
mémoire à son démarrage. Redémarré avec `--reload` pour que ça ne se reproduise
plus. Sans le test en navigateur réel, ce décalage silencieux serait resté
invisible : les tests pytest et les vérifications `curl` sur bases isolées
avaient tous été faits sur des instances fraîches, jamais sur le serveur de
démo lui-même.

### Détail — Prompt 1.5 (terminé le 2026-09-05)

Sources lues : section 5.4 du CDC (tableau de bord), maquettes desktop
(`#p-dash`, figure A.24) et mobile (`#s-tdb`, figure A.10).

**Backend** : `GET /api/v1/tableau-de-bord` (filtres `date_debut`, `date_fin`,
`site_id`), agrégations SQL uniquement (`GROUP BY`/`COUNT`, pas de chargement
de table en Python). `action_service.calculer_synthese` refactorisé à cette
occasion : chargeait toutes les lignes en mémoire depuis le prompt 1.2, remplacé
par deux requêtes agrégées. Nouvelle fonction `action_service.echeances_proches`.

**Requêtes générées pour l'endpoint principal (capturées et vérifiées) :**
6 `SELECT`, aucune par ligne (pas de N+1) : total de la période (COUNT),
histogramme mensuel (`GROUP BY EXTRACT(year)/EXTRACT(month)` — traduit en
`STRFTIME` sur SQLite, en `EXTRACT`/`date_part` sur PostgreSQL sans code
spécifique à un moteur), liste "à traiter" (une requête, limite 10), répartition
des actions par statut (`GROUP BY`), comptage des actions en retard (`COUNT`
avec `WHERE`), liste des échéances proches (une requête, limite 10).

**Frontend** : deux vues distinctes plutôt qu'une seule vue responsive —
`TableauBordMobileView.vue` et `TableauBordDesktopView.vue` (route
`/gestion/tableau-de-bord`, amorce du préfixe "interface de gestion" du CDC
11.1). CSS desktop ajoutée à `style.css` (`.mets`, `.grid2`, `.card .ch/.cb`,
tableaux, histogramme `.bars`/`.bcol`).

**Écarts et compromis à signaler — importants :**

1. **La plupart des indicateurs du chapitre 5.4 du CDC ne sont pas
   calculables** : sur les quatre familles prévues (sécurité et santé,
   prévention, environnement et qualité, échéances), seuls les modules
   Signalements et Actions existent. EPI (lot 2.1), inspections (lot 2.4),
   formations/documents/environnement/satisfaction (lot 4), coffre-fort
   (lot 3.3) sont listés dans `modules_non_disponibles` plutôt que simulés.
2. **Les 4 tuiles de tête ne sont PAS celles de la maquette.** La maquette
   affiche accidents avec arrêt / signalements / EPI à vérifier / conformité —
   3 de ces 4 dépendent de modules absents. Remplacées par : signalements de la
   période, signalements à traiter, avancement du plan d'action, actions en
   retard — les 4 seuls indicateurs réellement calculables aujourd'hui. Écart
   délibéré, dans la continuité du choix fait au prompt 1.3 (bandeau hors
   connexion reformulé) : ne jamais afficher un chiffre qui n'est pas
   réellement calculé.
3. **Le filtre `site_id` ne s'applique pleinement qu'aux signalements.**
   RISQUE et ACTION n'ont pas de site direct dans le modèle de données (posé
   au prompt 0.2) ; pour les actions, le filtre ne fonctionne que via la
   jointure `Action.signalement_id -> Signalement.site_id` — les actions
   issues d'un risque ou d'une inspection ne sont donc jamais comptées quand ce
   filtre est actif. Limite structurelle du modèle de données, pas un oubli de
   ce prompt.
4. **Deux vues distinctes (mobile/desktop), pas une seule vue responsive.** Les
   deux maquettes ont des systèmes de classes CSS différents et des contenus
   différents (le desktop ajoute deux tableaux absents du mobile) : les
   respecter fidèlement l'une et l'autre semblait plus honnête que de forcer un
   compromis hybride.
5. **Barre latérale desktop complète non reprise** : remplacée par un bandeau
   simple avec un seul lien (Signalements). Sera étoffée quand d'autres pages
   desktop existeront.
6. **Export PDF non implémenté** (bouton absent) : prévu au prompt 5.1.

**Bug réel trouvé et corrigé pendant la vérification visuelle en navigateur,
pas par les tests automatisés** : collision de nom de classe CSS — `.hd` était
déjà utilisée par l'en-tête plein écran (fond navy) des vues mobiles ; réutilisée
telle quelle pour l'en-tête d'une tuile métrique desktop, la tuile héritait du
fond navy et du padding de l'en-tête mobile. Invisible dans le code, visible
uniquement à l'écran — corrigé en renommant la classe desktop en `.met-hd`.
Deuxième leçon du même type qu'au prompt 1.3 : les vérifications visuelles en
navigateur réel trouvent des classes de bugs qu'aucun test automatisé ne peut
détecter.

**Un deuxième problème d'infrastructure trouvé en vérifiant** : plusieurs
processus `uvicorn --reload` empilés au fil des prompts précédents se
disputaient le port 8000, l'un d'eux servant du code obsolète (404 sur
`/tableau-de-bord` alors que le code source, vérifié par import Python direct,
était correct). Assaini : tous les processus arrêtés, un seul relancé sans
`--reload` pour cette session de vérification.

**Vérifié en conditions réelles :** 64 tests pytest passent (56 précédents + 8
nouveaux). Requêtes SQL de l'endpoint principal capturées et affichées (voir
ci-dessus). Les deux vues testées dans un vrai navigateur avec connexion réelle
au backend : 4 tuiles métriques et 2 tableaux présents côté desktop, 4 tuiles
et 2 cartes côté mobile, zéro erreur console, captures d'écran comparées aux
maquettes.

### Détail — Prompt 1.6 (terminé partiellement le 2026-09-05)

Source lue : chapitre 14 du CDC (recette et critères d'acceptation), tableau 8
entier (14 cas de test).

**Blocage structurel signalé avant d'écrire du code** : les cas 1, 2 et 10 du
tableau 8 testent tous le mécanisme hors connexion — exactement ce que couvre
le prompt 1.4, jamais implémenté (stratégie proposée le 2026-09-05, en attente
de validation). Écrire des tests qui prétendraient vérifier une synchronisation,
une numérotation différée ou une résolution de conflit inexistantes aurait
menti sur l'état du projet. Ces trois cas sont donc explicitement marqués
`pytest.mark.skip` avec le motif exact, dans `tests/test_recette_lot1.py` —
visibles à chaque exécution de la suite (`3 skipped`), pas seulement
documentés en prose ici.

**Cas réellement testés** :
- **Cas 11** (tableau de bord sans ressaisie) : un nouveau signalement et une
  action clôturée se reflètent immédiatement dans `/tableau-de-bord`, sans
  action manuelle supplémentaire.
- **Cas 13** (historique complet) — testé PARTIELLEMENT, limite documentée
  explicitement dans un test dédié (`test_cas_13_limite_pas_d_historique_complet_des_transitions`) :
  l'API ne restitue que l'état courant (dernière modification), pas la liste
  chronologique de toutes les opérations passées. Une vraie restitution
  "de toutes les opérations avec auteur et horodatage" demanderait une table
  d'historique dédiée, qui n'existe pour aucune entité (seul JOURNAL_ACCES
  existe, réservé au coffre-fort). **Bug réel corrigé à cette occasion** :
  `modifie_par_id` n'était renseigné par AUCUN service (signalements ni
  actions) depuis sa création au prompt 0.2 — une modification de statut ne
  traçait donc jamais qui l'avait faite, uniquement quand (`modifie_le`,
  auto-géré par la base). Corrigé dans `signalement_service.py` et
  `action_service.py` ; `cree_le`/`cree_par_id`/`modifie_le`/`modifie_par_id`
  également ajoutés à `SignalementSortie` et `ActionSortie`, absents de ces
  schémas depuis leur création (prompts 1.1/1.2) alors que les colonnes
  existaient déjà en base.
- **Cas 14** (refus de toute suppression) : confirmé sur signalements, actions
  et utilisateurs (404, pas 405, pour ce dernier : aucune route par
  identifiant n'existe du tout) ; l'archivage reste la seule voie.

**Vérifié en conditions réelles :** 74 tests pytest passent, 3 skippés avec
motif (13 nouveaux : 10 réussis + 3 skip). Correction de `modifie_par_id`
vérifiée en direct sur le serveur de démo (`null` avant tout changement de
statut, renseigné avec l'identifiant de l'agent après).

---

## Bilan du lot 1 (MVP)

**Terminé et testé** :
- Authentification JWT (access + refresh), matrice des droits, journalisation
  des connexions (0.3)
- API Signalements complète : création avec photos, workflow, anonymat
  garanti jusqu'en base brute, visibilité restreinte par rôle (1.1)
- API Actions complète : origine unique (risque/signalement/inspection),
  avancement, clôture bloquée sans indicateur, synthèse agrégée en SQL (1.2)
- Interface mobile Signalements : saisie et liste, fidèles aux maquettes,
  validation client sans remplacer la validation serveur (1.3)
- Tableau de bord (mobile et desktop) : agrégations SQL sans N+1, filtres
  période/site, honnête sur les indicateurs non calculables (1.5)
- Traçabilité auteur+horodatage sur création ET modification, corrigée pour
  couvrir réellement les deux (1.6)

**Ce qui reste — le plus important d'abord** :
1. **Le mode hors connexion lui-même (prompt 1.4) n'existe pas.** C'est le
   risque numéro un du projet selon le chapitre 15 du CDC (coté 4×4, le plus
   élevé avec la faille coffre-fort), et c'est la pièce manquante qui bloque
   la moitié des cas de recette du lot 1. Une stratégie complète a été
   présentée (file d'attente IndexedDB queue-first même en ligne, idempotence
   par UUID client, résolution de conflit à deux choix, `vite-plugin-pwa`)
   mais reste sans validation. **Le lot 1 ne peut pas être considéré terminé
   sans ce prompt.**
2. Écran de connexion actuel minimal (ajouté par nécessité au 1.3), sans
   gestion de session robuste (pas de rafraîchissement automatique du jeton
   côté frontend, pas de déconnexion).
3. Export PDF (cas de recette 12, prompt 5.1) — non demandé avant le lot 5,
   mentionné ici pour mémoire.
4. Historique complet des opérations (cas 13, partie non couverte) — nécessite
   une décision explicite : ajouter une table de journal des transitions, ou
   accepter que seul l'état courant soit restitué.

**Compromis assumés à relire avant la revue du lot** (détail complet dans les
sections ci-dessus, prompt par prompt) :
- 5 types de signalement affichés sur les 6 possibles côté formulaire (fidélité
  à la maquette, confirmée par l'utilisateur le 2026-09-05)
- `site_id` du signalement auto-rempli depuis le compte connecté, pas de
  sélecteur dans la maquette
- Le filtre site du tableau de bord ne s'applique pleinement qu'aux
  signalements (RISQUE et ACTION n'ont pas de site direct dans le modèle)
- Notification du référent SHEQ = log applicatif, pas un enregistrement
  persistant (aucune entité NOTIFICATION avant le lot 4.4)
- Pas de révocation serveur du refresh token (aucune table de session)

## LOT 2 — Travaux en hauteur

### Détail — Prompt 2.1 (terminé le 2026-09-05)

Sources lues : section 5.3.2 du CDC (module EPI) et règle 6 du point 7 de
CLAUDE.md.

Implémenté : `POST /epi` (numérotation automatique), `GET /epi` (filtres
type/statut/porteur_id), `GET /epi/verifications-dues` (horizon 30 jours par
défaut), `GET /epi/{id}`, `PATCH /epi/{id}/affectation`,
`POST /epi/{id}/verification-periodique`,
`POST /epi/{id}/verification-avant-utilisation`, `POST /epi/{id}/retirer`,
`POST /epi/{id}/reformer`. Nouvelle propriété calculée `Epi.est_conforme`
(chapitre 7.3.2 du CDC), distincte du champ `statut` stocké — servira à la
règle de blocage des permis (lot 2.2).

**Compromis et écarts à signaler :**

1. **Nouvelle dépendance : `python-dateutil`.** Nécessaire pour ajouter
   12 mois calendaires exacts (`relativedelta`) plutôt qu'une approximation à
   365 jours qui dérive avec les années bissextiles — direct sur une échéance
   réglementaire de sécurité, pas un détail cosmétique.
2. **Lettres de numérotation pour 3 des 6 types d'EPI, interprétées.** Le
   dictionnaire (chapitre 7.3.1) ne donne H/L/C que pour harnais/longe/casque ;
   antichute mobile, connecteur et ligne de vie ont reçu A/K/V par déduction,
   à confirmer avec le référent SHEQ.
3. **Numérotation en séquence globale, pas par lettre** : l'exemple du prompt
   ("H-001, L-002, C-003") attribue des numéros consécutifs à des types
   différents plutôt que de recommencer à 001 pour chaque lettre — interprété
   à la lettre de cet exemple.
4. **`prochaine_verification` amorcée dès la création** (date de mise en
   service + 12 mois), avant toute vérification réelle : le dictionnaire ne
   donne la formule qu'après une vérification effective ; sans cette amorce,
   un EPI neuf jamais vérifié n'aurait pas d'échéance et serait conforme par
   défaut indéfiniment.
5. **Colonne `motif_reforme` ajoutée**, absente du dictionnaire (7.2.6) : sans
   elle, le motif de réforme (« a arrêté une chute ») envoyé par l'API aurait
   été accepté puis silencieusement perdu. À l'inverse, le motif de simple
   retrait n'a PAS été persisté (champ retiré du schéma d'entrée) : le CDC
   n'insiste pas sur sa traçabilité comme il le fait pour la réforme.
6. **Vérification "avant utilisation" ne laisse aucune trace si elle est
   conforme** — seul un échec a un effet persistant (passage à "à vérifier").
   Même limite que le cas de recette 13 (prompt 1.6) : aucune table
   d'historique des vérifications n'existe parmi les 14 entités.
7. **`est_conforme` distinct du `statut` stocké**, et volontairement plus
   strict que prévu au premier jet : un bug a été trouvé par les tests
   eux-mêmes pendant l'écriture de ce prompt — la version initiale ne
   considérait "à vérifier" comme non conforme que si la date était en plus
   dépassée, ratant le cas où une vérification vient d'échouer alors que
   l'échéance calendaire, elle, est repoussée à 12 mois. Corrigé : seul
   `EN_SERVICE` est conforme, la date dépassée reste vérifiée en plus (pour le
   cas où `statut` serait resté EN_SERVICE en base après une échéance dépassée,
   faute de tâche planifiée qui le resynchronise — le lot 4.4 n'existe pas
   encore).

**Vérifié en conditions réelles :** 88 tests pytest passent, 3 toujours
skippés (1.4). Migration testée en upgrade/downgrade/upgrade. Sur le serveur
de démo redémarré à neuf : création d'un EPI, réforme avec motif persisté
confirmé dans la réponse, puis 409 confirmé sur une tentative de retrait après
réforme.

### Détail — Prompt 2.2 (terminé le 2026-09-06)

Sources lues : section 5.2.2 du CDC (module Travaux en hauteur), règle 1 du
point 7 de CLAUDE.md, et `docs/diagrammes/sequence.png` (regardé avant tout
code, comme demandé). Les 4 étapes SLAM et leurs 16 points ont été repris
littéralement du script de la maquette mobile (`const S=[...]`,
Maquettes_SHEQ_Management_v2.html), pas inventés — voir
`app/models/slam_referentiel.py`.

**Ce prompt est backend uniquement** : l'interface SLAM/permis est un prompt
séparé (2.3).

**LA RÈGLE CENTRALE** vit exclusivement dans
`app/services/regle_blocage_permis.py`, un fichier dédié à une seule fonction
(`evaluer_controles`), appelée à la fois à la création ET ré-exécutée à chaque
tentative de validation — jamais mise en cache. C'est cette relecture
systématique qui rend la règle impossible à contourner : un test dédié
(`test_impossible_de_contourner_en_validant_apres_coup`) dégrade un EPI
*entre* la demande et la validation et vérifie que le blocage s'applique
quand même.

**Découverte importante en lisant le diagramme de séquence** : il montre que
même un permis automatiquement bloqué est **persisté** (avec référence,
visible du responsable), pas rejeté sans trace — cohérent avec le statut
`bloqué` déjà présent dans le dictionnaire depuis le prompt 0.2. Un permis est
donc toujours créé à la demande (statut `demande` ou `bloqué` selon les
contrôles), jamais refusé silencieusement.

**Compromis et écarts à signaler :**

1. **`surveillant_id` rendu nullable** (posé NOT NULL au 0.2) : sinon "aucun
   surveillant désigné" ne pourrait jamais être une des quatre causes de
   blocage évaluées ensemble — ce serait une erreur de validation Pydantic
   avant même d'atteindre le service, pas un motif explicite. Migration
   testée en upgrade/downgrade avec `batch_alter_table` (SQLite ne supporte
   pas ALTER COLUMN directement).
2. **Fenêtre de validité du SLAM résolue** (point ouvert depuis le 0.2) : un
   intervenant doit avoir un GO daté du **même jour calendaire** que le début
   du créneau du permis. Un GO d'hier ne couvre pas une montée aujourd'hui —
   testé explicitement. À confirmer avec le référent SHEQ si la réalité du
   terrain est plus nuancée (plusieurs permis le même jour, décalage horaire
   nuit/matin…).
3. **Incohérence trouvée entre deux sources de référence, non résolue en
   silence** : la maquette mobile SLAM liste "Le permis de travail est validé"
   comme point de contrôle de l'étape 1 (S'arrêter), ce qui suggère SLAM
   *après* permis — alors que la règle 1 de CLAUDE.md et le diagramme de
   séquence (lecture des évaluations SLAM avant création du permis) impliquent
   l'inverse. Résolu en faveur de la règle et du diagramme (sources plus
   autoritatives qu'un unique point de texte UI) : SLAM est vérifié comme
   pré-condition du permis. Le texte du point de contrôle est repris tel quel
   dans le référentiel (fidélité à la maquette), mais aucune vérification
   serveur ne porte sur CE point précis individuellement — seul le résultat
   global (GO/NO_GO) compte pour la règle de blocage.
4. **"Étape suivante impossible sans tout valider" traduit en règle serveur
   équivalente, pas identique** : l'évaluation est soumise en un seul envoi
   (mobile hors connexion, pas d'échange par étape), donc le serveur valide
   "impossible de déclarer GO si un seul point sur 16 n'est pas coché" plutôt
   que de contrôler une progression écran par écran, qui reste une
   responsabilité du client (prompt 2.3).
5. **Notifications** (responsable à la demande, intervenant à la délivrance,
   responsable au NO GO) = logs applicatifs, même limite que les prompts 1.1
   et 2.1 — le service de notifications persistant est le lot 4.4.
6. **Réponse HTTP du cœur de la règle non-uniforme avec le reste de l'API** :
   `POST /permis/{id}/valider` renvoie 409 avec `detail` structuré
   (`{message, motifs}`) plutôt qu'une simple chaîne comme les autres 409 du
   projet — nécessaire pour transmettre plusieurs motifs cumulés lisiblement,
   à harmoniser si d'autres endpoints ont un jour le même besoin.

**Vérifié en conditions réelles :** 117 tests pytest passent (88 précédents +
29 nouveaux), 3 toujours skippés (1.4). La règle centrale a sa propre suite
(9 tests : cas nominal + une cause par condition, plus une cause supplémentaire
EPI réformé, plus le cumul de plusieurs causes). Sur le serveur de démo
redémarré à neuf : un permis avec EPI conforme + SLAM GO + surveillant valide
est créé `demande` puis délivré ; un second permis sans surveillant est
immédiatement `bloqué` avec le motif exact affiché en clair.

### Détail — Prompt 2.3 (terminé le 2026-09-06)

Sources lues : figures A.5, A.6 et A.30 (renvoyées vers les écrans réels des
maquettes : `#s-slam` et `#s-permis` du fichier mobile — A.30, desktop, n'a
pas de bullet de livrable propre dans ce prompt, seulement citée en lecture,
donc pas construite ici).

**Blocage signalé avant de commencer** : ce prompt demande explicitement de
"réutiliser le mécanisme du lot 1" pour le hors connexion — mécanisme qui
n'existe pas (prompt 1.4 jamais implémenté). Impossible de réutiliser ce qui
n'existe pas. Traité comme au prompt 1.3 : écran fonctionnel en ligne
uniquement, avec un bandeau honnête plutôt qu'une fausse promesse.

Implémenté : `SlamView.vue` (stepper 4 étapes fidèle à `#s-slam`, contenu
chargé depuis `GET /slam/referentiel`, jamais dupliqué en dur côté frontend),
`PermisValidationView.vue` (vue responsable fidèle à `#s-permis`).

**Amélioration backend nécessaire pour cet écran** : `ControlesAutomatiquesSortie`
(prompt 2.2) ne renvoyait qu'une liste plate de motifs d'échec — impossible d'en
tirer "la liste des contrôles avec leur résultat" (qui suppose de montrer aussi
ce qui PASSE). Ajouté `details: list[ControleDetail]`, une ligne fixe par
condition (a/b/c/d) avec son statut individuel, rétrocompatible (`motifs`
conservé). Testé (nouveau test dédié) avant de construire l'écran dessus.

**Compromis et écarts à signaler :**

1. **Accès au plan de sauvetage entièrement absent de la maquette** : aucun
   bouton, aucun écran dédié dans le prototype de référence. Construit de
   toutes pièces (`PlanSauvetage.vue`), avec un contenu réel — pas inventé —
   repris de `03-Procedures_et_consignes/PLA-SHEQ-002_Plan_Sauvetage_Hauteur.docx`
   (numéros SAMU/Protection civile, conduite à tenir résumée). Codé en dur
   faute de module Documents (lot 4.3) pour le servir dynamiquement.
2. **Bandeau d'intervention de la maquette remplacé.** `#s-slam` affiche en
   dur "Pylône 24 m — FASO-NET, permis 2026-041, surveillant : O. Diarra" —
   impossible à reproduire fidèlement puisque SLAM n'est relié à aucun permis
   précis dans notre modèle (décision actée au 2.2). Omis plutôt que simulé.
3. **Noms des intervenants non affichés** (`Utilisateur #id` à la place) sur
   l'écran de validation : l'API ne renvoie que des `intervenant_ids`, même
   limite déjà signalée pour l'auteur d'un signalement au prompt 1.3.
4. **Aucun écran de liste des permis** : la maquette desktop (A.30) en a un,
   mais ce prompt ne le demande pas explicitement dans ses livrables — la vue
   de validation n'est donc atteignable que par URL directe
   (`/permis/{id}/validation`), pas depuis un menu. Écart de navigation réel,
   à combler si une liste des permis est demandée plus tard.
5. **Hors connexion non traité** (détaillé plus haut) : bandeau honnête sur
   l'écran SLAM, comme sur l'écran Signalement depuis le prompt 1.3.

**Vérifié en conditions réelles, dans un vrai navigateur :** parcours SLAM
complet automatisé — 4 étapes traversées, bouton "Étape suivante" refusant
d'avancer tant qu'un point n'est pas coché (vérifié explicitement à chaque
étape), décision GO enregistrée avec le message exact de la maquette. Écran de
validation testé avec un permis réellement bloqué (créé via l'API) : les 4
contrôles s'affichent avec leur résultat individuel (3 conformes, 1 en échec
avec son motif), bouton "Valider et délivrer" désactivé. Captures d'écran
comparées visuellement aux maquettes. Zéro erreur console sur les deux
parcours. 118 tests pytest passent (117 précédents + 1 nouveau sur `details`),
3 toujours skippés (1.4).

### Détail — Prompt 2.4 (terminé le 2026-09-06)

Source lue : section 5.3.1 du CDC (module Inspections). Ce prompt est backend
uniquement (pas de bullet d'écran).

**Décision architecturale majeure, au-delà des 14 entités — à signaler
explicitement** : le CDC demande des « modèles de checklists paramétrables ».
Recherche des sources réelles (`FOR-SHEQ-011_Checklists_Inspection.xlsx` pour
locaux/incendie/électricité, `FOR-SHEQ-005`/`FOR-SHEQ-010` pour installations/
équipements) : **93 points réels** au total, organisés en catégories pour 2
des 5 types. Un volume et un besoin de « paramétrable » de cet ordre ne
pouvaient pas rester une constante Python (contrairement au référentiel SLAM,
fixe et jamais qualifié de « paramétrable » par le CDC) : ajout d'une entité
**POINT_CHECKLIST**, une 15e table hors du dictionnaire des 14, avec CRUD
minimal (créer, lister, archiver — pas de suppression physique). Les 93
points réels sont semés par une migration de données dédiée, dont le contenu
vit dans `app/models/checklist_referentiel.py` (partagé avec les fixtures de
test — voir plus bas).

Implémenté : `POST/GET /points-checklist`, `POST /points-checklist/{id}/archiver` ;
`POST /inspections` (cotation C/NC/SO en un seul envoi), `PATCH .../points`
(tant que non clôturée), `POST .../points/{id}/photo`, `POST .../cloturer`
(génère les actions correctives, une par point NC), `GET .../planification`.

**`Inspection.taux_conformite` converti en propriété calculée**, il était une
colonne stockée depuis le prompt 0.2 — cohérent avec `Action.en_retard` et
`Epi.est_conforme` : jamais de valeur dérivée susceptible de devenir périmée
en base.

**Bug d'infrastructure trouvé et corrigé pendant l'écriture des tests** : les
tests utilisent `Base.metadata.create_all()`, pas Alembic — la migration de
données (les 93 points) ne s'exécutait donc jamais pour la base de test,
11 tests échouaient avec `IndexError`. Corrigé en extrayant le contenu dans
`app/models/checklist_referentiel.py`, importé à la fois par la migration et
par `tests/conftest.py` : plus jamais de divergence possible entre ce qui est
semé en développement/production et ce que les tests utilisent.

**Compromis et écarts à signaler :**

1. **Actions correctives générées à la clôture, pas à la saisie de chaque
   point.** Le prompt dit « à l'enregistrement » (ambigu) ; générer à chaque
   sauvegarde intermédiaire aurait dupliqué les actions si l'inspection est
   corrigée avant d'être close. Résolu en faveur de la clôture, seul moment
   où le contenu est définitif.
2. **Délai des actions correctives fixé à 30 jours**, non donné par le CDC —
   choisi par cohérence avec l'alerte "actions à J-7" du tableau 3 (chapitre
   6.3), à confirmer avec le référent SHEQ.
3. **Responsable par défaut de l'action = l'inspecteur lui-même** : le CDC ne
   précise pas qui doit traiter un écart constaté ; l'inspecteur reste
   modifiable ensuite via l'API Actions (prompt 1.2).
4. **Photo uniquement après création**, via un endpoint dédié par point
   (`POST .../points/{id}/photo`), pas dans la requête de création elle-même
   — simplifie le contrat de `POST /inspections` (JSON pur, pas de
   multipart) puisque ce prompt n'a pas de contrainte d'écran à respecter.
5. **Planification calculée en direct depuis les inspections clôturées**
   (pas de table de planification dédiée) : périodicités reprises telles
   quelles des formulaires sources ("Fréquence recommandée" / "recommandation"
   dans FOR-SHEQ-005/010/011). Équipements varie selon la criticité dans le
   formulaire d'origine (trimestrielle à semestrielle) ; trimestrielle
   retenue par défaut faute de champ de criticité sur EQUIPEMENT.
6. **Hors connexion non traité** (même limite que 1.3/2.3) : aucun bandeau
   ajouté ici faute d'écran à construire dans ce prompt.

**Vérifié en conditions réelles :** 132 tests pytest passent (118 précédents +
14 nouveaux), 3 toujours skippés (1.4). Migrations testées en upgrade et
downgrade, 93 points confirmés en base (13/14/15/25/26 par type, total exact).
Sur le serveur de démo redémarré à neuf : inspection électricité créée avec
1 conforme/1 non conforme/1 sans objet → taux 0,5 confirmé ; clôture génère
exactement 1 action avec l'échéance +30 jours ; planification recalculée
immédiatement après (90 jours, périodicité trimestrielle électricité).

### Détail — Prompt 3.1 (terminé le 2026-09-06)

Source lue : section 5.2.3 du CDC (module Parc et configurations). Ce prompt
est backend uniquement (pas de bullet d'écran) : aucune vue frontend n'existe
encore pour EPI ni Inspections non plus (2.1, 2.4), ce module suit le même
principe.

**Note de cohérence documentaire, sans impact sur le code** : la section 5.2.3
cite les « figures A.7 et A.33 » comme écrans de référence. Vérification dans
le CDC : la figure A.33 réelle est légendée « Formations : matrice de
compétences... », pas le parc — la bonne figure desktop est en réalité
**A.31** (« Parc et configurations : équipements, qualité de liaison et état
des sauvegardes »). Incohérence de renvoi dans le document source lui-même, à
signaler au référent SHEQ ; sans conséquence ici puisque ce prompt ne
comporte pas d'écran.

**Ajout d'un lien `Inspection.equipement_id` (nullable), en amont de ce
prompt** : FOR-SHEQ-010 précise qu'« une même fiche est remplie par
équipement ou par baie/site selon le contexte ». Sans ce lien, la fiche
équipement demandée ici (« historique complet : configurations, inspections,
incidents ») n'aurait jamais pu retrouver les inspections d'un équipement
donné. Migration `14382e24e575`, avec `batch_alter_table` (SQLite ne
supporte pas l'ajout d'une contrainte de clé étrangère nommée hors mode
batch, même motif que `4b398dde2947` et `fb8c539876c8`) — cycle
upgrade/downgrade/upgrade vérifié avant d'aller plus loin.

Implémenté : `POST/GET/PATCH /equipements`, `GET /equipements/{id}`,
`GET /equipements/{id}/fiche` (agrégat configurations + inspections +
incidents), `POST /equipements/import` (CSV ou XLSX, rapport d'erreurs ligne
par ligne).

**Compromis et écarts à signaler :**

1. **Format `identity` validé par une forme structurelle (regex
   `SITE-FONCTION-NN`, normalisée en majuscules), pas par un vocabulaire de
   FONCTION fermé.** Le chapitre 7.3.1 (« Tableau 5 ») donne la forme mais
   aucune liste de codes FONCTION n'existe ailleurs dans le CDC, à la
   différence des préfixes EPI (H/L/C...) — cohérent avec sa propre mention
   « saisi par le technicien, unicité contrôlée ». À confirmer avec le
   référent SHEQ si une liste fermée doit finalement être imposée.
2. **« Incidents associés » de la fiche équipement = signalements de type
   incident/accident du même SITE, pas de l'équipement précis.** Le
   dictionnaire ne modélise aucun lien SIGNALEMENT → EQUIPEMENT (seulement
   SIGNALEMENT → SITE), contrairement à CONFIGURATION et au nouveau
   INSPECTION.equipement_id. Ajouter une colonne équipement à SIGNALEMENT
   sur la seule base du mot « associés » (sans le point d'appui textuel
   explicite qui existait pour INSPECTION via FOR-SHEQ-010) aurait été une
   extension trop spéculative du modèle : la corrélation par site est donc
   une approximation assumée, à affiner si le référent SHEQ le demande.
3. **Nouvelle dépendance `openpyxl` (3.1.x)** — la bibliothèque standard ne
   lit pas le format XLSX, seul le CSV (module `csv`). Signalée dans
   `requirements.txt`.
4. **Le gabarit réel (`docs/INV-SHEQ-001_Inventaire_Parc.xlsx`) contient des
   colonnes sans équivalent dans le modèle EQUIPEMENT** : « Adresse IP »
   (donnée de CONFIGURATION, pas d'EQUIPEMENT), « Type d'équipement » (non
   modélisé, seuls marque/modèle le sont), « Fiche de configuration (réf.) »
   et « Dernière inspection » (dérivées des historiques, jamais saisies).
   Ces colonnes sont acceptées si présentes mais ignorées à l'import plutôt
   que de rejeter le fichier réel tel qu'il existe.
5. **Dates du gabarit au format MM/AAAA** (ex. « 03/2026 »), pas une date
   complète : jour fixé au 1er du mois faute de jour réel connu. Les formats
   JJ/MM/AAAA et AAAA-MM-JJ restent acceptés par tolérance.
6. **Import "tout ou rien" par ligne, pas par fichier** : chaque ligne est
   validée et insérée indépendamment ; une ligne en erreur n'empêche pas les
   lignes valides du même fichier d'être importées — cohérent avec la
   demande explicite d'un « rapport d'erreurs par ligne » plutôt qu'un rejet
   global.
7. **Droits** : `GERER_PARC` (création/modification) ouvert à technicien +
   administrateur, conforme à « Saisie : techniciens » (5.2.3). Le CDC cite
   aussi « responsable technique, direction » pour la consultation et
   l'administration, deux libellés absents de la matrice de rôles
   (CLAUDE.md, point 6) : l'import initial (reprise de données, pas une
   saisie de terrain) est rapproché du rôle RESPONSABLE existant plutôt que
   laissé ouvert au technicien — à confirmer avec le référent SHEQ. La
   consultation (recherche, fiche) reste ouverte à tout utilisateur
   authentifié, comme pour EPI (2.1).
8. **Hors connexion non traité** (même limite que 1.3/2.3/2.4) : aucun
   bandeau ajouté ici faute d'écran à construire dans ce prompt.

**Vérifié en conditions réelles :** 145 tests pytest passent (132 précédents +
13 nouveaux), 3 toujours skippés (1.4). Migration `14382e24e575` testée en
upgrade/downgrade/upgrade sur une base SQLite fraîche. Sur le serveur de démo
redémarré à neuf : équipement créé via l'API avec une identity saisie en
minuscules (`bko-st-01`) → confirmée normalisée en `BKO-ST-01` ; recherche
par fragment d'identity, par site et par marque toutes vérifiées ; fiche
équipement confirmée vide (aucun historique) pour un équipement neuf. Le
fichier réel `docs/INV-SHEQ-001_Inventaire_Parc.xlsx` importé tel quel contre
le serveur vivant : sa ligne d'exemple (site `[Client A]`, explicitement
marquée « Exemple à supprimer » dans le classeur) est correctement rejetée
avec l'erreur « Site « [Client A] » introuvable » plutôt qu'importée ou
provoquant un plantage — comportement attendu puisqu'aucun site de ce nom
n'existe en base.

### Détail — Prompt 3.2 (terminé le 2026-09-06)

Sources lues : section 5.2.3 du CDC et les quatre fiches papier réelles
FOR-SHEQ-006 à 009 (MikroTik, Grandstream, Ubiquiti LiteBeam, Ruijie),
classées CONFIDENTIEL dans le SMI documentaire — lues directement à leur
emplacement source (`04-Formulaires_vierges/CONFIDENTIEL/`) pour leur seule
structure de champs, jamais copiées ni versionnées dans ce dépôt (voir
`docs/formulaires/LISEZ-MOI.txt`, note posée dès le prompt 0.1). Leur section
« Identifiants d'accès (CONFIDENTIEL) » (utilisateur/mot de passe admin, clé
Wi-Fi, etc.) a été lue puis délibérément exclue de tout schéma : c'est
exactement le contenu que la règle de conception de la section 5.2.3 interdit
dans ce module (« aucun champ de mot de passe... toute saisie d'identifiant
se fait exclusivement dans le module coffre-fort », lot 3.3).

**Décision de portée, tranchée par l'utilisateur avant de coder** : ce prompt
cite une maquette précise (figure A.8) et une exigence visuelle (retour
vert/orange). Recherche dans `docs/maquettes/Maquettes_SHEQ_Management_v2.html` :
l'écran existe bien (`#s-config`, fiche MikroTik complète avec champs
colorés, dépôt de sauvegarde, bandeau anti-mot de passe). Choix fait de
rester sur le même principe que 2.1/2.4 : **backend uniquement**, l'écran
mobile étant réservé à un futur prompt « Interfaces », comme cela avait été
fait pour SLAM/permis (2.3) plutôt que de le construire au fil de 2.2.

**Implémenté** : `POST /configurations` (multipart : champs génériques
+ `parametres_reseau`/`parametres_sansfil` en JSON, fichiers de sauvegarde
optionnels), `GET /configurations/{id}`, `GET /configurations/{id}/export-pdf`.
Aucune route de modification/suppression : l'immuabilité (règle 5,
CLAUDE.md) est garantie par l'absence structurelle de route, pas par une
vérification applicative contournable.

**Validation par marque** : un schéma Pydantic dédié par marque
(`parametres_reseau`/`parametres_sansfil`), avec `extra="forbid"` — une
liste blanche de champs autorisés, qui empêche par construction qu'un champ
mot de passe s'y glisse, plutôt qu'une liste noire de noms interdits.
Vérifié explicitement par un test qui tente de glisser `mot_de_passe_admin`
dans `parametres_reseau` MikroTik : rejeté en 422.

**Compromis et écarts à signaler :**

1. **Grandstream et Ruijie n'ont pas de véritable volet « sans fil »**
   (téléphonie SIP pour l'un, VLAN/ports/gestion cloud filaire pour l'autre)
   mais le dictionnaire (7.2.5) ne prévoit que deux champs « Structure » pour
   CONFIGURATION. Leurs champs spécifiques sont donc regroupés dans
   `parametres_reseau`, `parametres_sansfil` restant `null` pour ces deux
   marques (le service rejette explicitement toute valeur envoyée dessus
   pour elles). Une troisième colonne JSON dédiée aurait été plus propre
   sémantiquement, mais aurait exigé une migration pour un seul cas d'usage
   par marque — jugé disproportionné, à revoir si un cinquième champ
   spécifique apparaît un jour.
2. **Champs par marque limités à la liste du prompt**, pas à l'intégralité du
   formulaire papier réel : par exemple, Ruijie a une vraie section Wi-Fi
   (SSID principal/invité, bandes) dans FOR-SHEQ-009, non reprise ici car le
   prompt ne demande que « VLAN, ports, mode de gestion cloud » pour cette
   marque. Champ `protocole` (MikroTik) interprété comme la sécurité
   sans-fil (WPA2-PSK/WPA3 sur la fiche réelle), le prompt employant un mot
   différent du formulaire papier.
3. **Seuils de conformité repris littéralement des fiches réelles** :
   signal entre -65 et -50 dBm, CCQ > 90 % (mêmes valeurs sur FOR-SHEQ-006 et
   FOR-SHEQ-008) — sans objet (`null`, gris) pour Grandstream/Ruijie, qui
   n'envoient pas ces mesures.
4. **Convention de nommage des sauvegardes clarifiée par la maquette** : le
   CDC énonce la forme « SITE-IDENTITY-AAAAMMJJ », mais `identity` suit
   elle-même déjà la forme SITE-FONCTION-NN (prompt 3.1) — la maquette
   mobile (drop-zone de l'écran s-config : « FAS-AP-01-20260904 ») confirme
   qu'il n'y a pas de second préfixe de site distinct : le nom attendu est
   `{identity}-{AAAAMMJJ}`. Contrôlé sur le nom ORIGINAL du fichier avant
   tout écriture sur disque (tout ou rien) ; le fichier reste stocké sous un
   nom aléatoire comme partout ailleurs dans l'application (jamais le nom
   fourni par le client) — la fiche PDF affiche donc ce nom aléatoire, pas
   le nom conventionné d'origine, celui-ci n'étant conservé nulle part.
5. **Référence `ENR-SHEQ-AAAA-NNN`** (point 7, CLAUDE.md), confirmée par la
   maquette (toast « Fiche enregistrée · ENR-SHEQ-2026-118 ») plutôt
   qu'inventée.
6. **Nouvelle dépendance `reportlab`** pour l'export PDF — bibliothèque pure
   Python (pas de dépendance système type GTK/Cairo, contrairement à
   weasyprint), pertinent sur l'environnement de développement Windows de ce
   projet. Mise en page simple par sections, fidèle à l'ordre du formulaire
   papier réel (moins sa section confidentielle) mais pas un fac-similé
   pixel du papier, faute de gabarit visuel exploitable hors du fichier
   CONFIDENTIEL lui-même.
7. **Droits** : `GERER_PARC` réutilisé tel quel (même acteur « Saisie :
   techniciens » que pour les équipements, section 5.2.3 couvrant les deux
   sous-modules). Consultation et export PDF ouverts à tout utilisateur
   authentifié.
8. **Hors connexion non traité** (même limite que 1.3/2.3/2.4/3.1) : aucun
   écran construit dans ce prompt.

**Vérifié en conditions réelles :** 157 tests pytest passent (145 précédents
+ 12 nouveaux), 3 toujours skippés (1.4). Sur le serveur de démo redémarré à
neuf : équipement MikroTik réel créé, fiche de configuration complète créée
avec un fichier `.rsc` nommé selon la convention (`BKO-AP-01-20260906.rsc`)
→ acceptée, référence `ENR-SHEQ-2026-001` confirmée ; un second essai avec un
nom non conforme (`mauvais_nom.rsc`) rejeté en 400 avec le nom attendu
explicite dans le message d'erreur ; export PDF vérifié comme un document
PDF 1.4 valide à deux pages, sections dans l'ordre attendu, valeurs vides
affichées « — » plutôt que le littéral Python `None` (corrigé après
inspection visuelle du PDF généré, pas détecté par les tests automatisés —
même leçon que pour les chemins de fichiers du prompt 1.3 : certains défauts
ne se voient qu'en regardant le résultat réel).

### Détail — Prompt 4.1 (terminé le 2026-09-06)

Sources lues : section 5.2.5 du CDC (module Risques et plan d'action),
l'entité RISQUE au dictionnaire (7.2.2), et le classeur réel
`docs/REG-SHEQ-001_Registre_des_Risques.xlsx` (18 risques réels, feuilles
Cotation/Registre/Synthèse). Prompt 3.3 (coffre-fort) reste en pause, sa
conception ayant été présentée mais pas encore validée par l'utilisateur —
celui-ci a explicitement sélectionné le 4.1 ensuite, sans répondre sur le 3.3 ;
traité comme un report, sur le même principe que le 1.4 en son temps.

**Décision architecturale majeure, à signaler explicitement** : le
dictionnaire modélise RISQUE avec une cotation unique intégrée (probabilite,
gravite, criticite, niveau, date_evaluation, auteur_id en colonnes directes).
Mais la règle de gestion 5.2.5 est explicite et sans ambiguïté : « Une
réévaluation ne remplace pas la cotation antérieure : elle s'ajoute à
l'historique. » Ces deux exigences sont incompatibles avec des colonnes à
valeur unique, et le dictionnaire ne décrit aucune entité d'historique pour
les résoudre. Scindé RISQUE (identité stable : numéro, danger, catégorie,
unité de travail, personnes exposées) et une nouvelle entité
**COTATION_RISQUE** (une ligne par réévaluation, immuable après création,
même principe que CONFIGURATION) — une 16e table hors du dictionnaire des 14,
même précédent que POINT_CHECKLIST (prompt 2.4), signalée plutôt que passée
sous silence. Migration `88a3ec5c2f5f`, `batch_alter_table` requis (retrait
de colonnes + contrainte de clé étrangère sur SQLite), avec un piège
supplémentaire découvert en la testant : le mode batch reporte tel quel tout
CHECK constraint existant non explicitement supprimé, y compris ceux qui
référencent une colonne sur le point d'être retirée — a fait échouer la
reconstruction de la table ("no such column: gravite") jusqu'à l'ajout d'un
`drop_constraint` explicite pour les deux CHECK hérités de RISQUE. Cycle
upgrade/downgrade/upgrade vérifié avant d'aller plus loin. Cette
restructuration a nécessité la mise à jour de quatre fichiers de tests
préexistants (`test_models.py`, `test_actions.py`, `test_recette_lot1.py`,
`test_tableau_bord.py`) dont les fixtures créaient un `Risque` selon
l'ancienne forme à une seule table.

**Bug préexistant repéré en passant, non corrigé** : les CHECK constraints de
l'entité RISQUE originale (migration `0ecd676d66b6`, prompt 0.2) portent un
nom doublé (`ck_risque_ck_risque_gravite_1_5` au lieu de
`ck_risque_gravite_1_5`), à cause d'un nom déjà préfixé passé en dur au
`CheckConstraint(name=...)` alors que la convention de nommage
(`app/db/base.py`) ajoute déjà ce préfixe automatiquement. Sans conséquence
fonctionnelle (le nom reste valide et unique), mais pas reproduit sur la
nouvelle table `cotation_risque`. Non corrigé sur `risque` pour ne pas
toucher une migration déjà appliquée ailleurs — signalé pour mémoire.

Implémenté : `POST/GET /risques`, `GET /risques/{id}` (détail avec historique
complet des cotations), `POST /risques/{id}/reevaluer`, `GET /risques/matrice`
(grille 5×5 complète, cases vides incluses), `GET /risques/revues-dues`,
`POST /risques/import` (CSV/XLSX, rapport d'erreurs par ligne).

**Compromis et écarts à signaler :**

1. **Règle « gravité 4 ou 5 → au moins une mesure de maîtrise » déjà couverte
   structurellement**, sans logique conditionnelle dédiée : `mesures_proposees`
   est obligatoire et non vide pour TOUTE cotation, quelle que soit la
   gravité (le dictionnaire le marque "Oui" sans distinction) — aucune
   dérogation n'existe qui permettrait de contourner la règle pour les
   gravités 1 à 3, donc rien de plus à ajouter pour 4/5 spécifiquement.
2. **Périodicité de la revue annuelle fixée à 12 mois** depuis la date de la
   dernière cotation — le CDC dit "revue annuelle obligatoire, rappelée
   automatiquement" sans donner de formule (contrairement à EPI, chapitre
   7.3.2, qui donne "+12 mois" explicitement) : douze mois retenu par
   cohérence directe avec le mot "annuelle", pas une valeur inventée sans
   ancrage. Une réévaluation reporte naturellement la prochaine échéance.
3. **Numéro de registre attribué par le serveur** (séquence globale,
   max+1) à la création normale ; **honoré tel quel à l'import** (la colonne
   N° du classeur réel préserve l'ordre historique du registre papier),
   avec rejet si un numéro importé est déjà pris. Après import, les
   créations normales continuent au-delà du plus grand numéro existant.
4. **Colonnes du classeur réel sans équivalent modélisé** : « Responsable »,
   « Échéance », « Statut » sont en réalité des champs d'ACTION (section
   5.2.5), pas de RISQUE — mais « Responsable » y est un intitulé de rôle
   ("Référent SHEQ", "Direction", "Tout le personnel"), pas un identifiant
   d'utilisateur réel : aucune correspondance fiable n'est possible sans
   deviner. Ces colonnes sont ignorées à l'import (le module Actions,
   prompt 1.2, permet de créer le suivi manuellement via `risque_id`) — même
   principe que les colonnes non modélisées ignorées au prompt 3.1.
5. **« Danger identifié » et « Risque / Dommage potentiel » concaténés**
   dans le seul champ `danger` du dictionnaire (200 caractères) : le
   classeur réel sépare cause et conséquence en deux colonnes, le
   dictionnaire n'en prévoit qu'une — concaténées plutôt que de perdre l'une
   des deux silencieusement ; une ligne dont le résultat dépasserait 200
   caractères est rejetée avec le nombre de caractères, à raccourcir
   manuellement (aucun cas réel du classeur ne dépasse la limite).
6. **Date d'évaluation uniforme pour tout un import** (paramètre optionnel de
   la route, par défaut la date du jour) : le classeur réel ne donne qu'une
   période globale ("mars – mai 2026"), pas une date par ligne. Même logique
   que l'auteur (utilisateur qui déclenche l'import, faute de "Évaluateurs"
   nommément rattachables à des comptes réels).
7. **Droits** : `GERER_RISQUES` (référent SHEQ + administrateur) couvre
   création, réévaluation et import — la section 5.2.5 ne distingue pas
   d'acteur "administration" séparé comme le faisait 5.2.3 pour le parc.
   Consultation ouverte à tout utilisateur authentifié ("ensemble du
   personnel").
8. **Hors connexion non traité** (même limite que les prompts précédents).

**Vérifié en conditions réelles :** 169 tests pytest passent (157 précédents
+ 12 nouveaux), 3 toujours skippés (1.4). Migration `88a3ec5c2f5f` testée en
upgrade/downgrade/upgrade. Sur le serveur de démo redémarré à neuf, le
classeur réel `REG-SHEQ-001_Registre_des_Risques.xlsx` importé intégralement :
18/18 lignes importées sans erreur, criticité et niveau recalculés
serveur-side pour chacune — et la répartition par niveau qui en résulte
(0 critique, 9 élevé, 7 modéré, 2 faible) reproduit exactement la feuille
« Synthèse » du classeur source, qui donne les mêmes quatre chiffres. Matrice
5×5 vérifiée : les risques apparaissent dans la bonne case, les cases vides
sont bien présentes. Rappel de revue vérifié avec une cotation antidatée de
370 jours : correctement signalée `due`.

### Détail — Prompt 4.2 (terminé le 2026-09-06)

Trois modules liés implémentés en un seul prompt, comme demandé explicitement
par son texte. Sources lues : sections 5.3.3 et 5.3.4 du CDC, et les
formulaires réels FOR-SHEQ-014 (Feuille de présence), FOR-SHEQ-015 (Quiz de
sensibilisation, 10 questions), FOR-SHEQ-016 (CR de revue de direction) et
FOR-SHEQ-017 (Grille d'audit interne, non classée confidentielle contrairement
aux fiches de configuration).

**Constat préalable, à signaler** : le chapitre 7 du dictionnaire ne contient
en réalité que 8 entités détaillées avec table de champs (UTILISATEUR,
RISQUE, SIGNALEMENT, EQUIPEMENT, CONFIGURATION, EPI, PERMIS, SECRET/
JOURNAL_ACCES) — SITE, ACTION, DOCUMENT, INSPECTION, EVALUATION_SLAM n'ont
jamais eu de table de champs propre non plus (déjà noté dans leurs modèles
respectifs). FORMATION, COMPETENCE, QUIZ, AUDIT, EXIGENCE, REVUE_DIRECTION et
DECISION n'existent nulle part dans le CDC, ni comme entité ni comme liste
énumérée (aucune liste des « 22 exigences » citées par le prompt) : tout le
modèle de données de ce prompt est une reconstruction, faite pour coller aux
formulaires papier réels plutôt qu'aux seules 5 phrases fonctionnelles de
chaque section du CDC.

**Sept nouvelles entités hors dictionnaire** (même précédent que
POINT_CHECKLIST et COTATION_RISQUE) : Competence, Habilitation, Seance,
Emargement, QuestionQuiz, TentativeQuiz (Formations) ; ExigenceAudit,
CampagneAudit, CotationAudit (Audits) ; RevueDirection, DecisionRevue
(Revues) — onze au total. `Action.cotation_audit_id` ajouté, comme anticipé
explicitement dans le commentaire du modèle Action depuis le prompt 1.2
("AUDIT n'existe pas encore — colonne à ajouter par migration au lot 4").
Trois migrations chaînées : `b0fef0f9add6` (schéma, `batch_alter_table` pour
la colonne sur `action`), `c1a2b3d4e5f6` (seed des 22 exigences réelles de
FOR-SHEQ-017) et `d2b3c4e5f6a7` (seed des 10 questions réelles de
FOR-SHEQ-015) — même principe que `dafa396b65c4` (prompt 2.4) : contenu
partagé entre la migration et `tests/conftest.py` via `audit_referentiel.py`
et `quiz_referentiel.py`, pour ne jamais diverger.

**Décision de portée** : ce prompt insiste sur le soin de présentation de la
comparaison de maturité, mais reste dans la même famille que 2.1/2.4/3.2/4.1
(pas de figure d'écran citée explicitement comme condition du prompt lui-même,
contrairement au 3.2). Backend uniquement, comme les précédents modules de
cette forme : la structure de `ComparaisonCampagnes` (delta signé, par
chapitre, prêt pour un graphique) est pensée pour qu'un futur écran n'ait pas
à retravailler les données, mais aucun écran n'est construit ici.

**Compromis et écarts à signaler :**

1. **Score de maturité au dénominateur variable** : formule du chapitre 7.3.2
   ("somme des cotations rapportée au double du nombre d'exigences cotées")
   appliquée littéralement — une campagne partiellement remplie a un score
   maximal égal à 2× ses seules exigences déjà cotées, pas 44 (2×22) par
   défaut. Vérifié en conditions réelles (une seule exigence cotée à 2/2 →
   score 2/2 = 100 %, pas 2/44).
2. **Seuils d'interprétation (mature ≥ 80 %, en construction 50-79 %,
   prioriser < 50 %) et seuils de cotation (0/1/2)** repris littéralement de
   FOR-SHEQ-017, pas inventés — le CDC lui-même ne les donne pas.
3. **« Créer une action corrective à partir d'un écart » traité comme un acte
   manuel**, pas une génération automatique à la clôture (contrairement à
   Inspection, où CLAUDE.md énonce explicitement la règle automatique) : le
   CDC ne formule pas cette règle pour les audits de la même façon, et
   générer 22 actions à chaque clôture (même pour des écarts mineurs déjà
   suivis autrement) aurait été une interprétation plus intrusive que le
   texte ne l'exige.
4. **Seuil de réussite du quiz exprimé en proportion (70 %)**, pas en valeur
   absolue "sur 10" : le référentiel de questions est géré par le référent
   SHEQ (comme POINT_CHECKLIST) et peut donc évoluer en nombre — une
   proportion reste correcte quel que soit le total, une valeur absolue "7"
   ne le resterait pas.
5. **Émargement idempotent par (séance, participant)** : un second appel
   corrige le premier plutôt que de dupliquer la ligne — une présence n'est
   pas un historique à conserver point par point (contrairement aux
   cotations de risque ou aux configurations, délibérément immuables).
6. **Clôture de séance = renouvellement automatique des habilitations des
   présents**, seulement si la séance est rattachée à une compétence : lien
   direct avec la phrase "données gérées" de la section 5.3.3, qui associe
   explicitement compétences et séances — vérifié en conditions réelles
   (date d'expiration exactement +12 mois après la date de séance).
7. **Décisions de revue reportées globalement**, pas seulement celles de la
   revue immédiatement précédente : toute décision encore ouverte, quelle
   que soit son ancienneté, apparaît dans les données d'entrée de la
   prochaine revue — cohérent avec une décision qui resterait ouverte sur
   plusieurs cycles trimestriels.
8. **Rapport de revue sans le taux de conformité moyen des inspections** :
   `Inspection.taux_conformite` est une propriété Python calculée (prompt
   2.4), pas une colonne — la moyenner sans un N+1 aurait exigé de charger
   toutes les inspections de la période, jugé disproportionné pour ce seul
   champ du rapport.
9. **Droits du module Revues rapprochés de RESPONSABLE/ADMINISTRATEUR +
   REFERENT_SHEQ** : le CDC ne cite que "direction" comme acteur, mais
   FOR-SHEQ-016 désigne le référent SHEQ comme rédacteur et cosignataire du
   compte rendu — à confirmer avec le référent SHEQ si ce rapprochement est
   trop large.
10. **Hors connexion non traité** (même limite que tous les prompts
    précédents).

**Vérifié en conditions réelles :** 193 tests pytest passent (169 précédents
+ 24 nouveaux), 3 toujours skippés (1.4). Les trois migrations testées en
upgrade/downgrade/upgrade. Sur le serveur de démo redémarré à neuf :
compétence + séance créées, émargement enregistré, clôture de la séance
confirmée renouveler l'habilitation du participant présent (expiration
2027-09-06 pour une séance du 2026-09-06 et une périodicité de 12 mois) ;
quiz passé avec les 10 questions réelles, score recalculé serveur-side ;
campagne d'audit cotée sur les 22 exigences réelles (cotation 1 partout →
score 22/44 = 50 %, "En construction", exactement conforme à l'interprétation
de FOR-SHEQ-017) ; comparaison entre deux campagnes (50 % puis 100 %) donnant
une évolution de +50 points, cohérente par chapitre ; revue de direction
créée avec ses indicateurs de période assemblés automatiquement, décision
non soldée correctement reportée dans les données d'entrée de la revue
suivante avec son identifiant de revue d'origine conservé.

### Détail — Prompt 4.3 (terminé le 2026-09-06)

Quatre modules implémentés ensemble, comme demandé. Sources lues : sections
5.3.5 et 5.3.6 du CDC (une seule section combinée pour Visiteurs/Déchets/
Satisfaction, pas trois sous-sections distinctes), et les documents réels
LM-SHEQ-001 (Liste maîtresse), REG-SHEQ-004 (Registre des visiteurs),
REG-SHEQ-005 (Registre des déchets), PRO-SHEQ-004 (Procédure de maîtrise
documentaire) et FOR-SHEQ-018 (Fiche de satisfaction client). Conformément à
la consigne du prompt ("plus simples que les précédents : privilégie la
cohérence avec l'existant"), DOCUMENT (déjà modélisé depuis le prompt 0.2,
avec `accuses_lecture` déjà anticipé en JSON) a été réutilisé et étendu
plutôt que reconstruit, et seulement quatre nouvelles entités ont été
ajoutées au lieu d'une par sous-fonctionnalité.

**Nouvelle note de cohérence documentaire** : le CDC contient ici aussi des
renvois de figures incohérents (déjà rencontré aux prompts 3.1, 3.2 et 4.2).
§5.3.5 cite la figure A.38 pour l'écran de gestion des documents, mais A.38
est en réalité l'écran Déchets ; le bon renvoi est A.36 ("Liste maîtresse des
documents"). §5.3.6 cite A.39-A.41 pour Visiteurs/Déchets/Satisfaction, mais
A.40-A.41 sont en réalité Utilisateurs/rôles et Paramètres ; le bon renvoi
est A.37-A.39. Sans conséquence ici (prompt backend), à signaler au référent
SHEQ pour correction du document source.

**Décision de modélisation notable — DOCUMENT** : la règle 5.3.5 ("une seule
version en vigueur à un instant donné" + "la version antérieure passant
automatiquement en archive" à l'approbation) exigeait de lever la contrainte
d'unicité posée sur `reference` seule depuis le prompt 0.2 — remplacée par
une contrainte composite `(reference, version)`, migration `6efa01e166a2`
avec `batch_alter_table`. Une nouvelle version est une NOUVELLE ligne
(statut BROUILLON), jamais une réécriture de l'ancienne — même principe que
CONFIGURATION et COTATION_RISQUE — et l'ancienne version EN_VIGUEUR n'est
archivée qu'au moment où la NOUVELLE est approuvée, pas au moment où le
brouillon de la nouvelle version est créé (lu littéralement dans la règle :
c'est "approuver" qui déclenche l'archivage, pas "créer une nouvelle
version").

**Quatre nouvelles entités hors dictionnaire** : Visiteur, Dechet,
EnqueteSatisfaction, ReponseSatisfaction — le chapitre 7 n'en contient
aucune, ni pour ces trois modules ni pour Documents (même constat que les
prompts 4.1/4.2 : le dictionnaire réel ne couvre que 8 entités). Ajout
également de `Action.reponse_satisfaction_id` (5e origine possible, après
risque/signalement/inspection/cotation_audit), pour "l'ouverture d'une
analyse" que la règle 5.3.6 associe à une note de satisfaction basse.

**Compromis et écarts à signaler :**

1. **Visibilité des documents filtrée par statut, pas par route séparée** :
   un document EN_APPROBATION ou BROUILLON renvoie 404 (pas 403) à un
   utilisateur non autorisé à le voir — délibéré, pour ne pas révéler
   qu'un brouillon existe à qui n'y a pas droit (règle 5.3.5 : "n'est pas
   accessible aux utilisateurs finaux").
2. **Séparation rédaction/approbation assurée par les rôles, pas par une
   vérification "auteur ≠ approbateur"** : `GERER_DOCUMENTS`
   (référent SHEQ + administrateur) et `APPROUVER_DOCUMENTS`
   (responsable + administrateur) sont des ensembles disjoints sauf pour
   l'administrateur, qui peut se retrouver rédacteur et approbateur du même
   document — cohérent avec le principe "Tout" de son propre périmètre déjà
   appliqué partout ailleurs dans l'application (CLAUDE.md, point 6), pas
   une lacune propre à ce prompt.
3. **Visiteur.personne_visitee en texte libre**, pas une clé étrangère vers
   UTILISATEUR : le registre réel (REG-SHEQ-004) note un nom en clair, pas
   nécessairement celui d'un compte de l'application (accueil, service
   générique...).
4. **Dechet.quantite en texte libre** ("2 unités", "5 kg") plutôt qu'un
   nombre et une unité séparés : fidèle au registre réel (REG-SHEQ-005), qui
   mélange les deux sans les distinguer.
5. **Les 6 critères de satisfaction traités comme une constante Python**
   (`satisfaction_service.CRITERES`), pas une table de référence
   supplémentaire hors dictionnaire : contrairement au quiz de sensibilisation
   ou aux checklists, le CDC ne les déclare jamais "paramétrables".
6. **"Ouverture d'une analyse... selon la procédure de gestion des
   signalements" interprétée comme le mécanisme d'action corrective déjà
   existant** (`Action.reponse_satisfaction_id`), pas une création automatique
   de SIGNALEMENT : un signalement exige un site et une description
   d'incident interne, deux champs qui ne correspondent pas naturellement à
   une réponse de satisfaction client — l'action reste un acte manuel
   (même choix qu'au prompt 4.2 pour les écarts d'audit), pas générée
   automatiquement à la soumission.
7. **Envoi d'enquête ouvert au technicien**, pas réservé au seul référent
   SHEQ : la section 5.3.6 dit "traitement par le référent SHEQ" pour les
   réponses, mais ne restreint pas explicitement qui peut envoyer une
   enquête après une intervention — ouvert au technicien qui vient de la
   terminer, plus restrictif pour le traitement des réponses.
8. **Aucun envoi réel (e-mail/SMS) du lien** : la route renvoie le jeton, à
   charge du futur frontend de construire l'URL partageable — aucune
   dépendance d'envoi ajoutée, non demandée explicitement et hors périmètre
   d'un prompt qui insiste sur la simplicité.
9. **Première route publique sans authentification de l'application**
   (`GET`/`POST /satisfaction/questionnaire/{jeton}`) : jeton
   `secrets.token_urlsafe(24)`, à usage unique (`repondu` verrouille l'accès
   après soumission), 404 générique que le jeton soit invalide ou déjà
   utilisé (pas de distinction révélant l'un des deux cas à un appelant non
   authentifié).
10. **Hors connexion non traité** (même limite que tous les prompts
    précédents).

**Vérifié en conditions réelles :** 217 tests pytest passent (193 précédents
+ 24 nouveaux), 3 toujours skippés (1.4). Migration `6efa01e166a2` testée en
upgrade/downgrade/upgrade. Sur le serveur de démo redémarré à neuf : document
créé, soumis, approuvé, nouvelle version créée puis approuvée à son tour —
confirmé que la version 01 passe bien en archive à l'approbation de la 02 ;
visiteur enregistré puis retiré de la liste des présents après son départ ;
déchet créé puis enlèvement enregistré avec un vrai fichier joint
(chemin stocké sous nom aléatoire, jamais le nom original) ; enquête de
satisfaction envoyée, questionnaire consulté et répondu **sans aucun en-tête
d'autorisation** (vérifié explicitement : la route publique fonctionne bien
sans jeton JWT), une note à 1/5 déclenchant correctement `necessite_analyse`,
et une seconde tentative sur le même jeton rejetée en 404.

### Détail — Prompt 4.4 (terminé le 2026-09-07)

Source lue : chapitre 6.3 du CDC, tableau 3 (« Règles de notification ») —
huit lignes reprises une à une, sans réinterprétation du canal, du délai ou
du destinataire. Ce prompt **résout un écart assumé depuis le prompt 1.1**
(voir point 4 du « Détail — Prompt 1.1 » ci-dessus) : la notification du
référent SHEQ à un nouveau signalement n'était qu'une ligne de journal
applicatif, faute d'entité NOTIFICATION et de service dédié — les deux
existent maintenant. Même chose pour les commentaires similaires laissés
dans `permis_service.py` (« responsable à notifier ») et
`evaluation_slam_service.py` (« notifié au responsable ») depuis le prompt
2.2 : les quatre événements immédiats du tableau 3 (signalement, permis en
attente, décision NO GO, satisfaction faible) sont maintenant tous câblés à
la création de leur événement respectif, pas seulement journalisés.

**Nouvelle entité NOTIFICATION**, hors dictionnaire comme les précédentes
(chapitre 7 n'en contient aucune). Clé de déduplication
`(type, objet_type, objet_id, destinataire_id, declencheur)` : essentielle
pour les quatre rappels périodiques (actions, EPI, inspections, documents),
rejoués chaque jour par le planificateur sans jamais créer de doublon —
`declencheur` inclut la date d'échéance en suffixe pour les objets réutilisés
dans la durée (un EPI garde la même ligne à travers des années de cycles de
vérification ; sans ce suffixe, la contrainte bloquerait tout rappel après
le tout premier cycle).

**APScheduler** (nouvelle dépendance, demandée explicitement par le prompt
lui-même, pas une décision d'implémentation prise seul) : un
`BackgroundScheduler` unique, exécuté chaque jour à 6h dans le même
processus que l'API — le CDC ne précise pas d'heure, choisie tôt le matin
pour que les rappels soient visibles à la prise de poste. Démarré/arrêté via
le cycle de vie de FastAPI (`lifespan`). **Désactivé pendant les tests**
(`settings.scheduler_actif = False`, posé dans `tests/conftest.py` avant
même l'import de `app.main`) : le job ouvre sa propre session sur la base de
données réelle (`SessionLocal`), jamais la base en mémoire substituée par
les tests — le laisser actif aurait risqué d'écrire dans le fichier
`sheq.db` du développeur à chaque exécution de la suite de tests.

**Courriels** : `smtplib` de la bibliothèque standard (aucune nouvelle
dépendance pour ce seul besoin) plutôt qu'un service tiers, le CDC n'en
imposant aucun. Configuration SMTP entièrement optionnelle
(`SMTP_HOTE` vide par défaut) : en son absence, l'envoi n'est pas tenté et
la notification en application reste créée normalement — journalisé et
enregistré sur la notification elle-même (`courriel_envoye=False`,
`courriel_erreur` explicite), jamais une réussite supposée en silence
(CLAUDE.md, point 9). Vérifié en conditions réelles : sans SMTP configuré,
le message d'erreur exact apparaît sur la notification.

**Compromis et écarts à signaler :**

1. **Destinataires « de rôle » diffusés à tous les titulaires du rôle**,
   jamais à un individu pré-assigné, sauf quand un champ le permet
   réellement (Action.responsable_id, Epi.porteur_id) : le tableau 3 dit
   "Responsable désigné" pour un permis en attente, mais PERMIS (dictionnaire
   7.2.7) ne modélise aucun champ de responsable assigné à l'avance — diffusé
   à tous les utilisateurs du rôle RESPONSABLE, même principe que pour les
   alertes EPI/documents (référent SHEQ).
2. **« Inspecteur désigné » (inspection planifiée) interprété comme le
   dernier inspecteur ayant réalisé une inspection du même couple
   (site, modèle)** : PLANIFICATION (section 5.3.1) n'est qu'une prévision
   calculée à partir de la périodicité, sans affectation d'inspecteur pour
   une inspection future non encore créée — aucun champ d'affectation
   n'existe pour ce cas. Interprétation la plus proche du texte faute de
   mieux, à confirmer avec le référent SHEQ.
3. **Rappels déclenchés par seuil, pas par jour exact** : un rappel "J-7" se
   déclenche dès que le nombre de jours restants passe sous sept (pas
   exactement à sept), grâce à la déduplication qui garantit un envoi
   unique par jalon. Plus robuste qu'une correspondance exacte : couvre les
   cas où le planificateur n'a pas tourné exactement au bon jour (redémarrage,
   objet créé avec moins de jours restants dès le départ).
4. **« Puis en retard » (actions) traité comme un jalon supplémentaire
   unique**, pas une répétition quotidienne tant que l'action reste en
   retard : le tableau 3 ne précise pas de fréquence pour ce cas, un rappel
   quotidien indéfini aurait été une interprétation extensive non demandée.
5. **Administrateur non ajouté comme destinataire supplémentaire** des
   alertes de rôle (référent SHEQ, responsable), contrairement au principe
   "Tout" habituellement appliqué aux permissions d'accès dans ce projet :
   une notification n'est pas un droit d'accès mais une charge de travail
   assignée, l'ajouter systématiquement aurait rendu le compteur de
   non-lues de l'administrateur artificiellement bruyant.
6. **Aucun envoi réel testé** (pas de serveur SMTP en environnement de
   développement) : le mécanisme d'envoi est vérifié par son échec
   correctement journalisé et exposé, pas par une livraison réelle — cohérent
   avec l'absence de spécification SMTP dans le CDC.
7. **Hors connexion non traité** (même limite que tous les prompts
   précédents).

**Vérifié en conditions réelles :** 228 tests pytest passent (217 précédents
+ 11 nouveaux), 3 toujours skippés (1.4) ; suite complète toujours rapide
(~83 s), confirmant que le planificateur ne s'exécute pas pendant les tests.
Migration `90df54758db3` testée en upgrade/downgrade/upgrade. Sur le serveur
de démo redémarré à neuf (avec un vrai utilisateur référent SHEQ créé pour
l'occasion, le compte admin seul ne suffisant pas à vérifier un
destinataire de rôle) : signalement créé via l'API réelle, notification
immédiatement visible pour le référent SHEQ, avec l'échec d'envoi de
courriel correctement enregistré (« SMTP non configuré... ») plutôt que
silencieusement ignoré.

### Détail — Prompt 5.1 (terminé le 2026-09-07)

**Écart signalé avant de coder, tranché par l'utilisateur** : le prompt
demande explicitement WeasyPrint. Vérification du CDC (chapitre 10.2,
tableau du socle technologique) : la ligne "Génération PDF" ne cite
WeasyPrint qu'à titre d'exemple parmi deux ("Bibliothèque Python, ex. :
WeasyPrint / ReportLab") — rien n'impose l'un plutôt que l'autre. ReportLab
déjà utilisé depuis le prompt 3.2 (fiches de configuration), retenu sans
dépendance système (WeasyPrint exige GTK/Cairo, pénible sous Windows,
l'environnement de développement de ce projet) — confirmé par l'utilisateur
avant tout code.

**Neuf types d'export** couverts, comme demandé : signalement (avec
sélection du modèle FOR-SHEQ-001 ou 002 selon `type`), SLAM, permis,
inspection, fiche de configuration (déjà livrée au prompt 3.2, seulement
refactorée pour réutiliser la nouvelle infrastructure partagée), rapport
d'audit, compte rendu de revue, tableau de bord. Nouvelle infrastructure
`app/core/pdf.py` (classe `DocumentPDF`) : en-tête commun, tableaux clé/valeur
et tableaux libres, pied de page avec date et auteur — un seul mécanisme
réutilisé par les huit générateurs, plutôt que du code dupliqué huit fois.

**Références ENR-SHEQ générées paresseusement pour quatre entités qui n'en
avaient jamais eu besoin** : EvaluationSlam, Inspection, CampagneAudit,
RevueDirection n'avaient aucune colonne `reference` avant ce prompt (Signalement,
Permis et Configuration ont déjà la leur, assignée à la création — inchangés).
Plutôt qu'une pseudo-référence dérivée de l'id technique (non conforme à
l'esprit du point 7 de CLAUDE.md, qui décrit une séquence par année), une
vraie séquence `ENR-SHEQ-AAAA-NNN` est attribuée et persistée au premier
export PDF (`app/services/reference_service.py`, migration `8c5e991840c5`,
`batch_alter_table`) — une séquence indépendante par table, comme celle déjà
en place pour CONFIGURATION depuis le prompt 3.2, pas un compteur global
partagé entre tous les types d'enregistrement.

**Compromis et écarts à signaler :**

1. **Le SLAM exporté reflète les 4×4=16 points réellement utilisés par
   l'application** (référentiel simplifié posé au prompt 2.2), pas les
   5+7+6+7=25 points du formulaire papier réel FOR-SHEQ-004 (extraction
   complète effectuée pour ce prompt) — écart déjà existant depuis le
   prompt 2.2/2.3, pas introduit par cet export : le PDF est fidèle aux
   données réellement saisies dans l'application.
2. **Tableau de bord sans référence ENR-SHEQ** : ce n'est pas un
   enregistrement individuel mais un instantané calculé, rien à numéroter
   — seuls la date de génération et l'auteur de la demande figurent, comme
   l'exige la traçabilité (règle 3, CLAUDE.md).
3. **Compte rendu de revue limité aux sections ayant un équivalent dans
   l'application** : sur les 8 sections réelles de FOR-SHEQ-016, les
   sections 3 (analyse des événements marquants), 6 (ressources et moyens)
   et 7 (opportunités d'amélioration) ne sont pas générées — rien à y
   afficher sans inventer un contenu, seules les sections 1, 2, 4, 5 et 8
   (déjà assemblées dans `donnees_entree` à la création de la revue, prompt
   4.2) sont exportées.
4. **Bug trouvé par inspection visuelle, pas par les tests automatisés** :
   les cellules de tableau contenant du texte long (ex. la liste des
   modules indisponibles du tableau de bord) débordaient de leur colonne au
   lieu de passer à la ligne — ReportLab ne retourne jamais une chaîne
   brute à la ligne dans une cellule de tableau, seul un objet `Paragraph`
   le permet. Corrigé dans `app/core/pdf.py` en enveloppant systématiquement
   chaque valeur de cellule dans un `Paragraph` plutôt qu'une chaîne — même
   catégorie de leçon que les chemins de fichiers Windows du prompt 1.3 :
   certains défauts ne se voient qu'en regardant le résultat réel.
5. **Hors connexion non traité** (même limite que tous les prompts
   précédents).

**Vérifié en conditions réelles :** 237 tests pytest passent (228 précédents
+ 9 nouveaux), 3 toujours skippés (1.4). Migration `8c5e991840c5` testée en
upgrade/downgrade/upgrade. Sur le serveur de démo redémarré à neuf, quatre
PDF générés et inspectés visuellement (pas seulement vérifiés par leur en-tête
`%PDF`) : SLAM (16 points réels, décision, pied de page), rapport d'audit
(22 exigences réelles réparties sur les 6 vrais chapitres, score 14/44 = 32 %
correctement calculé et interprété « Prioriser les écarts »), compte rendu
de revue (sections numérotées comme le formulaire réel, responsable de
décision résolu par son nom plutôt que son identifiant), tableau de bord
(bug de débordement de texte trouvé puis corrigé, revérifié après correction).

### Détail — Prompt 5.2 (rapport livré le 2026-09-07)

Revue de sécurité en mode critique, par investigation directe (greps de
couverture des dépendances d'authentification route par route, `pip list` +
recherche des CVE réelles par version exacte installée, test empirique du
comportement de ReportLab face à des entrées malformées plutôt que théorisé,
lecture complète de `app/core/deps.py`, `app/core/security.py`,
`frontend/src/stores/auth.js` et `frontend/src/services/api.js`). Consigne
explicite du prompt : **« ne corrige rien avant que je valide la liste »** —
strictement respectée, aucune modification de code pendant cette revue.

**Constats classés par gravité (rapport complet transmis à l'utilisateur en
conversation, non dupliqué ici in extenso) :**

- **Élevé** : CVE-2026-48710 (« BadHost », Starlette 0.8.3–1.0.0, version
  installée 0.46.2 dans la plage vulnérable, correctif 1.0.1) ; aucune route
  ne permet de désactiver un utilisateur existant (le contrôle `actif`/`archive`
  dans `get_current_user` est réel mais rien ne peut jamais le faire basculer
  via l'API) ; aucune limitation de tentatives sur `/auth/connexion`.
- **Moyen** : injection de balisage ReportLab dans les 8 générateurs PDF
  (confirmé empiriquement : `<b>` non fermé ou `&` brut font planter
  `Paragraph`) ; aucune validation de robustesse sur le mot de passe à la
  création d'un compte ; upload de fichiers validé sur des métadonnées
  fournies par le client (`Content-Type`, extension), pas sur le contenu réel.
- **Faible/informationnel** : `GET /slam/referentiel` sans authentification
  (seule route de toute l'API dans ce cas) ; jeton stocké en `localStorage`
  côté frontend (aucun vecteur XSS trouvé à ce jour) ; `refresh_token` émis
  mais jamais utilisé par le frontend ; CORS sain par défaut, à vérifier au
  déploiement ; coffre-fort non construit (3.3 toujours en attente de
  validation), revue possible seulement sur la conception.
- **Positif** : aucune injection SQL trouvée (requêtes paramétrées SQLAlchemy
  partout) ; couverture des droits cohérente sur 19 des 20 fichiers de routes ;
  pas de `debug=True` ; secrets jamais journalisés ; `.env` correctement
  exclu du dépôt ; `python-multipart` et `PyJWT` vérifiés sains contre leurs
  CVE connues.

**Aucune correction appliquée.** En attente de la validation de l'utilisateur
sur la liste avant toute intervention.

### Détail — Prompt 5.3 (terminé le 2026-09-07)

**Écart majeur découvert en cours de route, signalé avant de poursuivre** :
le routeur frontend (`frontend/src/router/index.js`) ne compte que 8 vues
pour 6 écrans réels (accueil, connexion, signalements, nouveau signalement,
SLAM, tableau de bord mobile/desktop, validation de permis), alors que 14
modules métier ont une API complète et testée côté serveur (risques, EPI,
équipements, configurations, inspections, formations, audits, revues,
documents, visiteurs, déchets, satisfaction, actions, notifications) sans
aucun écran correspondant. Question posée explicitement à l'utilisateur avant
de rédiger le manuel utilisateur plutôt que de deviner : réponse — documenter
l'existant réellement construit, avec captures d'écran réelles, et consigner
l'écart clairement plutôt que produire un manuel qui laisserait croire à une
couverture plus large que la réalité.

**Livré :**

1. **`README.md` complété** : sections installation/développement/tests déjà
   présentes, ajout des sections données de démonstration, manuel utilisateur,
   sauvegarde/restauration, déploiement en production.
2. **Documentation d'API** : vérification empirique que les descriptions
   générées par FastAPI étaient inexistantes (aucun docstring sur les 118
   fonctions de route à travers les 20 fichiers, résumés auto-générés
   inexploitables du type « Creer Utilisateur Route »— vérifié sur
   `/openapi.json` réel, pas supposé). Un docstring French concis a été ajouté
   à chaque route (118 fonctions, 20 fichiers), avec mention des règles
   métier non triviales là où c'est utile (règle de blocage des permis,
   rattachement unique d'une action à une origine, anonymat des signalements,
   workflow des documents, seuils de criticité des risques, etc.), plus une
   description globale sur `FastAPI(...)` (flux d'authentification JWT,
   matrice des rôles). Suite de tests repassée intégralement après coup :
   237 passés, 3 ignorés (1.4), aucune régression — travail délégué à un
   agent en arrière-plan avec un brief détaillé (règles métier fournies
   explicitement, pas laissées à sa charge de les redécouvrir), vérifié
   ensuite par relecture du diff.
3. **Manuel utilisateur** (`docs/MANUEL_UTILISATEUR.md`) : captures d'écran
   réelles (8 images, `docs/manuel/captures/`) prises sur l'application
   réellement démarrée (backend + frontend, jeu de données de démonstration),
   organisées par profil, avec la section « modules sans interface » en
   évidence plutôt qu'en fin de document noyée. Deux textes obsolètes trouvés
   en cours de capture et corrigés à cette occasion (voir point 6).
4. **Script de données de démonstration** (`backend/scripts/donnees_demo.py`) :
   peuple une base vide via l'API réelle (pas d'insertion SQL directe, sauf
   les 2 sites et le premier compte administrateur — aucune route `/sites`
   n'existe, et l'amorçage du premier administrateur n'a pas d'autre chemin
   possible). Refuse de s'exécuter si des utilisateurs existent déjà (garde-fou
   contre un lancement accidentel sur une base en service). Couvre la
   majorité des modules, y compris une démonstration délibérée de la règle
   de blocage des permis (un permis demandé sans évaluation SLAM préalable
   est effectivement bloqué). Testé de bout en bout sur une base SQLite
   vierge (migrations réelles + script), pas seulement écrit puis supposé
   correct.
5. **Sauvegarde et restauration** (`backend/scripts/sauvegarde.py`,
   `restaurer.py`) : sauvegarde la base (copie sûre SQLite via l'API backup
   de `sqlite3`, ou `pg_dump --format=custom` selon `DATABASE_URL`) et
   `storage/`, jamais `.env` (règle 4, CLAUDE.md — les secrets se conservent
   séparément). **Procédure testée de bout en bout** : base vivante peuplée,
   sauvegarde, incident simulé (ligne supprimée en base, fichier de storage
   effacé), restauration, vérification que les deux sont revenus à l'état
   sauvegardé. Le chemin PostgreSQL suit la même logique mais n'a pas pu être
   exercé : ni Docker ni PostgreSQL ne sont disponibles dans cet environnement
   de développement — signalé plutôt que tu par silence.
6. **Deux textes obsolètes corrigés dans le frontend**, trouvés en prenant les
   captures d'écran, pas cherchés a priori : l'écran d'accueil affichait
   encore « Squelette d'application initialisé — aucun module métier encore
   implémenté » (vrai au prompt 0.1, faux depuis) sans aucun lien vers la
   connexion ; l'écran de connexion affirmait « Vos saisies fonctionnent sans
   réseau et se synchronisent automatiquement » alors que le mode hors
   connexion n'est toujours pas implémenté (1.4) — un message contradictoire
   avec les avertissements honnêtes déjà présents sur les écrans SLAM et
   nouveau signalement. Les deux corrigés pour refléter l'état réel.
7. **`docker-compose.prod.yml` + `backend/Dockerfile.prod` +
   `frontend/Dockerfile`/`nginx.conf`** : images construites une fois (pas de
   montage du code source, pas de rechargement à chaud), frontend compilé et
   servi par Nginx avec repli SPA (`try_files`), aucune valeur par défaut pour
   les identifiants PostgreSQL (`${VAR:?message}` — échec explicite plutôt que
   mot de passe faible silencieux), port PostgreSQL non publié sur l'hôte.
   `.env.prod.example` documente chaque variable. **Non exécuté de bout en
   bout** : ni Docker ni PostgreSQL disponibles dans cet environnement — les
   Dockerfiles et le compose suivent les pratiques standard mais n'ont pas pu
   être testés par un `docker compose up` réel, contrairement au reste de ce
   prompt.
8. **`.gitignore` corrigé** : `.env.prod.example` aurait été silencieusement
   ignoré par le motif `.env.*` (seule l'exception `!.env.example` existait) —
   trouvé avant le premier commit, pas après coup.

**Compromis et écarts à signaler :**

1. **Le manuel utilisateur documente un tiers de l'application seulement**
   (6 écrans sur 20 modules) — décision explicite de l'utilisateur plutôt
   que supposée : documenter l'existant fidèlement plutôt que produire une
   spec fonctionnelle du reste.
2. **Aucun test frontend n'existe** (Vitest prévu par la pile technique,
   jamais utilisé) — signalé dans le manuel et le README, pas corrigé ici
   (hors périmètre de ce prompt, chantier à part entière).
3. **`docker-compose.prod.yml` non exécuté réellement** (environnement sans
   Docker) — voir point 7 ci-dessus.
4. **Identifiants bruts affichés côté écran** (`Utilisateur #4`, `Site #2`
   au lieu des noms) sur plusieurs vues — trouvé en prenant les captures,
   signalé dans le manuel, non corrigé (portée : résolution des identifiants
   en libellés, pas une simple faute de copie comme les deux textes du point
   6 — jugé hors périmètre de « documentation et déploiement »).
5. **Hors connexion (1.4) et coffre-fort (3.3) toujours non traités**, comme
   à chaque prompt précédent.

**Vérifié en conditions réelles :** 237 tests pytest passent (aucune
régression après l'ajout des docstrings). Backend et frontend démarrés
ensemble contre une base de démonstration dédiée (script testé), 8 écrans
visités et capturés dans un vrai navigateur (Playwright/patchright, pas une
simulation). Procédure de sauvegarde/restauration SQLite exécutée
intégralement avec vérification du contenu avant/après incident simulé.

## LOT 6 — Intelligence artificielle

### Détail — Prompt 6.1 (terminé le 2026-09-07)

**Écart de documentation découvert et tranché avant de coder** : le chapitre 16
du CDC (principes, tableau 10, architecture 16.3) n'existe que dans le CDC du
projet SMI-HIRONDELLE (`...-17.docx`), pas dans celui de sheq-management
(`docs/CDC-SHEQ-001.docx`, `...-19.docx`) — vérifié par extraction et
comparaison directe des deux documents (zipfile + regex sur `word/document.xml`,
pas une supposition). Les deux CDC ont divergé. Décision explicite de
l'utilisateur : utiliser le chapitre 16 de SMI-HIRONDELLE comme base de
conception pour sheq-management, sans le copier formellement dans le CDC de ce
projet. Fournisseur retenu pour les appels externes : **Anthropic** (décision
explicite, le CDC n'imposant aucun fournisseur — nouvelle dépendance signalée
avant d'écrire du code, conformément à CLAUDE.md).

**Conception présentée et validée avant codage** (comme le prompt l'exige
explicitement — "Attends ma validation") : module `backend/app/services/assistance/`
isolé (`client.py`/`journal.py`/`configuration.py`/`garde_fous.py`, point
d'entrée unique `__init__.py`), client HTTP avec délai maximal, réessai limité
à une fois, repli silencieux vers l'appelant (jamais d'exception) mais toujours
journalisé, journal d'appels sur le modèle de `JournalAcces` (écriture seule),
interrupteur général + mécanisme d'activation par fonction (aucune fonction
métier n'existe encore pour en tester la valeur réelle), plafond mensuel
optionnel, masquage déterministe des noms d'utilisateurs connus, refus
structurel de tout contenu `bytes` (seule donnée binaire de cette base : les
secrets chiffrés du coffre-fort).

**Deux bugs trouvés en écrivant les tests, pas supposés corrects** :

1. **Le CHECK constraint que je pensais devoir migrer n'existe pas.** Après
   avoir écrit une migration `batch_alter_table` pour étendre la contrainte
   CHECK de `notification.type` (nouvelle valeur `PLAFOND_ASSISTANCE`), une
   inspection directe du schéma SQLite réel (`sqlite_master`) a montré que la
   colonne `type` est un simple `VARCHAR` sans aucun CHECK — `enum_column()`
   (app/db/base.py) construit un `sa.Enum` sans `create_constraint=True`, et
   SQLAlchemy 2.x a `create_constraint=False` par défaut pour un type non
   natif. La migration inutile (elle ne cassait rien, mais reconstruisait la
   table sans raison, avec un commentaire qui aurait été faux) a été
   simplifiée : ajouter une valeur à `TypeNotification` ne nécessite aucun
   changement de schéma dans ce projet, seulement au niveau Python.
2. **La déduplication des notifications par contrainte unique ne fonctionnait
   pas pour l'alerte de plafond**, découvert par le test dédié
   (`test_plafond_depasse_alerte_les_administrateurs`), pas en le supposant
   acquis parce que le mécanisme existe déjà pour d'autres notifications. En
   SQL, une valeur NULL n'est jamais égale à une autre valeur NULL, y compris
   dans une contrainte UNIQUE multi-colonnes : laisser `objet_id` (ou
   `declencheur`) à `None` — ce que ma première version faisait, faute
   d'identifiant d'objet naturel pour une alerte mensuelle sans objet précis —
   désactive silencieusement toute déduplication pour CETTE notification
   précise (les huit notifications existantes du tableau 3 passent toutes un
   `objet_id` réel, ce bug ne les concerne pas). Corrigé en encodant le mois
   dans `objet_id` (ex. 202609) et en renseignant `declencheur` en plus.

**Compromis et écarts à signaler :**

1. **Le mécanisme d'activation par fonction ne peut pas encore être vérifié
   avec une vraie fonction** : `Settings` (Pydantic) refuse tout champ non
   déclaré, donc `fonction_activee("assistant_documentaire")` renvoie
   toujours `False` en pratique tant que le prompt 6.2 n'ajoute pas son
   propre champ `assistance_assistant_documentaire_active` — comportement
   voulu, testé avec un objet `settings` de substitution plutôt qu'avec le
   singleton réel (qui ne peut pas être étendu dynamiquement).
2. **Coûts estimés approximatifs** : les tarifs par million de jetons
   (`app/services/assistance/client.py`) sont des valeurs de départ, à
   vérifier une fois un usage réel facturé disponible — le CDC lui-même ne
   demande qu'un "coût estimé", pas une facturation exacte.
3. **Masquage des noms limité aux utilisateurs de l'application** : ne
   masque ni un visiteur, ni un tiers cité en texte libre, ni une variante
   orthographique — limite documentée dans le docstring de `masquer_noms`,
   pas cachée.
4. **Aucune route API** : ce prompt est un socle pur, sans aucune fonction
   métier ni endpoint exposé — conforme à la demande explicite du prompt
   ("sans aucune fonction métier pour l'instant").
5. **Gate du lot 6 non remplie** (voir l'avertissement en tête de section) —
   poursuite décidée explicitement par l'utilisateur.

**Vérifié en conditions réelles :** 256 tests pytest passent (237 précédents
+ 19 nouveaux), 3 toujours skippés (1.4), aucune régression. Migration
simplifiée testée en upgrade/downgrade/upgrade sur une base SQLite vierge.
Suite de tests dédiée couvrant explicitement les deux garanties demandées par
le prompt : le service indisponible (délai dépassé, erreur réseau, absence de
clé API) ne lève jamais d'exception et reste journalisé ; un contenu `bytes`
est refusé avant tout appel réseau, même transmis directement à la fonction
`appeler()`, sans jamais atteindre `httpx.post`.

### Détail — Prompt 6.2 (terminé le 2026-09-07)

Ordre du lot respecté cette fois (chapitre 16.6 : "assistant documentaire" en
premier) — voir la décision de l'utilisateur en réponse à la sélection directe
du prompt 6.3, qui sautait celui-ci.

**Blocage réel signalé avant de concevoir quoi que ce soit** : Anthropic
(fournisseur retenu au prompt 6.1) n'expose aucune API d'embeddings publique,
alors que 16.3.2 exige des "représentations vectorielles". Décision explicite
avec l'utilisateur : **Voyage AI**, partenaire d'embeddings recommandé par
Anthropic elle-même — deuxième clé API distincte (`ASSISTANCE_VOYAGE_API_CLE`),
deuxième fournisseur externe à isoler derrière le même principe du prompt 6.1
(aucun autre composant n'appelle directement le service).

**Conception présentée avant codage** (CLAUDE.md, "explique avant de coder
quand tu introduis un mécanisme nouveau" — le prompt 6.2 ne l'exige pas
explicitement comme le faisait 6.1, mais l'ampleur du mécanisme le justifiait
tout autant) : extraction de texte par format (python-docx/openpyxl/pypdf,
deux nouvelles dépendances signalées et justifiées), découpage en segments
par paragraphes groupés sous ~1500 caractères, recherche par similarité
cosinus calculée en Python (pas d'extension vectorielle SQLite/PostgreSQL —
36 documents ne le justifient pas), indexation déclenchée dans
`document_service.approuver()` (point d'accroche déjà identifié dans le code
existant : c'est exactement là que la version précédente passe en ARCHIVE).

**La garantie de non-réponse fiable ne dépend pas du modèle de génération** :
si aucun segment ne dépasse le seuil de similarité (0.3), la réponse
"la documentation en vigueur ne permet pas de répondre" est renvoyée
directement, sans même appeler Anthropic — testé explicitement
(`test_repondre_sans_segment_pertinent_ne_genere_pas_de_reponse`, qui vérifie
que le modèle de génération n'est jamais sollicité). Le CDC qualifie cette
garantie de "critère d'acceptation, pas un détail" (16.2.1) : une réponse
fiable à 100 % dans ce cas vaut mieux qu'une réponse probable selon la
docilité du modèle.

**Route ajoutée hors périmètre initial mais nécessaire** : `GET
/documents/{id}/fichier` n'existait pas — sans elle, "références cliquables"
(exigence explicite du prompt) n'avait aucune cible. Mêmes règles de
visibilité que la lecture du document (404, pas 403, pour un document non
visible).

**Interface mobile ET desktop**, comme demandé : nouvel onglet "Assistant"
ajouté aux trois écrans mobiles qui portent déjà la barre d'onglets
(Signalements, SLAM, Tableau de bord), nouveau lien dans l'en-tête du tableau
de bord desktop. Nouvelle icône SVG "bulle de discussion" ajoutée au sprite
(aucune icône de ce type n'existait). Les deux vues confirmées fonctionnelles
dans un vrai navigateur : formulaire soumis, réponse "indisponible" affichée
correctement (aucune clé configurée dans cet environnement) — zéro erreur
console, zéro requête en échec.

**Compromis et écarts à signaler :**

1. **Les 4 questions de test demandées par le prompt n'ont pas été posées à
   un vrai fournisseur.** Cet environnement de développement n'a ni
   `ASSISTANCE_API_CLE` ni `ASSISTANCE_VOYAGE_API_CLE` réelles (CLAUDE.md,
   point 10 : "aucun secret réel... dans le code, les tests ou les
   exemples") : la démonstration a été faite avec des appels externes
   simulés (`monkeypatch`), sur une logique de récupération et de découpage
   entièrement réelle. Pour poser réellement les 4 questions, renseigner les
   deux clés dans `backend/.env`, activer `ASSISTANCE_ACTIVEE` et
   `ASSISTANCE_ASSISTANT_DOCUMENTAIRE_ACTIVE`, approuver au moins un document
   réel avec un fichier joint, puis interroger `/assistant` ou
   `/api/v1/assistance/question-documentaire`.
2. **"Section" reste une approximation selon le format** : titre `Heading`
   pour un `.docx`, numéro de page pour un PDF, nom de feuille pour un
   `.xlsx` — pas une vraie structure sémantique du document, faute de
   modélisation de cette structure dans DOCUMENT.
3. **Tarifs Voyage/Anthropic approximatifs**, même réserve qu'au prompt 6.1 —
   à ajuster une fois une facturation réelle observée.
4. **Aucun mécanisme de retour utilisateur** ("signaler une suggestion
   inexacte", 16.4) — non demandé explicitement par le prompt 6.2 lui-même
   (contrairement à 16.4, qui couvre l'ensemble du lot), reporté à un prompt
   ultérieur si le besoin se confirme à l'usage.

**Vérifié en conditions réelles :** 275 tests pytest passent (256 précédents
+ 19 nouveaux), 3 toujours skippés (1.4), aucune régression. Migration
testée en upgrade/downgrade/upgrade. Extraction testée sur de vrais fichiers
`.docx`/`.xlsx` générés par python-docx/openpyxl dans les tests (pas des
fixtures binaires committées). Indexation testée de bout en bout via le vrai
cycle de vie d'un document (création → soumission → approbation → nouvelle
version → approbation), vérifiant que les segments de la version archivée
disparaissent réellement. Les deux écrans (mobile et desktop) visités dans un
vrai navigateur après démarrage réel des deux serveurs.

### Détail — Prompt 6.4 (terminé le 2026-09-07)

Sélection directe de l'utilisateur, sautant à nouveau le prompt 6.3 (analyse
assistée des causes). Décision cette fois assumée sans nouvelle question à
l'utilisateur (contrairement au saut 6.1→6.3) : contrairement à 6.3, qui
réutilise un patron d'interface "suggestion" que 6.2 aurait établi, 6.4 ne
dépend techniquement de rien qui serait apporté par 6.3 — il réutilise
uniquement le socle du prompt 6.1 (client Anthropic) et le workflow
brouillon/validation déjà présent dans DOCUMENT (prompt 4.3), sans lien avec
l'analyse des causes d'un signalement.

**Décision de conception** (pas de nouveau fournisseur ni dépendance, donc
pas de blocage à signaler comme aux prompts 6.1/6.2) : plutôt que de
construire un système de brouillon parallèle (calqué sur DOCUMENT), le
commentaire pré-rédigé est un champ texte directement sur REVUE_DIRECTION et
CAMPAGNE_AUDIT (`commentaire_ia`, `commentaire_valide`), avec sa propre
traçabilité en réutilisant simplement `modifie_par_id`/`modifie_le` déjà
fournis par BaseModel — plus proportionné qu'un artefact séparé pour "un
paragraphe de synthèse".

**Effet de bord positif** : la section 3 de FOR-SHEQ-016 ("analyse des
événements marquants"), explicitement laissée vide dans l'export PDF depuis
le prompt 5.1 ("rien à y afficher sans inventer un contenu" — compromis n°3
de ce prompt), est désormais remplie — par le commentaire validé, jamais
avant. Section "Synthèse" équivalente ajoutée au rapport d'audit (pas de gap
préexistant à combler côté FOR-SHEQ-017, section nouvelle).

**Vérifié directement, pas supposé** : le PDF exporté AVANT validation
n'inclut ni le titre de section ni le texte du commentaire (vérifié par
extraction réelle du texte du PDF via `pypdf`, pas seulement par lecture du
code) ; APRÈS validation, les deux apparaissent. Testé dans les deux sens
pour la revue, et pour l'inclusion côté audit.

**Démonstration demandée par le prompt, réalisée sur les données de
démonstration** (revue et campagne d'audit créées par
`backend/scripts/donnees_demo.py`, prompt 5.3) : commentaire généré (avec un
appel simulé — aucune clé API réelle disponible, même réserve qu'au prompt
6.2 — mais un texte plausible construit à partir des VRAIES données de la
base, jamais inventées), validé, puis exporté. Le PDF réel produit a été lu
et vérifié (section 3 "Analyse des événements marquants" pour la revue,
citant correctement les 4 réévaluations de risques et le taux d'avancement à
0 % réellement présents en base ; section "Synthèse" pour l'audit, citant le
score réel 2/4 = 50 %, interprétation "En construction").

**Compromis et écarts à signaler :**

1. **Démonstration avec un fournisseur simulé**, même réserve que le prompt
   6.2 : aucune clé Anthropic réelle dans cet environnement de
   développement (CLAUDE.md, point 10). Le mécanisme démontré (génération →
   brouillon → validation → apparition conditionnelle dans le PDF) est
   entièrement réel ; seul le texte du commentaire lui-même provient d'un
   appel simulé plutôt que d'un vrai modèle.
2. **Aucune interface (mobile/desktop) pour ce prompt** — non demandé
   explicitement par le texte du prompt 6.4 (contrairement à 6.2, qui exigeait
   "interface : champ de question sur mobile et desktop") : seules les routes
   API existent (`POST .../commentaire/generer`, `PATCH .../commentaire`,
   `POST .../commentaire/valider`, sur revues et audits). À construire si
   l'usage réel le justifie.
3. **`assistance_pre_redaction_active`** suit le même principe que les
   indicateurs par fonction précédents : désactivé par défaut, à activer
   explicitement une fois le budget arbitré (16.6).

**Vérifié en conditions réelles :** 285 tests pytest passent (275 précédents
+ 10 nouveaux), 3 toujours skippés (1.4), aucune régression. Migration
testée en upgrade/downgrade/upgrade sur base vierge, ET appliquée avec succès
sur la base de démonstration déjà peuplée (ligne de revue et de campagne
existantes — vérifie que l'ajout d'une colonne NOT NULL avec
`server_default` fonctionne réellement sur des lignes préexistantes, pas
seulement sur une table vide). Rapport de démonstration généré, lu et vérifié
page par page (texte extrait du PDF réel).

### Détail — Écrans EPI, prérequis de résolution de noms, écran Menu (terminé le 2026-09-07)

**Prérequis ajoutés avant l'écran lui-même** : aucune route ne permettait de
résoudre un `porteur_id`/`site_id` en nom affichable (lacune déjà signalée au
prompt 5.3, "Utilisateur #4"). Ajout de `GET /auth/utilisateurs` (ouvert à
tout authentifié — ces informations sont déjà visibles de tous dans
l'organisation papier) et `GET /sites` (nouveau fichier `app/schemas/site.py`,
`app/api/v1/sites.py` — aucune route SITE n'existait avant). Nécessaire pour
que l'écran EPI affiche un nom de porteur plutôt qu'un identifiant brut, et
pour tous les écrans à venir (permis, équipements, inspections référencent
tous un site ou un utilisateur).

**Écran Menu ajouté** (`/menu`, maquette `#s-menu`) : nécessaire dès ce
premier écran additionnel — la barre d'onglets fixe (5 destinations) ne peut
pas accueillir les 13 modules restants un par un. Sert de hub, un onglet
"Menu" (6ᵉ, icône grille) ajouté à tous les écrans mobiles existants. Seuls
les modules ayant réellement un écran y figurent (même principe que
SignalementsView.vue depuis le prompt 1.3 : "mieux vaut les omettre que
proposer des boutons qui ne mènent nulle part").

**EPI mobile (`/epi`, maquette `#s-epi`) et desktop (`/gestion/epi`, maquette
`#p-epi`)** : liste avec code couleur (rouge = vérification dépassée, orange
= J-7, vert = en service, gris = réformé/retiré), bannière d'alerte si des
EPI bloquent la délivrance d'un permis, action de vérification directement
sur chaque ligne (écart assumé face à la maquette, qui montre un bouton
unique en pied d'écran sans préciser l'écran suivant — une action directe par
ligne est plus rapide sur le terrain).

**Bug réel trouvé et corrigé en testant, pas en le supposant correct** :
`auth.utilisateur` (store Pinia) ne survit jamais à un rechargement de page —
seul `jeton` est persisté en `localStorage`. Avant ce prompt, aucun écran ne
lisait `auth.utilisateur.role` ou `.nom` de façon qui aurait révélé le
problème visuellement (TableauBordDesktopView affiche juste un nom vide sans
casser l'écran). L'écran Menu, qui masque conditionnellement "Tableau de
bord" selon le rôle, l'a rendu visible immédiatement (rôle affiché vide,
tuile manquante) — trouvé par une capture d'écran réelle après rechargement,
pas en relisant le code. Corrigé par `auth.chargerProfil()`, appelée depuis
le garde de navigation (`router.beforeEach`) chaque fois qu'un jeton existe
sans profil chargé ; un jeton devenu invalide déconnecte proprement plutôt
que de laisser un état incohérent indéfiniment.

**Accessibilité** : la ligne EPI cliquable (ouverture de l'action de
vérification) était un `<div>` sans `role`/`tabindex`, invisible à la navigation
clavier et aux lecteurs d'écran — trouvé en testant avec l'outil
d'accessibilité du navigateur automatisé (la ligne n'apparaissait pas dans
l'arbre des éléments interactifs), pas supposé correct. Corrigé
(`role="button"`, `tabindex`, gestion de la touche Entrée).

**Vérifié en conditions réelles**, pas seulement par lecture du code : les
deux serveurs réels démarrés (base de développement réelle de l'utilisateur,
pas une base de test), un EPI créé via l'API, testé dans un vrai navigateur —
navigation Menu → EPI, action "Conforme" cliquée réellement, vérifiée que la
règle "prochaine vérification = dernière + 12 mois" (règle 6, CLAUDE.md)
s'applique correctement (14/01/2026 dépassé → 06/09/2027 après vérification),
que la bannière d'alerte disparaît, que le porteur affiche "Démo Admin" et
non "Utilisateur #1". Aucune erreur console, aucune requête en échec, sur
les deux vues (mobile et desktop).

**Compromis à signaler** : l'action de vérification par ligne (plutôt que le
bouton unique de la maquette) est une interprétation, à confirmer avec
l'utilisateur si un écran de sélection dédié est finalement préféré. Pas de
pagination côté desktop (classe `.pagin` de la maquette non portée) — sans
conséquence à la volumétrie actuelle, à revoir si le parc d'EPI grossit.

### Détail — Écrans Risques, Actions, refonte desktop (terminé le 2026-09-07)

Décision explicite de l'utilisateur ("tu dois me construire tous les écrans") :
construction sans pause de confirmation entre modules, avec points d'étape
réguliers plutôt que des questions bloquantes.

**Refonte de l'ossature desktop, décidée en cours de route** : après EPI et
avant Risques, le constat que chaque écran desktop accumulait ses propres
boutons de navigation ad hoc (4 déjà après seulement 2 écrans) a conduit à
construire `GestionLayout.vue` — la vraie barre latérale de la maquette
(`.side`/`.nv`/`.navsec`), en pleine fenêtre plutôt que le cadre "prototype"
centré de la maquette (qui n'a de sens que pour la présenter, pas pour
l'usage réel). Toutes les routes `/gestion/*` sont maintenant des enfants de
ce layout (routes imbriquées Vue Router), avec un titre de page porté par
`meta.titre` plutôt que dupliqué dans chaque vue. Plusieurs classes CSS
`.bureau X` (scopées à l'ancien conteneur) ont été dé-scopées pour devenir
globales — sans quoi elles auraient cessé de s'appliquer aux écrans déjà
construits une fois `.bureau` retiré.

**Écrans Risques** (mobile `#s-risques`, desktop `#p-risk`) : matrice de
criticité 5×5 reconstruite à partir de `GET /risques/matrice` (la maquette la
peuple par script, sans markup de référence), formulaire de création avec les
12 catégories réelles, réutilisé tel quel entre mobile et desktop plutôt que
dupliqué avec un style distinct.

**Écran Actions** (mobile `#s-actions`, desktop `#p-act`) : filtres
Toutes/En retard/Les miennes, avancement modifiable en ligne, clôture directe.
Création limitée à une origine "risque" (`ActionCreation` exige exactement
une origine parmi risque/signalement/inspection/écart d'audit/réponse de
satisfaction — seul "risque" a un écran assez avancé pour y accrocher un
sélecteur pour l'instant).

**Deux bugs réels trouvés en testant, pas supposés corrects :**

1. **La matrice de criticité ne s'affichait pas en grille** : `.mtx`/`.ax`
   avaient été utilisées dans le template sans jamais être portées dans
   `style.css` — les 25 cases s'alignaient sur une seule ligne. Trouvé par
   capture d'écran réelle (le texte seul, extrait sans mise en page, ne
   l'aurait pas révélé), pas par relecture du code.
2. **Décalage d'un jour sur toute date civile affichée** (échéances
   d'action, dates de vérification EPI) : `new Date("2026-10-15")` est
   interprété comme un instant UTC minuit par le constructeur `Date`, puis
   reformaté dans le fuseau local par `toLocaleDateString()` — un décalage
   d'un jour selon le fuseau du navigateur. Trouvé en créant une vraie action
   avec une échéance réelle (15/10 saisi, 14/10 affiché), pas en relisant le
   code. Ce bug touchait potentiellement tous les écrans avec une date de
   type `date` (pas `datetime`) : `EpiView`/`EpiDesktopView`
   (vérifications), `TableauBordDesktopView` (échéances proches), en plus
   d'`ActionsView`/`ActionsDesktopView`. Corrigé partout avec un utilitaire
   partagé (`frontend/src/utils/dates.js`, `formaterDateCivile`/
   `joursRestantsCivil`) plutôt que patché au cas par cas — à réutiliser pour
   tout futur champ `date` plutôt que réintroduire le bug.

**Compromis à signaler :**

1. Formulaire de création d'action limité à l'origine "risque" (voir
   ci-dessus).
2. Tableau de bord toujours honnête sur ses limites, mais son message
   "Indisponibles pour l'instant, faute de module : epi..." est désormais
   partiellement obsolète (EPI a un écran) — c'est un indicateur backend
   (`tableau_bord_service.py`) distinct de la présence d'un écran, non
   corrigé ici (hors périmètre de "construire les écrans", plutôt "étendre
   les indicateurs du tableau de bord").

**Vérifié en conditions réelles** sur la vraie base de développement de
l'utilisateur (pas une base de test) : un risque créé (P4×G5, criticité 20
calculée côté serveur), une action créée et rattachée, avancement mis à
jour, échéance affichée correctement après correction du bug de fuseau,
navigation complète testée dans un vrai navigateur (Menu → Risques → Actions,
sidebar desktop entre les 4 écrans). 289 tests pytest toujours au vert
(aucune régression backend, ce chantier est entièrement frontend).

### Détail — Écran Visiteurs (terminé le 2026-09-07)

**Écrans Visiteurs** (mobile `/visiteurs`, desktop `/gestion/visiteurs`) :
enregistrement d'arrivée (nom, motif, société facultative, personne visitée,
case obligatoire "consignes lues"), liste des personnes présentes sur site,
enregistrement de départ. Ajoutés à `MenuView.vue` et à la barre latérale de
`GestionLayout.vue`.

**Bug réel trouvé en testant, pas supposé correct :** en soumettant le
formulaire sans cocher la case des consignes, le serveur rejette bien la
création (`HTTP 422`, le validateur Pydantic `_consignes_obligatoires` de
`VisiteurCreation` l'exige) — c'est le comportement attendu côté serveur.
Mais le message d'erreur affiché à l'écran était le texte littéral
`[object Object]` au lieu du message. Cause : FastAPI renvoie le détail
d'une erreur de validation Pydantic sous forme de liste d'objets
(`{"detail": [{"loc":..., "msg":..., "type":...}]}`), pas une chaîne — et
`ErreurApi` (`frontend/src/services/api.js`) passait ce détail tel quel à
`Error.message`, qui n'est censé être qu'une chaîne. Corrigé à la source
(nouvelle fonction `extraireMessage()` dans `api.js`, appelée par `requete()`)
plutôt que dans chaque écran : gère les 3 formes possibles de `detail`
renvoyées par FastAPI (chaîne, liste d'erreurs de validation, objet unique).
Ce bug touchait potentiellement tout formulaire pouvant déclencher un 422 de
validation Pydantic (pas seulement Visiteurs) — corrigé une fois pour toutes
au niveau du client API commun. Vérifié en conditions réelles : le message
affiché est maintenant "Value error, les consignes de sécurité doivent être
lues et validées avant tout enregistrement".

**Vérifié en conditions réelles** sur la vraie base de développement : un
visiteur enregistré avec succès une fois la case cochée (affiché en liste
"présents sur site" avec heure d'arrivée), rejet propre et lisible sans la
case. 289 tests pytest toujours au vert (aucune régression backend, ce
chantier est entièrement frontend).

### Détail — Écran Déchets (terminé le 2026-09-07)

**Écrans Déchets** (mobile `/dechets`, desktop `/gestion/dechets`) : registre
des lots de déchets (date, type, description, quantité, site, filière —
tous des champs texte libre côté backend, le registre réel n'impose pas de
liste fermée), enregistrement d'un enlèvement (date + justificatif optionnel
côté desktop admin plus tard si besoin, non exposé dans ce formulaire).

**Compromis à signaler :** le 4e indicateur de la maquette desktop
("Incidents environnement") n'a aucune entité backend dédiée — affiché figé à
0 avec une note explicite plutôt qu'une fausse donnée dynamique.

**Vérifié en conditions réelles** : un lot DEEE créé (2 routeurs HS, câbles,
1 onduleur, 14 kg, Siège Bamako), passage "en stock" → "tracé" via
l'enregistrement d'un enlèvement, date d'enlèvement affichée sans décalage de
fuseau (07/09/2026, correspondant au jour réel du test), cohérence entre
écran mobile et desktop (même lot visible des deux côtés, mêmes totaux).
289 tests pytest toujours au vert (aucune régression backend, ce chantier
reste entièrement frontend — seules les routes déjà existantes `GET/POST
/dechets` et `POST /dechets/{id}/enlevement` ont été consommées).

### Détail — Écran Satisfaction (terminé le 2026-09-07)

**Deux écrans, pas un seul**, reflet direct de la distinction CDC 11.1
"deux interfaces, deux usages" : le questionnaire (`#s-satis`) est un écran
**public**, sans authentification, accessible par lien/QR code envoyé au
client (`/satisfaction/:jeton` — route ajoutée hors du préfixe `/gestion` et
sans `meta.necessiteAuth`) ; le pilotage (`#p-satis`, moyenne, retours à
analyser, enquêtes envoyées, création d'enquête) est un écran de gestion
desktop (`/gestion/satisfaction`), réservé au personnel. Aucun écran mobile
interne : la maquette n'en prévoit pas, cohérent avec le reste de l'app
(le pilotage est desktop, la saisie terrain est mobile — la satisfaction
n'est ni l'un ni l'autre côté staff, c'est un envoi + un traitement).

**Écarts assumés :**
1. Le vrai référentiel (`CRITERES`, satisfaction_service.py) a 6 critères,
   pas 3 comme dans le fragment de maquette — rendus dynamiquement à partir
   de `GET /questionnaire/{jeton}`.
2. `ReponseEntree` exige une `recommandation` (3 valeurs FOR-SHEQ-018) que le
   fragment de maquette ne montre pas explicitement — ajoutée comme un choix
   à 3 boutons, seule façon de satisfaire ce champ obligatoire du vrai schéma.
3. **Nouvelle route backend** `GET /satisfaction/reponses` (+ service
   `lister_reponses`, + 2 tests) : aucune route existante ne renvoie
   l'ensemble des réponses (seulement `/a-traiter`, filtrée aux notes ≤ 2) —
   sans elle, la moyenne de satisfaction affichée sur l'écran de pilotage
   n'aurait pu être calculée qu'à partir d'un sous-ensemble biaisé (que les
   mauvaises notes), ce qui aurait été trompeur plutôt qu'un vrai compromis.
   Moyennes (globale et par critère) calculées côté client, aucune agrégation
   de ce type n'existant côté serveur.

**Bug réel trouvé en testant, pas supposé correct :** l'écran desktop
restait entièrement blanc (aucune erreur console, aucune requête en échec —
silence total), alors que Visiteurs et Déchets, construits juste avant avec
le même patron, s'affichaient normalement. Cause : le getter Pinia
`moyenneGlobale` était écrit `(state, getters) => …` en supposant, par
réflexe Vuex, qu'un second paramètre `getters` est passé aux getters —
**Pinia ne fait pas ça** : un getter accède aux autres getters via `this`, ce
qui exige une fonction normale (pas fléchée, `this` ne s'y lie pas). Le
getter plantait donc silencieusement (`Cannot read properties of undefined`)
à chaque rendu, et Vue n'a rien signalé sur la console dans ce cas précis —
trouvé uniquement en comparant le rendu réel de trois écrans construits côté
à côté avec le même patron, pas par relecture du code seul. Corrigé en
`moyenneGlobale() { return …this.moyenneParCritere… }`.

**Deuxième bug, plus mineur, trouvé au même endroit :** les bascules
"Nouvelle enquête" (Satisfaction) et "Nouvel enregistrement" (Déchets) sont
des `<span>` avec `@click`, sans `role="button"`/`tabindex` — invisibles à
l'arbre d'accessibilité (et donc au clavier/lecteur d'écran), même défaut que
la ligne EPI cliquable corrigée plus tôt dans ce chantier. Corrigé sur les
deux écrans, plus la puce "À planifier" de Déchets (même défaut, oubliée
lors de la première passe).

**Vérifié en conditions réelles**, bout en bout, sur la vraie base de
développement : une enquête créée depuis l'écran desktop (client "Client
Test Satisfaction", intervention "Maintenance PtP"), lien public généré et
ouvert dans un navigateur sans session authentifiée, questionnaire rempli
(5 critères à des notes hautes, 1 à 2/5 — "Respect des délais annoncés"),
recommandation "Probablement" et un commentaire, soumis avec succès
("Merci pour votre retour"). Revenu sur l'écran desktop : moyenne globale
4,3/5 recalculée correctement (moyenne de 5,2,5,5,4,5), barre par critère
juste, alerte "1 réponse à 2 étoiles ou moins" déclenchée (seuil réel
`SEUIL_ALERTE_NOTE = 2` du backend), ligne de la table à jour ("Répondu",
"4,3 / 5", "Analyse requise"). 291 tests pytest au vert (289 + 2 nouveaux
pour `GET /satisfaction/reponses`), aucune régression.

### Détail — Cloche de notifications (terminé le 2026-09-07)

Ni la maquette mobile ni la desktop ne contiennent d'écran dédié aux
notifications (aucun `id="s-notif"`/`id="p-notif"` dans les 41 écrans) —
seulement un bouton d'en-tête (icône cloche + point) : `.hd .act .ib` en
mobile (maquette v2, ligne 299, écran `#s-home`), `.gestion-top .ib` en
desktop (maquette Desktop, ligne 244, présent sur toutes les pages). Ce
n'est donc pas un "écran manquant" au même titre que les modules précédents,
mais un élément transverse resté inutilisé jusqu'ici (icône `i-bell` présente
dans le sprite depuis un prompt antérieur, jamais montée nulle part).

**Construit :** `NotificationsCloche.vue`, un composant unique monté aux deux
endroits où la maquette montre le bouton — l'en-tête de Signalements (écran
d'atterrissage mobile réel de l'app, `#s-home` avec son "Bonjour, {prénom}"
n'ayant jamais été construit, voir lot 1) et l'en-tête de `GestionLayout.vue`
(présent sur les 13 écrans desktop d'un coup, une seule insertion). Un clic
ouvre un panneau déroulant listant `GET /notifications` — absent des deux
maquettes (qui ne montrent que le bouton statique) mais nécessaire pour que
la cloche serve à quelque chose plutôt que d'être décorative ; construit dans
le langage visuel existant (`.card`-like) plutôt qu'improvisé. Clic sur une
notification → `POST /{id}/lue` ; "Tout marquer comme lu" → `POST
/toutes-lues`. Aucune route backend n'a été ajoutée : les 5 existantes
(prompt 4.4) couvraient déjà exactement ce besoin.

**Vérifié en conditions réelles**, avec un compromis assumé pour y parvenir :
la base de développement ne contenait qu'un seul compte (`admin`), et les
notifications réelles (ex. `notifier_satisfaction_faible`) ne ciblent que
`referent_sheq`/`responsable` — impossible à observer avec un seul compte
administrateur. Un compte fictif `referent.test` / `Referent-Test-2026!` a
été créé via `POST /auth/utilisateurs` (même principe que le compte `admin`
déjà documenté pour les tests manuels — voir plus haut dans ce journal),
uniquement pour cette vérification. Une enquête de satisfaction notée 1/5 sur
tous les critères a bien généré la notification attendue, visible dans la
cloche de ce compte : badge rouge sur le bouton, message "Note de
satisfaction client faible (≤ 2/5) : une analyse est requise" avec date/heure
correcte, bascule vers l'état "lu" au clic (disparition du fond navy-soft,
disparition du badge), testé en mobile et en desktop. 291 tests pytest
toujours au vert (aucune modification backend pour ce module).

### Détail — Permis / SLAM & permis (terminé le 2026-09-07)

**Aucune des deux maquettes n'a d'écran de "liste" ou de "demande" de
permis** — seul `#s-permis` existe, et c'est la vue responsable de
validation (déjà construite au prompt 2.3, `PermisValidationView.vue`). Le
seul point d'entrée maquette est la tuile "SLAM & permis" du menu mobile, qui
ne menait qu'au stepper SLAM (`SlamView.vue`) : sans écran de demande,
`POST /permis` — avec sa vraie règle de blocage (EPI conforme, SLAM GO par
intervenant, surveillant désigné et distinct des intervenants) — restait
inatteignable depuis l'interface, alors que la route existe depuis le
prompt 2.2. Construits ici, en reprenant le langage visuel déjà établi
(métriques + liste + formulaire repliable, comme Risques/Déchets) plutôt
qu'inventés sans référence :
- mobile `/permis` (`PermisView.vue`) : compteurs "en cours"/"en attente",
  liste des permis (clic → l'écran de validation existant, inchangé),
  formulaire de demande (site, nature des travaux, support, hauteur
  estimée, créneau, intervenants à cocher, surveillant facultatif) ;
- desktop `/gestion/permis` (`PermisDesktopView.vue`), calqué sur
  `#p-hauteur` : 4 métriques, table des permis, table "Décisions SLAM
  récentes" (absente d'API jusqu'ici, voir ci-dessous), même formulaire de
  demande que côté mobile.

La tuile mobile "SLAM & permis" est repartie en deux tuiles distinctes
("SLAM" → stepper, "Permis" → ce nouvel écran) : la conserver unique aurait
laissé la moitié de son intitulé sans destination.

**Nouvelle route backend** `GET /slam` (+ service `lister_toutes`, + 2
tests) : seule `/slam/mes-evaluations` existait (scopée à l'appelant) — la
table "Décisions SLAM récentes" de `#p-hauteur` montre les décisions de
*tous* les intervenants, impossible à construire sans une vue d'ensemble.
Réservée aux rôles de pilotage (`CONSULTER_TABLEAU_BORD`, identiques au
tableau de bord), par cohérence avec le reste de l'écran plutôt qu'ouverte à
tout utilisateur comme `/mes-evaluations`.

**Bug réel trouvé en testant, pas supposé correct :** l'écran desktop a
d'abord affiché "Method Not Allowed" à la place des métriques (`GET /slam`
renvoyait 405). Cause : le serveur de développement tournait avec
`--reload`, qui a bien rechargé après la modification de
`evaluation_slam_service.py` (nouvelle fonction `lister_toutes`) mais n'a
**jamais rechargé** après la modification suivante de
`app/api/v1/evaluations_slam.py` (l'enregistrement de la route elle-même) —
confirmé en relisant le journal du serveur (`WatchFiles detected changes`
apparaît une seule fois pour toute la session, pas deux). La suite de tests
pytest, elle, importe l'application à chaque exécution et ne pouvait pas
révéler ce décalage — seul un test contre le vrai serveur de développement,
déjà démarré, l'a montré. Corrigé en arrêtant et relançant uvicorn
proprement plutôt qu'en comptant sur le rechargement automatique.

**Vérifié en conditions réelles**, bout en bout : une demande de permis
créée depuis le mobile (référence réelle générée par le serveur, "2026-001"),
visible immédiatement avec le bon site, le bon créneau et le tag "À
valider" ; clic sur la ligne → ouverture de l'écran de validation existant,
qui affiche correctement les 4 contrôles automatiques à partir des
véritables données du compte utilisé pour le test. Revérifié côté desktop :
mêmes données, plus le panneau "Décisions SLAM récentes" peuplé par la
nouvelle route. 293 tests pytest au vert (291 + 2 nouveaux pour `GET
/slam`), aucune régression.

### Détail — Gestion des utilisateurs (terminé le 2026-09-07)

Dernier écran de ce chantier, hors Coffre-fort (toujours bloqué, aucun
service backend). Desktop uniquement (`/gestion/utilisateurs`) — aucun
équivalent mobile, l'administration des comptes n'étant un usage ni terrain
ni "deux minutes suffisent" ; l'écran n'apparaît dans la barre latérale que
pour le rôle `administrateur` (nouvelle section `roles` sur `GestionLayout.vue`,
généralisable aux futurs écrans à accès restreint).

**Deux nouvelles routes backend**, seule vraie lacune structurelle de ce
chantier (signalée dès le début, avant même de commencer à construire des
écrans) : `POST /auth/utilisateurs/{id}/desactiver` et `.../activer` (+
service `desactiver_utilisateur`/`activer_utilisateur`, + 5 tests). Aucune
suppression physique (point 2, CLAUDE.md) : bascule du seul champ `actif`,
le compte et son historique restent en base. Règle ajoutée et testée : un
administrateur ne peut pas désactiver son propre compte (sans quoi un admin
seul en base se verrouillerait lui-même dehors).

**Écart assumé sur la "Matrice des droits par rôle"** : la maquette en
montre une version fine, par module (illustrative — ni lue depuis
`core/permissions.py`, qui n'est exposé par aucune route, ni garantie de
correspondre exactement aux permissions réelles). Remplacée par le tableau
"Rôles et périmètres" de CLAUDE.md (section 6), moins granulaire mais tiré
d'une source de vérité réelle plutôt que d'un exemple de maquette. Colonne
"Appareil" (Web/Mobile) également omise : rien ne trace ça côté backend.

**Bug réel trouvé en testant, pas supposé correct :** la colonne "Dernière
connexion" affichait "Jamais connecté" pour un compte qui venait de se
connecter à l'instant. Cause : `derniere_connexion` existe bien sur le
modèle `Utilisateur` et se met à jour à chaque connexion (`auth.py`), mais
`UtilisateurSortie` (le schéma de sortie de `GET /auth/utilisateurs`) ne
l'exposait tout simplement pas — la donnée existait, seule sa sortie API
manquait. Corrigé en l'ajoutant au schéma (+ 1 test vérifiant qu'elle n'est
plus `null` juste après une connexion). Trouvé en lisant l'écran réellement
peuplé de vraies données (le compte `admin`, connecté des dizaines de fois
au cours de ce chantier, affichant pourtant "Jamais connecté"), pas en
relisant le schéma seul.

**Vérifié en conditions réelles**, bout en bout, avec le compte fictif
`referent.test` créé plus tôt (voir "Détail — Cloche de notifications") :
désactivation refusée sur son propre compte ("Vous ne pouvez pas désactiver
votre propre compte", lisible grâce à la correction `[object Object]` de
Visiteurs — un bug corrigé une fois profite à tous les écrans qui l'auraient
sinon reproduit), désactivation réussie sur l'autre compte (bascule
immédiate "Actifs · 1 / Désactivés · 1"), compte désactivé retrouvé dans
l'onglet "Désactivés" avec un bouton "Réactiver", réactivation réussie
("Actifs · 2 / Désactivés · 0"), dates de dernière connexion réelles et
correctement affichées pour les deux comptes. 298 tests pytest au vert (293
+ 4 pour désactiver/activer/refus/404 + 1 pour `derniere_connexion`
exposée), aucune régression.

---

**Bilan de ce chantier** ("construire tous les écrans") : Visiteurs, Déchets,
Satisfaction, Notifications, Permis / SLAM & permis, Utilisateurs — tous
terminés le 2026-09-07, en plus d'EPI, Risques, Actions, Parc, Formations,
Audits/Revues et Documents construits plus tôt dans la même journée (voir
détails plus haut). Seul Coffre-fort reste hors périmètre, explicitement
bloqué depuis le début (aucun service backend, prompt 3.3 toujours en
attente de validation). Chaque écran a été vérifié en conditions réelles,
sur la vraie base de développement, dans un vrai navigateur — pas seulement
relu : cette discipline a permis de trouver et corriger, en cours de route,
7 bugs réels indépendants du simple manque d'écran (matrice de criticité non
grillée, décalage d'un jour sur les dates civiles, `[object Object]` sur les
erreurs 422, un getter Pinia mal écrit qui plantait un écran en silence,
plusieurs éléments cliquables invisibles à l'accessibilité, un rechargement
automatique du serveur de dev resté incomplet, et une donnée réelle absente
d'un schéma de sortie). 298 tests pytest au vert, aucune régression.

---

## Module Documents — catalogue réel du SMI (2026-09-07)

Demande explicite de l'utilisateur, après consultation de l'écran Documents
fraîchement construit : "je voudrais que ce module reflète l'architecture
réelle de mon système SMI de Hirondelle avec les documents qu'il faut". Le
seul document présent jusqu'ici était un test fictif créé pendant la
vérification du module (`POL-SHEQ-002 Politique environnementale`, un code
qui n'existe même pas dans le vrai système).

**Sources consultées** : `docs/CDC-SHEQ-001.docx` (§1.1, tableau §5.3.5) —
insuffisant seul (regroupe plusieurs codes par ligne, ex. "FOR-SHEQ-006 à
009", sans détailler chaque titre) — puis, sur indication de l'utilisateur,
l'archive `SMI-HIRONDELLE/SMI-SHEQ_Hirondelles_IT_Lab-20.zip` : le vrai
classeur SMI (01-Politique_et_engagement, 02-Pilotage, 03-Procédures,
04-Formulaires_vierges dont un sous-dossier CONFIDENTIEL, 09-Archives), avec
en particulier `LM-SHEQ-001_Liste_Maitresse_Documents.xlsx` — la vraie liste
maîtresse elle-même, table faisant autorité avec les 36 lignes exactes
(code, intitulé, niveau, format, version, rédacteur, approbateur,
emplacement, confidentialité, prochaine revue). A permis de combler tous les
trous laissés par le seul CDC : PLA-SHEQ-002 (Plan de sauvetage en hauteur,
classé niveau 3 malgré son préfixe PLA), PRO-SHEQ-001/003/005 (Gestion des
signalements, Sauvegarde des configurations, Achat et réception du
matériel), REG-SHEQ-003 (Registre EPI antichute, confirmé), FOR-SHEQ-003
(Fiche d'accueil sécurité — code qui n'apparaît nulle part dans le CDC lui-
même), FOR-SHEQ-010/011 (Inspection équipements / Checklists locaux-
incendie-électricité) et FOR-SHEQ-013 (Vérification harnais/EPI, distinct du
permis FOR-SHEQ-012).

**Seed via l'API réelle, pas d'insertion directe en base** (script
`seed_smi_reel.py`, one-off, non versionné) : chaque document suit le vrai
cycle `POST /documents` (brouillon) → `soumettre-approbation` →
`approuver`, avec les vrais rôles habilités — `GERER_DOCUMENTS` (créer,
soumettre) et `APPROUVER_DOCUMENTS` (approuver) ne sont pas les mêmes rôles.

**Comptes réels créés** (`POST /auth/utilisateurs`, mots de passe fictifs de
développement) : Oumou DIARRA (`o.diarra`, référent SHEQ — rédactrice/
soumissionnaire des 36 documents, rôle habilité à `GERER_DOCUMENTS`),
Alassane TRAORÉ (`a.traore`, administrateur — approbateur des 36, rôle
habilité à `APPROUVER_DOCUMENTS`), Abdoulaye KONÉ (`a.kone`, technicien).
**Compromis assumé** : la liste maîtresse crédite Abdoulaye KONÉ comme
co-rédacteur de chaque document, à égalité avec Oumou Diarra ; mais son rôle
réel (technicien) n'a pas le droit `GERER_DOCUMENTS`, et `Document.
redacteur_id` n'accepte qu'un seul auteur — impossible de représenter fidèlement
une corédaction dans ce modèle. Oumou Diarra a été retenue comme rédactrice
de tous les documents (seule des deux dont le rôle le permet), la
co-rédaction réelle de M. Koné n'étant pas représentable sans changement de
modèle (hors périmètre de cette demande).

**Vrais fichiers joints**, pas seulement les métadonnées : chaque document a
reçu son vrai fichier `.docx`/`.xlsx` du classeur SMI comme pièce jointe
(`POST /documents` accepte un fichier, formats et taille max déjà prévus
pour "Word/Excel/PDF, formats réels du SMI documentaire" — commentaire déjà
présent dans `core/fichiers.py` avant ce chantier). Les 4 fiches de
configuration confidentielles (FOR-SHEQ-006 à 009) sont de vrais formulaires
vierges (aucun identifiant réel dedans, juste la structure — dossier nommé
"04-Formulaires_vierges" à raison) : sans risque à joindre, `backend/
storage/` est déjà exclu de Git.

**Historique de versions réel pour FOR-SHEQ-006** (seul document dont la
liste maîtresse indique une version autre que 01) : les 3 vrais fichiers du
dossier `09-Archives` et `CONFIDENTIEL` ont servi à reconstituer l'historique
exact via `nouvelle-version` (v01 générique → v02 détaillée → v03,
confidentielle, en vigueur), chaque étape passant par le vrai workflow
d'approbation. La règle "l'ancienne version part en archive à l'approbation
de la nouvelle" (5.3.5, déjà implémentée) a fait le travail : v01 et v02
sont automatiquement repassées en `archive`, sans intervention manuelle sur
leur statut.

**Nettoyage** : l'ancien document de test (`POL-SHEQ-002`) est repassé en
`archive` directement en base (script one-off de maintenance, pas une
fonctionnalité de suppression ajoutée à l'application — aucune route de
suppression physique n'existe ni ne doit exister, point 2 de CLAUDE.md).

**Vérifié en conditions réelles** : les deux écrans (mobile `/documents`,
desktop `/gestion/documents`) affichent maintenant les 36 documents réels
(39 lignes avec l'historique FOR-SHEQ-006 et l'archive de test), codes et
intitulés exacts, bon niveau (1 Politique, 2 Pilotage — dont les 5 registres,
3 Procédure — dont PLA-SHEQ-002, 4 Formulaire), bonne version, bon statut.
Téléchargement d'un fichier réel confirmé : `GET /documents/{id}/fichier`
renvoie exactement 10226 octets pour POL-SHEQ-001, taille identique à
l'original du zip, type MIME Word correct. 298 tests pytest toujours au
vert (aucune modification du code applicatif, seed de données uniquement).

---

## Documents en sous-dossiers réels + module Inspections (2026-09-07)

Deux demandes explicites de l'utilisateur dans le même message : "le module
Document doit avoir des sous dossier comme dans le SMI et chaque fichier
serait dans son dossier" et "les écrans pour les inspections aussi doit
être réalisé" — Inspections avait un backend complet depuis le prompt 2.4
(`/inspections`, `/points-checklist`) mais aucun écran, jamais signalé dans
le chantier "construire tous les écrans" (oubli de ma part : ni Risques ni
Inspections n'étaient dans la liste initiale du chantier, seul Risques avait
été rattrapé).

### Documents — classement par dossier réel

Aucun champ "dossier" sur `Document` (backend) — le classement dérive
entièrement de trois champs déjà là (`niveau`, `confidentialite`, `statut`),
exactement comme le fait le classeur réel (`SMI-SHEQ_Hirondelles_IT_Lab/
LISEZ-MOI.txt` : niveau 1 → 01-Politique, niveau 4 confidentiel → 04.../
CONFIDENTIEL, une version retirée → 09-Archives). Nouveau fichier
`utils/dossiersDocuments.js` (`DOSSIERS`, `dossierDe()`) partagé par les
deux écrans, pas de nouveau champ en base à tenir synchronisé.

Les 4 dossiers du classeur réel sans registre applicatif (05-Enregistrements,
06-Formations, 07-Revues, 08-Réglementation — confirmés vides par
`LISEZ-MOI.txt` de chacun) sont listés quand même, à 0, avec une note
explicative : la structure réelle complète doit être visible, pas seulement
les dossiers qui ont des lignes en base aujourd'hui.

**Mobile** : nouvel écran `DocumentsView.vue` transformé en navigateur de
dossiers (dix lignes, une par dossier, avec compteur) ; nouvel écran
`DocumentsDossierView.vue` (route `/documents/:dossier`) reprenant le rendu
par ligne de l'ancien écran plat, désormais filtré. **Desktop** : dix
filtres segmentés (`.seg`, déjà utilisé par Parc/Utilisateurs) plutôt qu'une
arborescence à ouvrir/fermer — plus cohérent avec le paradigme "tableaux
denses, filtres" déjà établi côté gestion.

**Vérifié en conditions réelles** sur les 39 documents déjà seedés (chantier
précédent) : répartition exacte 01→1, 02→11, 03→6, 04→14, 04/CONFIDENTIEL→4,
05-08→0, 09→3 (somme = 39, cohérent). Filtre "04 · CONFIDENTIEL" du desktop
vérifié : montre exactement FOR-SHEQ-006 à 009, rien d'autre.

**Bug réel trouvé en testant, pas supposé correct :** les onglets desktop
utilisaient `d.nom.split(" · ")[0]` pour un libellé court — "04 ·
Formulaires vierges" et "04 · Formulaires vierges / CONFIDENTIEL"
devenaient tous deux "04", indiscernables. Corrigé en ajoutant un champ
`abrege` dédié à chaque dossier plutôt qu'en découpant un libellé long à
l'affichage.

### Inspections — nouveau module (mobile + desktop)

Aucune maquette de "liste" ou de "démarrage" (seul `#s-insp` existe : la
fiche de saisie d'une inspection déjà en cours, "Incendie & extincteurs").
Construits en reprenant le langage déjà établi (métriques + liste +
formulaire, comme Permis/Déchets) : sans ces écrans, `POST /inspections`
restait inatteignable depuis l'interface malgré un backend complet et
5 vrais référentiels de checklist déjà seedés (locaux 15 points, incendie 14,
électricité 13, installations 25, équipements 26 — prompt 2.4).

**Écart de conception notable** : `InspectionCreation.points` exige au moins
un point coté — impossible de créer l'inspection avant la première réponse
(contrairement à Audits, où "ouvrir une campagne" ne demande aucune
cotation). Résolu par une création paresseuse : l'écran de saisie
(`InspectionDetailView.vue`) affiche la checklist complète, non cotée,
dès l'arrivée sur `/inspections/nouvelle?modele=...&site_id=...` ; le
premier clic sur un point déclenche `POST /inspections` (avec seulement ce
point), puis `router.replace` vers `/inspections/:id` (l'URL réelle) ; les
clics suivants envoient `PATCH /points` avec l'état complet des réponses —
ce endpoint remplace le tableau entier, ne fusionne pas (service
`mettre_a_jour_points`), point déjà découvert en lisant le code avant
d'écrire l'écran plutôt qu'en le devinant à l'usage.

**Deux écrans mobiles** : `InspectionsView.vue` (liste + "à planifier" +
démarrage) et `InspectionDetailView.vue` (checklist tri-état C/NC/SO,
photo sur un point NC, "Terminer et signer"). **Desktop**
`InspectionsDesktopView.vue` (maquette `#p-insp` : conformité par type en
barres, planification, table "Inspections réalisées") — le clic sur une
ligne réutilise l'écran mobile de saisie, même compromis que Parc.

**Bug réel trouvé en testant, pas supposé correct (le plus sérieux de ce
tour) :** l'upload de photo sur un point non conforme renvoyait 200 avec
`photo` toujours à `null` — vérifié faux jusqu'au niveau de la table SQLite
elle-même, pas une illusion de cache ORM. Cause : `ajouter_photo`
(`inspection_service.py`) faisait `points = list(inspection.points)` avant
de muter un point en place puis réassigner — `list()` ne copie que la liste
externe, les dictionnaires internes restent des références PARTAGÉES avec
l'objet suivi par la session SQLAlchemy. Les muter en place corrompt l'état
"avant" que SQLAlchemy compare à l'état "après" à la réassignation : les
deux deviennent identiques (mêmes dictionnaires, déjà mutés), donc perçus
comme "rien n'a changé" — aucun `UPDATE` n'est jamais émis, confirmé en
activant l'écho SQL (`BEGIN` puis `SELECT` puis `COMMIT`, sans `UPDATE`
entre les deux). `mettre_a_jour_points` n'a pas ce défaut : il reconstruit
des dictionnaires neufs via `_construire_points_json`, jamais de référence
partagée avec l'ancienne valeur — c'est justement pourquoi le reste du
module (cotation, clôture, calcul du taux) fonctionnait correctement
pendant que la photo, seule, échouait silencieusement. Corrigé en
reconstruisant des dictionnaires neufs (`[dict(p) for p in
inspection.points]`) avant toute mutation. Aucun autre endroit du code ne
reproduit ce motif (`grep` sur `= list(\w+\.\w+)` dans tout `app/` : un seul
résultat, déjà corrigé) ; `Document.accuses_lecture` utilise le même style
`list(...)` mais seulement pour *ajouter* un élément neuf, jamais pour
muter un élément existant — non affecté, vérifié par le raisonnement plutôt
que supposé sans preuve. Test de non-régression ajouté
(`test_photo_deposee_sur_un_point_est_persistee`), qui relit l'inspection
par une requête séparée après l'upload plutôt que de se fier à la seule
réponse HTTP — exactement le doute qui aurait détecté le bug plus tôt.

**Deuxième bug réel, plus mineur** : `Inspection.taux_conformite` (API) est
une fraction 0-1 (`conformes / total`), pas un pourcentage — utilisé tel
quel dans les nouveaux écrans (`${taux}%`), ce qui affichait "1 %" au lieu
de "50 %". Trouvé en lisant l'écran desktop rempli de vraies données, pas
en relisant le code (la valeur "1 %" est plausible en apparence, seule la
comparaison avec le calcul manuel — 1 conforme sur 2 cotés — la révèle
fausse). Corrigé par un helper `pourcent()` local à chaque écran
(`stores/inspections.js` pour l'agrégat par type, `InspectionsView.vue` et
`InspectionsDesktopView.vue` pour l'affichage ligne par ligne) — même
défaut que le sprite d'onglets desktop tronqués (voir Documents ci-dessus,
"04" × 2) : construit et testé le même jour, retrouvé deux fois de suite.

**Vérifié en conditions réelles**, bout en bout : une inspection "Incendie
et extincteurs" démarrée depuis le mobile (site réel), 3 points cotés
(C, NC, SO) sur les 14 réels de FOR-SHEQ-011, conformité 50 % correcte
(1 conforme / 2 cotés, SO exclu du dénominateur — règle 6, CLAUDE.md),
photo réelle jointe au point NC (confirmée par une lecture séparée après
l'upload, pas seulement la réponse HTTP), clôture réussie avec génération
automatique d'une action corrective portant le bon libellé. Revérifié côté
desktop : mêmes données, filtres par type fonctionnels, plus de doublon
"Installations" dans les onglets après correction. 299 tests pytest au vert
(298 + 1 nouveau pour la persistance de la photo), aucune régression.

---

## Tableau de bord synchronisé + retrait des traces de développement (2026-09-08)

Retour direct de l'utilisateur après usage réel de l'application : "le
tableau de bord n'est pas synchronisé aux données réelles et dans certains
écrans de l'application on sent que l'application a été développée par
l'IA — j'aimerais que nous soyons beaucoup plus professionnelle". Deux
problèmes concrets, tous deux confirmés en relisant le code AVANT de coder
quoi que ce soit :

### Tableau de bord — indicateurs réels au lieu de "module indisponible"

`tableau_bord_service.py` datait du prompt 1.5 (lot 1, avant même EPI) :
`MODULES_NON_DISPONIBLES` listait encore `epi, inspections, formations,
documents, environnement, satisfaction, coffre_fort` — six de ces sept
modules ont un écran et des données réelles depuis le chantier du
2026-09-07 (Documents/Inspections) et le chantier précédent, mais le
service n'avait jamais été mis à jour pour les exploiter. Les deux écrans
affichaient donc, en direct, un bandeau lisant "Indisponibles pour
l'instant, faute de module : epi, inspections, formations, documents..." —
une affirmation fausse pour six modules sur sept, visible de tout
utilisateur du tableau de bord.

**Nouveaux indicateurs réels**, calculés sur les mêmes données que l'écran
de chaque module (jamais une valeur recalculée séparément qui pourrait
diverger) : `securite` (accidents et presque-accidents de la période,
jours sans accident — depuis Signalement.type), `inspections` (réalisées
sur la période, taux de conformité moyen — depuis Inspection, réutilise le
calcul déjà existant), `epi` (à vérifier bientôt / dépassées — réutilise
`epi_service.verifications_dues`), `formations` (personnel formé sur
total, séances à venir — depuis Habilitation), `documents` (à réviser
bientôt / en attente d'approbation — réutilise `document_service.
alertes_revue`), `satisfaction` (réclamations = notes ≤ 2 sur la période,
note moyenne). `echeances_proches` n'est plus une simple liste d'actions :
fusion de quatre sources (actions, vérifications EPI, révisions
documentaires, séances à venir) triée par proximité, comme le montre
réellement la maquette `#p-dash` ("Échéances proches" y mélange EPI,
formation et document, jamais seulement des actions).

**Seuls deux indicateurs restent sans module source**, réellement cette
fois : incidents environnementaux (aucune entité de suivi dédiée) et
sécurité des données (coffre-fort, toujours bloqué). `MODULES_NON_
DISPONIBLES` réduit à ces deux-là — et n'est plus jamais montré à
l'utilisateur (voir section suivante).

**Bug réel trouvé en écrivant le test, avant même de tester dans le
navigateur** : `_securite()` plantait avec `TypeError: can't subtract
offset-naive and offset-aware datetimes` dès qu'un accident existait en
base. Cause : SQLite renvoie un datetime naïf même pour une colonne
`DateTime(timezone=True)` (contrairement à PostgreSQL) — `datetime.now
(timezone.utc) - dernier_accident` échouait dès que `dernier_accident`
provenait d'une lecture SQLite. Corrigé en ajoutant `tzinfo=timezone.utc`
à la valeur lue si elle est naïve (toutes les dates de l'application sont
écrites en UTC, donc naïve signifie UTC, jamais l'heure locale du serveur).
Un test dédié aurait immédiatement révélé ce bug en production sur
PostgreSQL vs silencieusement fonctionné en développement sur SQLite —
exactement le genre d'écart entre les deux moteurs que l'ORM est censé
lisser, ici pris en défaut.

**Sept nouveaux tests** couvrant chaque indicateur individuellement plus le
mélange des échéances par proximité (pas par type ni par ordre
d'insertion) ; le test existant sur `modules_non_disponibles` corrigé pour
refléter la nouvelle réalité (2 modules, pas 7).

### Retrait des traces de développement visibles par l'utilisateur

En cherchant d'autres écrans avec le même défaut que le bandeau du tableau
de bord (un message qui parle du développement de l'application plutôt que
de l'application elle-même), quatre autres bannières se sont révélées bien
pires — des références explicites au processus de développement, montrées
telles quelles à l'utilisateur final :

- `SlamView.vue` : "Le mode hors connexion n'est pas encore actif pour le
  SLAM **(prompt 1.4 non implémenté)**..." — un numéro de prompt de
  développement affiché dans l'application en production.
- `NouveauSignalementView.vue` : "...n'est pas encore actif **— il arrive
  au prompt suivant**." — une référence directe à la feuille de route de
  développement.
- `ParcView.vue` : "...ils vont au coffre-fort **(non disponible pour
  l'instant)**." — reformulé en une affirmation simple sur l'architecture
  ("sont conservés dans le coffre-fort chiffré"), sans commentaire sur
  l'état d'avancement.
- `MenuView.vue` : "Le coffre-fort **a une API fonctionnelle** mais pas
  encore d'écran." — du jargon backend (API) exposé à un utilisateur final,
  reformulé en "n'est pas encore accessible depuis l'application".

Ces quatre bannières ont été écrites au fil des prompts précédents pour
documenter honnêtement, À DESTINATION DE L'UTILISATEUR DU PROJET (l'auteur
des prompts), les écarts et le calendrier restant — une habitude saine
pendant le développement, mais qui n'a pas sa place dans l'interface une
fois l'application utilisée en conditions réelles : ce niveau de détail
appartient à `docs/JOURNAL.md`, pas à une bannière visible de tout
utilisateur final. Recherche systématique (`grep` sur "prompt [0-9]",
"compromis", "écart assumé", "JOURNAL.md" dans tous les fichiers `.vue`) :
aucune autre occurrence trouvée en dehors des commentaires de code
(invisibles, légitimes — c'est là qu'ils doivent rester).

**Vérifié en conditions réelles** : les deux tableaux de bord affichent
maintenant des valeurs réelles et cohérentes avec les autres écrans (50 %
de conformité inspections, correspondant à l'inspection réellement clôturée
plus tôt ; 2 réclamations à note moyenne 2,7/5, correspondant aux réponses
de satisfaction déjà enregistrées) ; export PDF revérifié (200, contenu
réel) ; les quatre bannières corrigées affichent un texte propre, sans
jargon ni référence interne, en conditions réelles dans le navigateur.
306 tests pytest au vert (299 + 7 nouveaux pour le tableau de bord), aucune
régression.

---

## Coffre-fort d'identifiants (2026-09-08)

Dernier module resté en pause depuis le 2026-09-06 ("conception présentée,
en attente de validation avant codage — comme convenu pour un module aussi
sensible"). L'utilisateur a explicitement redemandé à en discuter ("selon
toi comment on doit procéder") : plan présenté à nouveau (chiffrement,
visibilité par secret, masquage à la demande, génération de mot de passe,
deux points tranchés avec sa confirmation — voir ci-dessous), validé
("Alors on fait cela") avant d'écrire la moindre ligne de code, conformément
au point 9 de CLAUDE.md ("explique avant de coder... un mécanisme
nouveau : chiffrement").

**Beaucoup de fondations existaient déjà**, retrouvées en relisant le code
avant de commencer : le modèle `Secret` (chapitre 7.2.8), le modèle
`JournalAcces` — délibérément privé de la classe de base commune pour
qu'aucune route de modification ne puisse jamais lui être ajoutée par
erreur —, `FERNET_MASTER_KEY` déjà prévue dans `.env.example` avec sa
commande de génération, et les tables `secret`/`journal_acces` déjà
présentes dans la base de développement. Le service de chiffrement, la
logique métier et les écrans restaient entièrement à construire.

**Chiffrement** (`app/core/chiffrement.py`) : Fernet (`cryptography`),
authentifié (AES-128-CBC + HMAC-SHA256). Échoue au chargement du module si
`FERNET_MASTER_KEY` est absente ou mal formée — jamais de mode dégradé
silencieux sur un module sensible (`Settings.fernet_master_key` était déjà
un champ obligatoire sans valeur par défaut, donc l'absence totale de clé
faisait déjà échouer le démarrage de l'API ; l'erreur explicite ajoutée ici
couvre le cas d'une clé présente mais invalide).

**Visibilité par secret, pas par permission globale**
(`secret_service.py`, `NIVEAU_ROLE_SECRET`) : chaque secret porte un
`role_requis` (technicien/responsable/administrateur, seuls rôles que le
CDC mentionne pour ce module) comparé au rôle de l'appelant via une
hiérarchie propre à ce module — jamais `RoleUtilisateur.__members__` tel
quel, pour que le référent SHEQ et le collaborateur restent exclus même si
l'ordre de déclaration de l'énuméré changeait. `peut_consulter()` renvoie
`False` pour tout rôle absent de cette hiérarchie : un secret dont
`role_requis` serait mal renseigné n'est visible de personne plutôt que de
tout le monde par défaut (fail-safe). `role_requis` est validé côté schéma
(`ROLES_SECRET_VALIDES`) : impossible de créer un secret réservé au
référent SHEQ ou au collaborateur, qui serait alors invisible de tous.

**Consultation = déchiffrement + journalisation, jamais l'un sans l'autre**
(`consulter_secret()`) : les deux opérations sont dans la même fonction,
qui ne renvoie la valeur qu'après avoir ajouté la ligne au journal — aucun
chemin de code ne peut renvoyer un secret en clair sans laisser de trace.
Idem pour la création et la modification (`ActionJournal.CREATION` /
`MODIFICATION`), au-delà de la seule exigence du CDC ("toute consultation
est enregistrée") : traçabilité complète plutôt que le minimum demandé,
cohérent avec le point 3 de CLAUDE.md.

**Deux points tranchés avec l'utilisateur avant de coder, confirmés tels
quels** :
1. Seule la valeur du secret est chiffrée, pas le champ `identifiant`
   (login) — le CDC les liste comme deux champs distincts ("identifiant,
   secret chiffré"), l'identifiant seul n'étant pas sensible.
2. Le journal des accès à un secret est réservé aux mêmes rôles que sa
   gestion (responsable + administrateur, nouvelle permission
   `CONSULTER_JOURNAL_SECRETS`) — le CDC ne précise pas qui peut le
   consulter, seulement qu'il existe.

**Écart assumé, différent de la maquette** : `#p-vault` montre un journal
global (tous secrets confondus). Le CDC (5.2.4, "Fonctionnalités
attendues") est plus précis : "Consulter le journal des accès **à un
secret donné**" — singulier. La route backend suit ce texte
(`GET /secrets/{id}/journal`, pas de route d'agrégation) ; le panneau de
droite du desktop affiche donc le journal du secret sélectionné (clic sur
une ligne), pas un flux global — fidèle au texte du CDC plutôt qu'à
l'aspect exact de la maquette sur ce point précis.

**22 tests** couvrant : création (responsable/administrateur autorisés,
technicien et référent SHEQ refusés), validation de `role_requis`, la
liste qui ne renvoie jamais la valeur, consultation qui déchiffre ET
journalise, visibilité par secret dans les deux sens (un technicien ne voit
ni la fiche ni ne peut consulter un secret réservé au responsable ; il voit
et consulte normalement un secret qui lui est ouvert), l'exclusion totale
du référent SHEQ et du collaborateur (même sur le secret le moins
restrictif), modification, archivage (jamais de suppression — le journal
survit à l'archivage du secret), rattachement à un équipement réel,
génération de mot de passe (longueur, présence de lettres/chiffres/
symboles), absence de toute route DELETE (sur les secrets et sur le
journal), et — vérification directe en base — que la valeur chiffrée ne
contient jamais le texte en clair.

**Écrans** : mobile `/coffre-fort` (liste masquée par défaut, affichage à
la demande avec masquage automatique après 15 secondes — cohérent avec la
maquette et la valeur par défaut du service ; formulaire d'ajout avec
génération de mot de passe intégrée) ; desktop `/gestion/coffre-fort`
(table + panneau "Journal des accès" au clic sur une ligne). Le lien
"Coffre-fort" est masqué du menu mobile et de la barre latérale desktop
pour le référent SHEQ et le collaborateur — pas montré puis vide, cohérent
avec le principe déjà appliqué à "Utilisateurs & rôles" (visible du seul
administrateur). Le bandeau du Parc, qui renvoyait vers un coffre-fort
inexistant depuis le début du chantier "construire tous les écrans", pointe
maintenant réellement vers l'écran (lien "Ouvrir" de la maquette mobile,
jamais câblé jusqu'ici) — masqué lui aussi pour le référent SHEQ.

**Vérifié en conditions réelles**, bout en bout, avec les comptes déjà
créés durant ce chantier (admin/administrateur, o.diarra/référent SHEQ) :
un secret créé avec un mot de passe généré par le bouton "Générer"
(20 caractères, lettres/chiffres/symboles réels) ; affiché à la demande —
la valeur exacte générée à la création réapparaît, confirmant le
chiffrement/déchiffrement réel, pas une simulation ; masquage automatique
confirmé après une attente réelle de 15 secondes dans le navigateur (pas
supposé, chronométré) ; journal desktop affichant les 3 vraies entrées
(création, 2 consultations) avec le nom résolu de l'utilisateur et
l'horodatage exact ; connecté ensuite en référent SHEQ : tuile absente du
menu, accès direct par URL renvoyant une liste vide sans erreur (pas de
fuite d'existence), bandeau Parc sans lien "Ouvrir". 328 tests pytest au
vert (306 + 22 nouveaux), aucune régression.

## Type de signalement incomplet — écran "accidents" introuvable (2026-09-08)

**Retour direct de l'utilisateur** : "je ne vois pas l'écran des
accidents". Il n'existe pas d'écran séparé pour les accidents dans le
modèle de données (`SIGNALEMENT` couvre les 5 valeurs du CDC — situation
dangereuse, presque-accident, anomalie matérielle, incident, accident —
chapitre 7.2.3), mais le formulaire "Nouveau signalement" n'exposait que
les 3 premières, recopiées de la maquette (`#s-newsig`) sans plus : un
écart déjà noté en commentaire ("à trancher") lors de la construction
initiale de l'écran, jamais réglé depuis. Résultat concret : aucun
signalement de type incident ou accident ne pouvait jamais être créé nulle
part dans l'application, alors même que l'API et la base les acceptaient
depuis le début — et que le nouveau tableau de bord (entrée précédente,
même journée) calcule désormais un indicateur "accidents" à partir de ce
même champ, resté bloqué à 0 sans aucun moyen de le tester.

**Décision** : la maquette était incomplète sur ce point, pas
l'application — les 5 valeurs réelles du dictionnaire de données sont
maintenant toutes proposées dans le sélecteur "Type" du formulaire.
Ajouté dans la foulée, ce qui manquait pour que ce champ serve à quelque
chose une fois saisi :
- **Liste des signalements** : le type était invisible (seul le statut
  l'était) — ajouté en première position de chaque ligne, en rouge gras
  pour "Accident" afin qu'il ressorte visuellement dans une liste souvent
  longue.
- **Filtre par type** : une deuxième rangée d'onglets (Tous les types /
  Situation dangereuse / Presque-accident / Anomalie / Incident /
  Accident), combinée au filtre par statut déjà existant. La route
  `GET /signalements` acceptait déjà `type` en paramètre côté API depuis
  le lot 1 — jamais exploité côté écran jusqu'ici.

**Bug introduit puis corrigé pendant ce correctif** : l'édition du
commentaire d'en-tête de `NouveauSignalementView.vue` a supprimé par
erreur le `*/` fermant le bloc JSDoc, cassant la compilation Vite
(`Unterminated comment`, erreur 500 sur l'écran). Repéré immédiatement au
test navigateur (page blanche, log Vite explicite) et corrigé avant toute
vérification fonctionnelle.

**Vérifié en conditions réelles**, bout en bout, connecté en admin : les 5
boutons de type s'affichent sur `/signalements/nouveau` ; un signalement
de type Accident créé (lieu "Pylône P-12, secteur nord") obtient sa
référence réelle (`SIG-2026-001`, attribuée par le serveur) et apparaît
dans `/signalements` avec le badge "Accident" en rouge ; le filtre
"Situation dangereuse" appliqué ensuite renvoie bien 0 résultat (exclusion
correcte, pas un simple masquage visuel) ; le tableau de bord affiche
"1 accidents" immédiatement après création, confirmant que l'indicateur
lit réellement ce champ. 328 tests pytest au vert, aucune régression (le
correctif est entièrement frontend, aucun fichier backend modifié).

## Mode hors connexion — file d'attente et synchronisation automatique (2026-09-08)

**Contexte** : contrainte fondatrice n°1 du CLAUDE.md ("le mode hors
connexion est une exigence, pas une option"), jamais construite jusqu'ici —
`BandeauReseau.vue` le disait lui-même en commentaire ("ce mécanisme est le
prompt 1.4, pas celui-ci"), et le formulaire de signalement affichait un
avertissement explicite ("une connexion est nécessaire pour envoyer ce
signalement"). Demande directe de l'utilisateur ("comment connecter le
mobile au desktop et synchroniser les données"), clarifiée en échange avant
de coder : les écrans mobile et desktop sont déjà une seule application
connectée à la même API et à la même base — rien à "connecter" de ce
côté-là — mais le vrai mode hors connexion terrain, lui, restait à
construire. Discuté puis confirmé avant tout code, comme pour le
coffre-fort.

**Mécanisme, générique dès le départ** (pas seulement pour les
signalements — pensé pour être réutilisé par SLAM et Inspections, mêmes
besoins terrain) :
- `services/filesync.js` (nouveau) : file d'attente dans IndexedDB (aucune
  dépendance ajoutée, API native du navigateur). `ajouterEnAttente(type,
  champs, fichiers)` range un élément avec référence provisoire locale ;
  `synchroniser(gestionnaires)` rejoue chaque élément en attente dans
  l'ordre de saisie, un `gestionnaire` par type métier (`executer`,
  `onSucces`).
- `stores/horsConnexion.js` (nouveau) : orchestration Pinia — compteur
  d'éléments en attente, écoute de l'événement `online` pour synchroniser
  automatiquement, registre de gestionnaires rempli une seule fois dans
  `main.js` (pour qu'aucun store métier n'ait besoin d'importer un autre
  store métier).
- `stores/signalements.js` : `creer()` extrait désormais l'envoi réel dans
  `envoyerVersServeur()` (rejouable tel quel par la file) ; si l'échec est
  une erreur réseau (`TypeError` de fetch, pas un refus serveur), l'élément
  part en file au lieu de faire échouer la saisie. Un vrai refus serveur
  (422, 401…) continue de remonter normalement — une nouvelle tentative
  donnerait le même résultat, la file ne doit pas les avaler.
- `SignalementsView.vue` : un signalement en attente affiche un statut
  dédié "EN ATTENTE DE RÉSEAU" (icône `sync`), distinct des vrais statuts
  serveur, et ne compte dans aucun onglet de statut (`nombreParStatut`)
  tant qu'il n'est pas confirmé.
- `BandeauReseau.vue` : le sous-texte de droite (`.sp` dans la maquette,
  jusqu'ici jamais rempli) affiche maintenant réellement "N élément(s) en
  attente" hors ligne, et "Synchronisé à l'instant / il y a N min" en
  ligne — vocabulaire repris tel quel de la maquette.
- Écran pilote : Signalements — cas d'usage le plus critique du CDC
  (technicien sur un pylône, zéro réseau) et l'écran où l'avertissement
  existait déjà.

**Bug réel trouvé et corrigé pendant la vérification** (pas seulement une
supposition — repéré par un test en coupure réseau simulée réelle, pas une
simple lecture de code) : la mise en file échouait systématiquement avec
`DataCloneError: [object Array] could not be cloned`. Cause : `photos`
transmis à `ajouterEnAttente` est un tableau réactif Vue (`ref([])`, donc
un Proxy) — la valeur de retour de `photos.value` reste un Proxy même
vide, et l'algorithme de clonage structuré d'IndexedDB ne sait pas cloner
un Proxy (les fichiers qu'il contient ne sont pas concernés, Vue ne les
rend pas réactifs). Corrigé dans `filesync.js` en copiant `champs` et
`fichiers` en objets/tableaux plats (`{ ...champs }`,
`Array.from(fichiers)`) avant de les ranger — centralisé une fois pour
toutes les futures files d'attente, pas seulement celle des signalements.

**Vérifié en conditions réelles**, coupure réseau simulée au niveau du
navigateur (`context.setOffline`, pas une simple lecture de
`navigator.onLine`) : signalement saisi hors ligne → apparaît
immédiatement dans la liste avec réf. provisoire et statut "EN ATTENTE DE
RÉSEAU", bandeau affichant "Hors connexion · 1 élément en attente" ;
retour du réseau (événement `online` réel) → synchronisation automatique
sans action de l'utilisateur, référence réelle attribuée par le serveur
(`SIG-2026-00x`), statut redevenu "NOUVEAU", bandeau "En ligne ·
Synchronisé à l'instant". Répété trois fois de suite (y compris après
redémarrage à froid du serveur de développement), résultat identique à
chaque fois.

**Ce que ça ne couvre pas encore** : SLAM et Inspections ont le même
besoin terrain mais ne sont pas encore branchés sur `horsConnexion.js` —
le mécanisme est prêt à les recevoir (même registre de gestionnaires),
mais chaque module a sa propre forme de données à adapter, donc un chantier
séparé plutôt qu'un embarquement silencieux ici. Pas de gestion de conflit
au-delà de l'ordre de saisie (non nécessaire ici : chaque élément en file
est une création indépendante, jamais une modification d'un enregistrement
existant). Pas de test Vitest ajouté : le projet n'a jamais eu de suite
Vitest jusqu'ici (aucun fichier `*.test.js` dans `frontend/`) — introduire
IndexedDB en environnement de test (nécessiterait `fake-indexeddb`, une
dépendance non demandée) pour un premier test isolé aurait été disproportionné ;
la vérification s'est donc faite en conditions réelles, comme pour tous les
écrans de ce chantier jusqu'ici.

## Points critiques relevés le 2026-09-08 — traitement en cours

Retour direct de l'utilisateur ("quels sont les points critiques de cette
application", puis "on corrige tous ces points") après un état des lieux
honnête, six points classés par gravité : (1) jeton d'accès sans
rafraîchissement, (2) coffre-fort/authentification jamais revus en
sécurité malgré l'exigence explicite du CLAUDE.md point 10, (3) jamais
testé sur PostgreSQL malgré une divergence déjà connue avec SQLite
(datetime naïf), (4) mode hors connexion limité aux signalements, (5)
aucun test frontend automatisé, (6) aucune sauvegarde de base de données.
Traités un par un, dans cet ordre.

### Point 1 — rafraîchissement automatique du jeton d'accès

**Constat** : `jwt_access_token_expire_minutes = 15` (config.py). Le
backend générait déjà un couple access/refresh token et exposait
`POST /auth/rafraichissement` (prompt 0.3) — jamais utilisés côté
frontend, qui stockait uniquement l'access token et laissait n'importe
quel écran échouer sur un 401 générique après 15 minutes. Aggravant
concret découvert en construisant le mode hors connexion la veille : un
401 sur un signalement (session expirée) n'est PAS une erreur réseau —
avec la logique alors en place (`e instanceof TypeError`), il ne partait
pas en file, il échouait juste avec "Envoi impossible, réessayez",
trompeur puisque ce n'était pas vraiment le problème.

**Corrigé, entièrement côté frontend** (le backend avait déjà tout) :
- `services/api.js` : stockage du refresh token à côté de l'access token ;
  `requete()` intercepte un 401 sur une requête qui portait un jeton,
  tente un rafraîchissement silencieux via `/auth/rafraichissement`
  (dédoublonné — une seule vraie tentative même si plusieurs requêtes
  échouent en même temps), puis rejoue la requête d'origine une fois
  (`_relance`, jamais deux fois : pas de boucle). Si le rafraîchissement
  échoue aussi (refresh token expiré/absent), les deux jetons sont
  effacés et `gestionnaireSessionExpiree()` est appelé — injecté depuis
  `main.js`, pas importé directement, pour qu'un service générique n'ait
  pas à connaître le store d'authentification ni le routeur.
- `stores/auth.js` : stocke le refresh token à la connexion, nettoie les
  deux jetons à la déconnexion.
- `main.js` : câble `gestionnaireSessionExpiree` sur une vraie
  déconnexion + redirection vers `/connexion`.

**Vérifié en conditions réelles**, deux cas simulés en corrompant
directement les jetons stockés dans le navigateur (pas juste en attendant
15 minutes) : (1) access token invalide, refresh token valide → requête
vers `/signalements` réussit quand même, la liste s'affiche normalement,
et l'access token en `localStorage` a effectivement changé (nouveaux
`iat`/`exp` dans le JWT décodé) — preuve d'un rafraîchissement réel, pas
d'une coïncidence ; (2) access ET refresh invalides → 401 sur
`/auth/rafraichissement`, jetons effacés, redirection propre vers
`/connexion` avec le formulaire de connexion affiché.

### Point 2 — revue de sécurité coffre-fort et authentification

Lecture ciblée de tout le module Coffre-fort (`chiffrement.py`,
`secret_service.py`, `api/v1/secrets.py`) et de l'authentification
(`security.py`, `deps.py`, `auth_service.py`, `main.py` pour le CORS,
`core/fichiers.py` pour l'upload). Pas une simple relecture : deux
défauts réels trouvés et corrigés, avec test de non-régression pour
chacun.

**Défaut réel n°1 — `GET /secrets/{id}/journal` contournait la règle de
visibilité par secret.** Toutes les autres routes du module (fiche,
liste, consultation) appliquent `role_requis` du secret en plus du rôle
global de l'appelant — sauf celle-ci, qui ne vérifiait que le rôle global
(responsable/administrateur gèrent le coffre-fort). Un responsable
pouvait donc lire qui a consulté un secret réservé à l'administrateur, et
quand, en devinant simplement son id — alors que la fiche et la liste le
lui masquent déjà. Corrigé (`obtenir_secret_pour_journal()`, nouvelle
fonction — pas `obtenir_secret_visible()` réutilisée telle quelle, parce
que celle-ci exclut aussi les secrets archivés, ce que le journal ne doit
justement pas faire : cassé une première fois en corrigeant trop vite,
repéré immédiatement par `test_archivage_retire_le_secret_de_la_liste_
mais_garde_le_journal`, déjà existant). Testé : un responsable reçoit 404
sur la fiche ET sur le journal d'un secret administrateur ; l'administrateur
voit toujours les deux.

**Défaut réel n°2 — aucune limite de tentatives sur `/auth/connexion`.**
Un mot de passe pouvait être essayé sans fin, aucun verrouillage, aucun
throttling. Corrigé par verrouillage de compte après 5 échecs consécutifs
(15 minutes), champs `tentatives_echouees`/`verrouille_jusqua` sur
`UTILISATEUR` (migration Alembic `129412013be2`, `server_default='0'`
nécessaire pour ne pas casser l'ajout de colonne NOT NULL sur une table
déjà peuplée). Ne distingue jamais "compte verrouillé" de "mot de passe
incorrect" dans la réponse (même 401 générique déjà utilisé pour un
compte désactivé) — pas de nouveau canal d'énumération. **Compromis
assumé, à noter** : verrouillage par compte, pas par IP (pas de nouvelle
dépendance ni de nouvelle table de suivi par adresse) — un tiers qui
connaît un identifiant réel peut délibérément verrouiller ce compte
15 minutes en enchaînant des mots de passe faux (déni de service ciblé,
pas un vol d'accès). Acceptable pour un nombre restreint de comptes
nommés internes à l'entreprise, pas un système à inscription publique ;
à revoir si le profil d'utilisation change.

**Vérifié sans trouver de défaut** (pas seulement supposé sain — lu et
vérifié explicitement) :
- Chiffrement Fernet : clé jamais en base ni en dur, aucune valeur par
  défaut (`config.py`, l'API refuse de démarrer sans elle), déchiffrement
  qui ne masque jamais une erreur (`InvalidToken` remonte explicitement).
- Upload de fichiers (`core/fichiers.py`) : nom de fichier original
  jamais réutilisé tel quel sur disque (uniquement son extension,
  vérifiée contre une liste autorisée), le nom réel est un UUID généré
  côté serveur — aucun chemin de traversée de répertoire possible.
- CORS (`main.py`) : origines explicites (`cors_origins`), pas de
  joker `*`.
- Mot de passe de démonstration du script d'amorçage (`db/seed.py`,
  `admin` / `ChangezMoi!2026`) : déjà transparent sur son propre risque —
  averti par nom ("changez-moi"), documenté comme réservé à la démo dans
  le docstring et dans son propre message affiché à la création. Pas un
  défaut caché ; à ne pas oublier de changer ou supprimer avant toute
  mise en production réelle.

**Non traité dans cette passe, à signaler plutôt qu'à ignorer** : les
jetons vivent dans `localStorage`, pas dans un cookie `httpOnly` — un XSS
réussi ailleurs dans l'application pourrait donc exfiltrer un jeton actif.
C'est un choix d'architecture déjà fait dès le prompt 0.3 (SPA + API REST
séparées, pas de rendu serveur), pas une régression de cette revue ; le
changer impliquerait de revoir tout le mécanisme d'authentification, hors
périmètre d'un correctif ponctuel.

**331 tests pytest au vert, 3 ignorés (pré-existants, sans rapport), 0
régression** — suite complète relancée après les deux correctifs de ce
point (328 précédents + 3 nouveaux : 1 régression coffre-fort +
2 verrouillage de connexion).

### Point 6 — sauvegarde de base de données : déjà fait, revérifié

En listant ce point comme critique, je ne savais pas encore qu'un chantier
antérieur (lot 5, prompt 5.3) avait déjà construit
`backend/scripts/sauvegarde.py` et `restaurer.py` : copie sûre du fichier
SQLite (API `backup()` de `sqlite3`, cohérente même si l'API écrit en
parallèle) ou `pg_dump --format=custom` selon `DATABASE_URL`, plus
`storage/`, jamais `.env`. Déjà testé de bout en bout à l'époque (incident
simulé, restauration, vérification). Revérifié aujourd'hui après tous les
changements de schéma de cette session (colonnes `tentatives_echouees`/
`verrouille_jusqua`) : `python scripts/sauvegarde.py` fonctionne toujours
sans modification — normal, la copie SQLite est binaire, pas
colonne-par-colonne, donc insensible à l'ajout de colonnes. Le chemin
PostgreSQL reste non exercé, pour la même raison que le point 3 ci-dessous
(ni Docker ni PostgreSQL disponibles ici). Rien à corriger : juste corriger
mon propre état des lieux, qui l'ignorait.

### Point 5 — première suite de tests automatisés côté frontend (Vitest)

Vitest était déjà dans la pile imposée (CLAUDE.md §3) mais jamais utilisé
— aucun fichier `*.test.js` n'existait avant aujourd'hui. Ajouté :
`vitest`, `jsdom` (environnement DOM en Node, nécessaire pour tout test
qui touche `localStorage`), `fake-indexeddb` (IndexedDB n'existe pas
nativement dans jsdom — nécessaire pour tester `filesync.js` sans passer
par un vrai navigateur) — trois dépendances de développement, aucune en
production, signalées ici comme demandé plutôt qu'ajoutées en silence.
`vite.config.js` porte directement la config `test` (pas de fichier
séparé, Vitest sait lire la config Vite existante).

**Priorité donnée à la logique la plus récemment corrigée**, pas un
balayage générique : les trois fichiers testés sont ceux du rafraîchissement
de jeton (point 1) et du mode hors connexion — exactement le code où de
vrais bugs ont été trouvés cette session (le DataCloneError du Proxy Vue,
la confusion 401/erreur réseau). Choix déjà signalé dans le journal du mode
hors connexion : "introduire IndexedDB en environnement de test... pour un
premier test isolé aurait été disproportionné" — ce n'est plus vrai
maintenant que le point 5 est traité pour de bon.

- `services/api.test.js` (8 tests) : extraction de message d'erreur (les 3
  formes de `detail` FastAPI), rafraîchissement silencieux + rejeu de la
  requête, dédoublonnage de deux 401 concurrents (une seule vraie requête
  de rafraîchissement), échec définitif (jetons effacés, callback de
  session expirée appelé, erreur 401 d'origine qui remonte), aucune
  tentative de rafraîchissement si la requête ne portait pas de jeton ou
  si aucun refresh token n'est stocké.
- `services/filesync.test.js` (8 tests) : ordre de la file, comptage,
  copie plate de `champs`/`fichiers` (pas de référence conservée vers
  l'original — le principe du correctif du DataCloneError, sans
  prétendre reproduire l'erreur de clonage elle-même : signalé
  explicitement en commentaire que fake-indexeddb n'a aucune raison de
  partager les mêmes restrictions de clonage qu'un vrai moteur de
  navigateur, la vérification de ce bug précis reste celle déjà faite en
  navigateur réel), et les trois branchements de `synchroniser()` (succès,
  vrai refus qui n'arrête pas la file, erreur réseau qui l'arrête net).
- `stores/signalements.test.js` (4 tests) : la distinction TypeError
  (mise en file) vs ErreurApi (remontée normale, jamais mise en file) au
  cœur de `creer()` — exactement la confusion qu'un 401 de session expirée
  provoquait avant le correctif du point 1. Un test a d'abord échoué pour
  une fausse raison (`toBe` au lieu de `toEqual` — Pinia enveloppe l'état
  dans un Proxy réactif, l'objet lu depuis `store.liste` n'est jamais la
  même référence que celle renvoyée par l'action même à contenu strictement
  identique), corrigé, pas un vrai défaut du store.

**20 tests, 3 fichiers, tous au vert** (`npm test`). `package.json` gagne
un script `test`.

### Point 4 — mode hors connexion étendu : SLAM

Deux volets, parce que SLAM a un besoin que Signalements n'a pas : un
référentiel à **lire** avant de pouvoir rien saisir (`GET
/slam/referentiel`), pas seulement une écriture à mettre en file.

- **Lecture** : le référentiel est mis en cache dans `localStorage`
  (`sheq_slam_referentiel_cache`) dès qu'il charge avec succès ; si le
  réseau manque au montage de l'écran, retombe sur ce cache plutôt
  qu'une erreur bloquante. **Limite réelle assumée et non résolue** :
  cette app n'a pas de service worker (la case "PWA" de la pile technique,
  CLAUDE.md §3, n'a jamais été construite au-delà de cette file
  IndexedDB) — un technicien qui recharge la page ou l'ouvre pour la toute
  première fois alors qu'il est déjà hors ligne ne peut charger ni le
  cache ni rien d'autre, l'application elle-même (JS/CSS) n'étant pas mise
  en cache. Le correctif d'aujourd'hui aide seulement l'utilisateur déjà
  arrivé sur l'écran avant de perdre le réseau (le cas réel visé : monter
  au pylône avec du réseau, le perdre en cours de route) — pas le
  chargement à froid sans réseau, qui resterait un chantier à part entière
  (service worker complet).
- **Écriture** : la décision GO/NO_GO part en file au lieu d'échouer,
  même mécanisme que Signalements (`horsConnexion.enregistrerGestionnaire
  ("slam", …)`, câblé dans `main.js` — pas de store SLAM dédié, l'écran
  appelle l'API directement, donc pas d'`onSucces` : rien à rafraîchir
  après coup). Ce choix n'est pas anodin : cette décision autorise ou non
  l'intervention (CLAUDE.md §7.2, "une décision NO_GO... ne bloque rien
  pour l'intervenant") — elle devait rester utilisable hors connexion,
  pas simplement échouer silencieusement.

**Deuxième bug réel du DataCloneError, une couche plus profonde.**
Testé en conditions réelles (réseau coupé au niveau du navigateur, pas
supposé), la mise en file du SLAM échouait exactement comme celle des
signalements la veille — alors que le correctif de la veille (copie
superficielle `{ ...champs }`) était censé être réglé. Cause : `champs`
pour SLAM contient `etapes_validees`, un **tableau de tableaux de
booléens** qui est lui-même un `ref()` Vue, imbriqué DANS l'objet
`champs` — une copie superficielle du conteneur ne "dérobotise" pas cette
valeur imbriquée, seulement le premier niveau. Le correctif de la veille
était donc accidentellement correct pour les signalements (leurs champs
sont tous des primitifs plats issus d'un objet littéral fraîchement
construit) et pas structurellement robuste. Corrigé pour de bon dans
`filesync.js` (`ajouterEnAttente`) avec un clonage JSON récursif
(`JSON.parse(JSON.stringify(champs))`) plutôt qu'une copie superficielle
— retire la réactivité à n'importe quelle profondeur, correct pour tout
futur module qui réutilisera ce mécanisme (Inspections, ensuite). Limite
consciente : ne fonctionnerait pas pour une valeur non sérialisable en
JSON (Date, Map...) — non applicable ici, tout ce qui transite dans
`champs` part de toute façon en JSON vers l'API.

**Vérifié en conditions réelles**, bout en bout : référentiel chargé en
ligne puis mis en cache (vérifié en lisant `localStorage` directement) ;
passage hors ligne réel (`context.setOffline`, pas
`navigator.onLine` simulé) ; 16 points cochés sur les 4 étapes, GO
enregistré → écran de verdict affiché immédiatement ("GO enregistré...")
avec la mention "Enregistrée localement, en attente du retour du réseau"
et le bandeau réseau affichant "1 élément en attente" ; retour du réseau
→ synchronisation automatique ; **vérifié côté serveur** (pas seulement
côté écran) via `GET /api/v1/slam` : l'évaluation est bien arrivée, avec
les 4×4 valeurs `true` exactement telles que cochées. Test Vitest ajouté
pour la régression précise (`filesync.test.js` — une valeur réactive
imbriquée, pas seulement le conteneur, est bien dérobotisée), 21 tests
au vert.

### Point 4 — Inspections : décision de conception nécessaire avant de coder

Contrairement à Signalements et SLAM (une saisie, un envoi, terminé),
Inspections est un flux en plusieurs étapes dont chacune dépend de la
précédente côté serveur : `creer()` (obtient un id serveur réel) →
`mettreAJourPoints()` (PATCH sur CET id, potentiellement plusieurs fois
pendant l'inspection, point par point) → `cloturer()` (POST sur CE même
id). Mettre uniquement `creer()` en file, comme les deux modules
précédents, laisserait l'inspection bloquée : sans id serveur réel, il
n'y a rien sur quoi faire porter un PATCH de points ni une clôture tant
que la création n'a pas été confirmée — or c'est précisément pendant une
inspection réelle sur site (cocher les points un par un en marchant) que
le réseau manque le plus. Traiter ce module correctement demande de
changer la forme des choses, pas seulement de réutiliser
`horsConnexion.enregistrerGestionnaire()` tel quel : par exemple, une
inspection non synchronisée vivrait entièrement en local (id provisoire,
tous ses points modifiables sans réseau) et ne partirait vers l'API qu'en
un seul envoi groupé à la synchronisation, plutôt que trois appels
distincts et dépendants. C'est un changement de mécanisme, pas une
extension du même — signalé avant de coder plutôt que bâclé (CLAUDE.md
§9, "explique avant de coder quand tu introduis un mécanisme nouveau").

### Point 4 — Inspections : construit (retour direct de l'utilisateur : "je construis la nouvelle mécanique")

**Simplification décisive qui rend le mécanisme tractable** : `PATCH
/inspections/{id}/points` envoie déjà l'état COMPLET des réponses à
chaque coche (remplace le tableau entier, ne fusionne pas — service
`mettre_a_jour_points`, déjà ainsi avant ce chantier). Pas besoin
d'accumuler des opérations en file : un seul élément par inspection,
remplacé (jamais dupliqué) à chaque coche.

- `services/filesync.js` : nouvelle fonction `mettreAJourEnAttente(id,
  champs)` — remplace les `champs` d'un élément déjà en file au lieu
  d'en créer un nouveau. Générique, réutilisable par un futur module.
- `stores/inspections.js` : `_mettreEnFile(points, cloturer, idReelConnu)`,
  cœur du mécanisme. `champs.id` reste `null` tant que l'inspection n'a
  jamais été créée côté serveur (`donnees_creation` porte alors de quoi
  faire le POST initial à la synchronisation) ; une fois un id réel connu
  (créée en ligne, puis coupée hors ligne plus tard), seuls
  points/cloturer restent à envoyer. `creer()`, `mettreAJourPoints()` et
  `cloturer()` retombent chacun sur cette fonction en cas de `TypeError`
  réseau, sans changer leur signature — `InspectionDetailView.vue` n'a
  connaissance d'aucun cas hors ligne, tout vit dans le store.
- Lecture aussi mise en cache (référentiel des points par modèle,
  sites/équipements/utilisateurs) — même principe que SLAM, même limite
  assumée (pas de service worker, un rechargement à froid déjà hors ligne
  reste impossible).
- `main.js` : gestionnaire "inspection" — POST initial si `id===null`,
  sinon PATCH points, puis POST clôture si `cloturer`.

**Piège trouvé en écrivant le premier test** (pas seulement en le
faisant tourner) : mon premier réflexe testait `id === null` pour
décider si l'inspection restait "à créer" — cassé dès le deuxième appel,
puisque `id` devient `local-N` dès la première mise en file. Corrigé en
se basant uniquement sur la présence de `_donneesCreation` (posé une
fois, jamais retiré avant une vraie confirmation serveur — qui n'arrive
jamais dans la session locale ouverte, une limite déjà notée : l'écran
resté ouvert après une synchronisation en arrière-plan n'affiche pas
automatiquement la référence réelle).

**Vérifié en conditions réelles**, coupure réseau simulée au niveau du
navigateur, sur une inspection "incendie" (14 points) : 3 points cotés
"C", un seul élément en file à chaque fois (vérifié en lisant
IndexedDB directement, pas seulement l'écran) ; re-cotation du premier
point en "NC" → même élément remplacé, pas dupliqué, `champs.points`
reflète les 3 valeurs à jour ; clôture hors ligne → `champs.cloturer:
true` sur ce même élément, banderole "Cette inspection est clôturée."
affichée immédiatement ; retour du réseau → synchronisation automatique,
file vidée. **Vérifié côté serveur** (`GET /api/v1/inspections`) :
inspection réellement créée, `statut: "cloturee"`,
`taux_conformite: 0.6667` — exactement 2 conformes sur 3 cotés (le point
recoté en NC exclu du numérateur), preuve que le contenu synchronisé est
le bon, pas une coïncidence de comptage. 25 tests Vitest au vert (4
nouveaux pour ce module, `inspections.test.js`).

**Restait délibérément non traité** : upload de photo sur un point NC
(`deposerPhoto()`) — nécessiterait un id d'inspection réel pour
s'attacher, incompatible avec une inspection encore locale ; hors ligne,
l'erreur actuelle ("Impossible d'ajouter la photo") reste honnête plutôt
que silencieusement cassée, mais rien n'est mis en file pour ce cas
précis.

## Gestion des utilisateurs — modification de profil (2026-09-09)

Retour direct de l'utilisateur ("dans ce module, nous devons permettre
la modification, la création d'un nouvel utilisateur"). La création
existait déjà (`UtilisateursDesktopView.vue`, chantier "construire tous
les écrans") ; la modification, elle, n'avait jamais été construite — le
commentaire d'en-tête de l'écran le disait déjà : "aucune route de
modification n'existait, seule la création". Vérifié dans le CDC (figure
A.40, "gestion des utilisateurs avec matrice des droits par rôle") et
dans la maquette (aucun écran dédié à l'édition d'un compte) : ni l'un
ni l'autre ne détaille ce flux au niveau des champs — construit sur la
base du modèle de données existant (`UTILISATEUR`) et du principe déjà
appliqué à la désactivation (même garde-fou d'auto-protection).

**Backend** :
- `schemas/auth.py` — `UtilisateurModification` : nom/prénom/rôle/site/
  courriel, tous optionnels (`exclude_unset`, même motif que
  `SecretModification` du coffre-fort — permet d'effacer explicitement
  `site_id`/`courriel` à `null` sans le confondre avec "non fourni").
  **Compromis assumé, à signaler** : ni `identifiant` ni `mot_de_passe`
  n'y figurent. Le premier sert de clé de connexion et de repère dans
  tout l'historique/les journaux — le changer mériterait son propre flux
  dédié. Le second est sensible par nature (réinitialisation) — à traiter
  séparément d'une modification de profil générale, pas construit ici.
- `auth_service.modifier_utilisateur()` — même garde-fou que
  `desactiver_utilisateur` : un administrateur ne peut pas retirer son
  propre rôle d'administrateur (risque de verrouiller tout le monde hors
  de la gestion des comptes). Toute autre modification sur son propre
  compte reste permise.
- `PATCH /auth/utilisateurs/{id}` — réservé à l'administrateur
  (`GERER_UTILISATEURS`), 404 générique si le compte n'existe pas.

**Régression trouvée et corrigée en relançant la suite complète** :
`test_cas_14_utilisateur_aucune_suppression_possible` supposait
qu'aucune route `/auth/utilisateurs/{id}` n'existait DU TOUT — devenu
faux avec l'ajout de PATCH sur ce même chemin. `DELETE` sur ce chemin
renvoie donc désormais 405 (méthode non autorisée) plutôt que 404
(chemin introuvable) — même comportement que pour actions/signalements,
toujours aucune suppression possible, seul le code exact change,
légitimement.

**Frontend** : `UtilisateursDesktopView.vue` — un seul emplacement de
carte bascule entre "Nouveau compte" et "Modifier le compte"
(`modeFormulaire`), plutôt que deux cartes séparées ; le formulaire
d'édition n'expose que les champs modifiables (pas d'identifiant, pas de
mot de passe). Bouton "Modifier" ajouté à chaque ligne du tableau,
pré-remplit le formulaire avec les valeurs actuelles. `stores/
utilisateurs.js` gagne `modifier(id, donnees)`.

**Incident de session, sans rapport avec le code applicatif** : après le
redémarrage du backend, `netstat -ano` continuait de rapporter un ancien
PID comme à l'écoute sur le port 8000 alors que `tasklist` ne le
trouvait plus — la route PATCH toute fraîche renvoyait donc l'erreur
générique FastAPI ("Not Found") d'un process resté sur l'ancien code,
pas la mienne ("Utilisateur introuvable"), ce qui a permis de repérer
l'incohérence. `tasklist`/`taskkill` par nom d'image (`python.exe`) a
retrouvé le vrai PID là où `netstat` induisait en erreur — à retenir
pour la suite de ce chantier : ne plus se fier au PID de `netstat -ano`
seul pour identifier le processus à arrêter dans cet environnement.

**Vérifié en conditions réelles**, bout en bout dans le navigateur,
connecté en admin : compte créé via "Inviter un utilisateur" (apparaît
immédiatement dans le tableau) ; compte existant modifié via
"Modifier" — formulaire pré-rempli avec les valeurs réelles (rôle actuel
présélectionné), nom changé, enregistré, reflété immédiatement dans le
tableau sans rechargement ; **vérifié côté serveur** que le changement a
persisté. Garde-fou anti-auto-rétrogradation testé directement contre le
vrai compte admin (`PATCH` sur son propre id avec un autre rôle) → 400,
message explicite ; le même changement de rôle appliqué à un AUTRE
compte fonctionne normalement. 44 tests pytest sur `test_auth.py` +
`test_recette_lot1.py` au vert (10 nouveaux pour la modification), suite
complète relancée sans régression restante.

## Trois chantiers UX (2026-09-09) — retour direct de l'utilisateur : "les points à améliorer"

Trois demandes en une fois, deux ambiguës au départ, clarifiées avant de
coder (CLAUDE.md §9) : (1) thèmes — combien, gardant le thème actuel par
défaut ; (2) "dropdown" pour les formulaires — le motif ouverture/
fermeture déjà en place sur ~20 écrans, ou une vraie fenêtre modale ? La
réponse : une vraie fenêtre modale centrée, pas le motif existant ; (3)
recherche et filtrage avancés sur toutes les listes — non commencé cette
session, périmètre trop large pour s'y lancer sans d'abord finir les deux
premiers points proprement.

**État des lieux fait avant de coder** (pas seulement supposé) : aucune
couleur codée en dur en dehors de `style.css` (4 occurrences isolées,
sans rapport) — un système de thèmes par variables CSS est donc
réellement propre à construire, pas un vœu pieux. Le motif ouverture/
fermeture existait déjà sur ~20 écrans (`formulaireOuvert`/
`modeFormulaire`...) — seul un vrai manque trouvé : **Visiteurs**, dont
le formulaire restait affiché en permanence. Aucun écran desktop n'avait
de champ de recherche texte, seulement quelques filtres par statut/type
(Signalements, Documents, Inspections, Utilisateurs) — confirme un vrai
manque généralisé pour le point 3.

### Point 1 — système de thèmes

`stores/theme.js` (nouveau) : 4 thèmes déclarés (`THEMES`), persistance
`localStorage`, `appliquer(theme)` pose/retire l'attribut
`data-theme` sur `<html>` (rien posé pour "clair" — le thème par défaut
reste celui de `:root`, sans condition). `main.js` pose l'attribut
**avant même la création de l'app Vue** (lecture directe de
`localStorage`, pas d'attente du montage de Pinia) : sans ça, un
rechargement de page sur un thème non-clair afficherait le clair une
fraction de seconde avant de basculer — vérifié explicitement (attribut
lu à 100 ms après rechargement, pas seulement après stabilisation,
aucune différence observée entre les deux mesures).

**4 thèmes, un seul documenté par CLAUDE.md §8** — signalé explicitement
avant de coder, comme demandé au §9 : "Clair" (par défaut, Navy/Or,
identique à aujourd'hui) ; "Sombre" (mêmes teintes de marque éclaircies
pour rester lisibles sur fond sombre — identité conservée, pas une
palette différente) ; "Ardoise" (clair, accent bleu-acier au lieu de
l'or — rendu plus neutre) ; "Émeraude" (clair, accent vert profond —
teinte volontairement distincte du vert de statut "conforme" déjà
utilisé partout ailleurs, pour ne jamais confondre "thème actif" et
"élément conforme"). Toutes les variables (`--navy`, `--gold`, les
couleurs d'état, les neutres) redéfinies sous `[data-theme="..."]` dans
`style.css` — un composant qui utilise `var(--gold)` reçoit l'accent du
thème actif sans rien changer à son propre code.

**Sélecteur** : `<select>` natif dans l'en-tête desktop
(`GestionLayout.vue`, visible sur tous les écrans de gestion) et dans le
menu mobile (`MenuView.vue`, section "APPARENCE") — un vrai menu
déroulant, cohérent avec la nature du choix (une seule valeur parmi
quatre), à ne pas confondre avec le point 2 ci-dessous qui parle de
fenêtres modales pour des formulaires à plusieurs champs.

**Vérifié en conditions réelles**, capture d'écran à l'appui (pas
seulement la lecture des variables CSS) : bascule vers "Sombre" — fond
`#0b1220`, cartes/texte lisibles, accents navy/or toujours reconnaissables,
tag rouge "Nouveau" et barre orange "En retard" toujours contrastés ;
bascule vers "Ardoise" — le graphique "Signalements par mois" (qui
utilise `var(--gold)`) passe du doré au bleu-acier sans aucune
modification du composant graphique lui-même, preuve que le découplage
variable/composant fonctionne réellement. Persistance vérifiée après un
vrai rechargement de page (pas simulée). 6 tests Vitest ajoutés
(`theme.test.js`) : pose/retrait de l'attribut, mémorisation, valeur
invalide ignorée sans casser l'état, valeur mémorisée corrompue retombe
sur "clair". 34 tests Vitest au total, tous au vert.

### Point 2 — fenêtres modales pour les formulaires de création/édition

`components/Modal.vue` (nouveau) : générique, réutilisable — fond
semi-transparent, boîte centrée (réutilise `.card`/`.ch`/`.cb`, pas de
nouvelle classe pour le contenu), ferme sur Échap, sur clic **hors** de
la boîte (`@click.self` sur le fond, jamais sur un clic dans la boîte),
ou sur le bouton ✕. Le contenu (champs, boutons "Enregistrer"/"Annuler")
reste entièrement à la charge de l'écran appelant via un slot — ce
composant ne connaît aucune logique métier.

**Deux écrans convertis cette session** (sur ~20 à terme — chantier
volontairement étalé, pas tout fait d'un coup, CLAUDE.md §9 "un module à
la fois") :
- **Utilisateurs** (`UtilisateursDesktopView.vue`) — écran pilote,
  création et édition toutes deux converties.
- **Visiteurs** (`VisiteursDesktopView.vue`) — le vrai manque identifié
  dans l'état des lieux : formulaire "Nouveau visiteur" qui restait
  affiché en permanence à côté de "Présents sur site", jamais escamoté.
  Un bouton "Nouveau visiteur" ouvre désormais le modal, fermé par
  défaut.

**Reste à faire, explicitement** : les ~19 autres écrans utilisant déjà
le motif carte-en-haut-de-page (`formulaireOuvert`, `modeFormulaire`...)
gagneraient en cohérence visuelle à passer au même composant `Modal.vue`
— fonctionnellement ils ouvrent/ferment déjà correctement, c'est
uniquement une question de présentation (carte insérée dans la page vs.
fenêtre par-dessus). Report volontaire, pas un oubli.

**Vérifié en conditions réelles**, sur les deux écrans convertis : fond
présent, boîte centrée (marge gauche ≈ marge droite, mesuré), fermeture
sur Échap, fermeture sur clic hors de la boîte, fermeture automatique
après une création/modification réussie, et — le plus important —
le compte/visiteur créé apparaît bien dans la liste ensuite (la
conversion visuelle n'a rien cassé de fonctionnel). Formulaire "Nouveau
visiteur" confirmé absent de l'écran par défaut (`formulaireVisiblePardefaut:
false`), corrigeant le vrai manque trouvé dans l'état des lieux.

### Point 3 — recherche et filtrage avancés

**Non commencé cette session** — signalé plutôt que bâclé. Périmètre
réel une fois l'état des lieux fait : ~20 écrans desktop sans aucun champ
de recherche texte, seulement quelques filtres par statut/type déjà en
place. Nécessite de définir d'abord un motif commun (barre de recherche
+ éventuels filtres avancés) avant de le décliner partout, comme cela a
été fait pour `Modal.vue` — à traiter dans un prochain chantier.

## Suite directe (2026-09-09) — retour de l'utilisateur : généraliser les modales + 5e thème

Deux demandes courtes, sans ambiguïté cette fois (le point 2 précédent
avait déjà établi le vocabulaire exact — "fenêtre modale centrée, ferme
après l'action") : (1) généraliser ce comportement à tous les écrans
desktop restants, pas seulement les deux du pilote ; (2) ajouter un
5e thème, "bleu clair professionnel".

**Thème "Bleu professionnel"** : contrairement à Ardoise/Émeraude (qui ne
changent que l'accent `--gold`), celui-ci éclaircit la couleur
PRINCIPALE elle-même (`--navy: #1568c4`, bleu vif plutôt que le navy
foncé par défaut) — c'est cette couleur-là, pas l'accent, que la demande
visait explicitement ("la couleur bleu claire"). L'or reste inchangé
comme accent chaud, pour ne pas tout mettre dans la même famille de
bleus et garder un contraste net avec les statuts. `THEMES` passe à 5
entrées, test `theme.test.js` mis à jour en conséquence (34 tests
toujours au vert).

**Conversion complète des ~9 écrans desktop restants** vers
`components/Modal.vue` (Actions, Risques, Parc, Documents, Formations,
Déchets, Inspections, Permis, Coffre-fort, Audits) — tous les écrans
desktop avec formulaire de création/édition utilisent désormais le même
composant modal, plus aucun "carte affichée en haut de la page".

**Deux écrans avec une vraie nuance, pas juste un copier-coller** :
- **Satisfaction** : la création d'une enquête génère un lien à
  transmettre au client (`lienGenere`). Fermer le modal immédiatement
  après l'action, comme demandé, aurait fait disparaître ce lien avant
  que l'administrateur ait pu le copier. Résolu en déplaçant l'affichage
  du lien au niveau de la page (bannière au-dessus du tableau), en dehors
  du modal — le modal se ferme bien après l'action, le lien reste visible
  ensuite. Vérifié explicitement : `satisfaction_ferme_apres_envoi: true`
  ET `satisfaction_lien_visible_apres_fermeture: true` en même temps.
- **Audits — Revue de direction** : flux en deux étapes réelles (créer la
  revue, PUIS y ajouter des décisions) — fermer après la première étape
  aurait rendu la seconde inatteignable. Le modal reste donc ouvert après
  la création de la revue (bascule vers l'étape "Ajouter une décision"),
  et ne se ferme que sur un bouton "Terminé" explicite ou "Annuler".
  Vérifié : `audits_reste_ouvert_apres_creation_revue: true`,
  `audits_etape_decision_visible: true`.

**Défaut d'accessibilité réel trouvé en écrivant les tests** (pas
seulement en les faisant tourner) : le déclencheur "Nouvelle séance"
(Formations) et "Nouvelle revue"/"Ouvrir une campagne" (Audits) sont des
`<span class="r" @click="...">` sans `role="button"` ni `tabindex` — donc
absents de l'arbre d'accessibilité (invisibles au clavier, invisibles à
un lecteur d'écran, et c'est cette absence qui a fait échouer le premier
essai de test automatisé, pas un bug du modal lui-même). Corrigés avec le
même motif déjà appliqué plus tôt dans la session à Déchets/Permis/
Coffre-fort (`role="button" tabindex="0" @keydown.enter`) — recherché
ensuite sur tout le dépôt (`class="r" @click` sans `role="button"`),
aucune occurrence restante.

**Vérifié en conditions réelles**, sur les 9 écrans convertis + les 2
déjà faits (Utilisateurs, Visiteurs), soit 11 au total : fond modal
présent, boîte centrée (mesuré, pas supposé), fermeture sur Échap sur
chacun, plus les deux cas particuliers ci-dessus vérifiés séparément.
Build de production propre (103 modules), 34 tests Vitest au vert.

## Thèmes — vrai bug corrigé, un faux bug écarté (2026-09-09)

Retour direct de l'utilisateur : "les thèmes ne sont pas professionnels et
en plus après avoir changé un thème celui de la sidebar ne change pas".
Deux affirmations, un seul vrai bug derrière — creusé plutôt que supposé.

**Bug réel confirmé** : `.side` (barre latérale, `GestionLayout.vue`)
avait sa couleur de fond codée en dur (`background: #12294f`) dans
`style.css`, **en dehors** de tout bloc `:root`/`[data-theme]` — un oubli
de la mise en place du système de thèmes la veille : je n'avais vérifié
les couleurs codées en dur que dans les fichiers `.vue`, jamais dans
`style.css` lui-même en dehors des blocs de thème. La barre latérale ne
pouvait donc littéralement jamais changer, quel que soit le thème choisi
— exactement le symptôme rapporté.

**Corrigé** : nouveau token `--side-bg`, dédié (pas `var(--navy)`
réutilisé tel quel — la barre reste volontairement sombre dans tous les
thèmes, y compris les thèmes clairs, donc sa couleur doit être choisie
par thème plutôt que dérivée mécaniquement d'un navy parfois clair,
comme dans le thème "Bleu"). Une valeur par thème : `#12294f` (clair,
valeur d'origine conservée), `#060d1a` (sombre), `#0c3563` (bleu),
`#1b2732` (ardoise), `#0c2620` (émeraude). `.side` utilise désormais
`var(--side-bg)`.

**Ardoise retravaillé** : la première version (navy `#1f3a52`, accent
`#3f6f93`) mettait couleur principale et accent dans la même famille de
bleus, trop proches pour vraiment se distinguer — un vrai défaut de
palette, pas qu'une question de goût : sans contraste de teinte entre les
deux, aucune palette ne lit comme "professionnelle", elle lit comme fade.
Remplacé par un accent teal (`#2f8f88`), franchement distinct du navy
tout en restant sobre.

**Un faux bug écarté, vérifié à trois niveaux avant d'être exclu** :
en relisant ma propre capture d'écran du thème "Bleu professionnel", j'ai
d'abord cru que rien n'avait changé par rapport au thème clair (bouton de
navigation actif visuellement identique). Vérifié avant de conclure à un
bug : (1) `getComputedStyle` sur `.nv.on` → `rgb(47, 128, 224)` (bleu vif)
pour "bleu" contre `rgb(37, 70, 126)` (navy foncé) pour "clair", nettement
différents ; (2) `document.elementFromPoint` au centre de ce bouton →
confirme qu'aucun élément ne se superpose, c'est bien `.nv.on` lui-même
qui est visible à cet endroit ; (3) lecture du pixel réellement peint dans
le PNG exporté (Pillow) → `(74, 128, 224)`, cohérent avec la valeur CSS.
Les trois niveaux (CSS calculé, élément réellement affiché, pixel
réellement peint) concordent : le thème "Bleu" fonctionnait déjà
correctement, c'est ma propre lecture visuelle de la capture compressée
qui était erronée — signalé ici explicitement plutôt que corrigé une
seconde fois sans raison, ou pire, laissé sans explication.

**Vérifié en conditions réelles** : capture d'écran des 5 thèmes,
couleur de fond de la sidebar interrogée par script pour chacun —
5 valeurs RGB distinctes confirmées (`rgb(18,41,79)`, `rgb(6,13,26)`,
`rgb(12,53,99)`, `rgb(27,39,50)`, `rgb(12,38,32)`). 34 tests Vitest et
build de production toujours au vert (changement CSS pur, aucune
logique touchée).

## Impression, sidebar en accordéon, logo (2026-09-09)

Trois retours directs de l'utilisateur en une fois : (1) tous les
documents renseignés doivent pouvoir s'imprimer, l'application doit "se
connecter à toutes les imprimantes" ; (2) chaque titre de section de la
barre latérale (PILOTAGE, TERRAIN, SYSTÈME) doit devenir un menu
déroulant ; (3) créer un logo Hirondelles et l'insérer.

### Point 1 — Impression

**Clarifié avant de coder** (CLAUDE.md §9) : une page web ne se
"connecte" jamais directement à une imprimante — c'est une frontière de
sécurité du navigateur, pas une limite de ce projet. `window.print()`
délègue à la boîte de dialogue d'impression du système, qui voit déjà
toutes les imprimantes installées sans configuration côté application.
Le travail réellement utile : un déclencheur visible et une mise en page
imprimée propre.

- Bouton "Imprimer" ajouté une seule fois, dans l'en-tête partagé de
  `GestionLayout.vue` — présent sur les ~20 écrans desktop d'un coup,
  plutôt que 20 modifications séparées (même logique que le sélecteur de
  thème, déjà ajouté au même endroit).
- Nouvelle classe utilitaire `.no-print` (style.css) : masque au format
  impression n'importe quel élément de navigation/action marqué avec —
  appliquée à la barre latérale et aux contrôles de l'en-tête (thème,
  impression, cloche). `.gestion-main`/`.gestion-view` reprennent un
  `overflow: visible` à l'impression (ils sont en défilement interne à
  l'écran, `overflow-y: auto` — sans ce correctif, seule la portion
  visible à l'écran se serait imprimée, pas le contenu complet). Modal
  ouvert, barre d'onglets mobile et bandeau réseau masqués aussi, par
  sélecteur direct plutôt que d'exiger `.no-print` sur chaque écran.
- Nouvelle icône `i-print` ajoutée au sprite, même style trait que le
  reste (Lucide).

**Bug réel introduit puis corrigé en vérifiant** : première version de
`.no-print` posait aussi `display: block` en dehors de `@media print` —
inutile (seul le masquage à l'impression compte) et carrément nuisible :
`.side` et `.no-print` ont la même spécificité CSS, donc l'ordre du
fichier tranche — `.no-print` étant déclaré plus bas, il l'emportait sur
`display: flex` de `.side`, cassant sa mise en page **à l'écran**, pas
seulement à l'impression. Retiré, seule la règle sous `@media print`
reste.

**Vérifié en conditions réelles** : `.side` correctement masqué en
simulant le média `print` (`page.emulateMedia`). Le clic sur "Imprimer"
appelle bien `imprimer()` → `window.print()` — confirmé via le journal
du serveur Vite (`DEBUG imprimer() appelée` juste après le clic, retiré
ensuite), **pas** via la valeur de retour du script de test : appeler la
vraie API `window.print()` dans un navigateur headless se comporte de
façon imprévisible pour l'automatisation (aucun affichage réel, aucune
imprimante) — signalé explicitement plutôt que présenté comme un test
concluant sur ce point précis.

### Point 2 — sections de la barre latérale en accordéon

`GestionLayout.vue` : `sectionOuverte(section)`/`basculerSection(titre)`,
état mémorisé dans `localStorage` (persiste après rechargement) —
**sauf** pour la section qui contient l'écran actuellement affiché,
toujours forcée ouverte même si l'utilisateur l'avait repliée
juste avant de naviguer dedans (sinon un rechargement de page pourrait
faire disparaître le lien vers l'écran affiché). Chevron (`i-chev`,
déjà existant) pivote à 90° par CSS quand la section est ouverte.

**Vérifié en conditions réelles** : repli de TERRAIN → ses liens
disparaissent, PILOTAGE non affecté ; rechargement de page → repli
toujours actif ; repli forcé de PILOTAGE (qui contient l'écran actif,
Tableau de bord) → le lien reste quand même visible, confirmant le
garde-fou. Capture d'écran à l'appui : mise en page de la barre latérale
intacte après le correctif du point 1.

### Point 3 — logo Hirondelles

Ajouté comme icône du sprite existant (`i-hirondelle`,
`IconeSprite.vue`) plutôt qu'un composant à part : même style trait
(Lucide) que tout le reste, hérite `currentColor` automatiquement,
s'utilise via `<Icone nom="hirondelle" />` exactement comme les autres.
Silhouette d'hirondelle en vol — ailes en mouette (courbe large) + queue
fourchue, le trait distinctif d'une hirondelle par rapport à un oiseau
générique.

Remplace le "H" texte brut (jamais un vrai logo, un espace réservé)
dans les 7 écrans qui l'utilisaient (`ConnexionView`,
`GestionLayout`, `AssistantDocumentaireView`, `ParcView`,
`SatisfactionQuestionnaireView`, `SignalementsView`,
`TableauBordMobileView`). Trouvé au passage : le badge `.mk` de la barre
latérale n'avait jamais eu de règle CSS dédiée (`.hd .mk` et `.login .mk`
existaient, pas `.side .top .mk`) — ajoutée, même recette (dégradé or,
coins arrondis) que `.hd .mk`.

**Vérifié en conditions réelles** : SVG présent dans le badge (pas de
texte "H" résiduel), capture d'écran confirmant un rendu net et lisible
dans la barre latérale.

34 tests Vitest et build de production au vert après les trois points.

## Aperçu des documents (2026-09-09) — correction du point 1 précédent

Retour direct de l'utilisateur, plus précis que le point 1 de l'entrée
ci-dessus : l'impression construite était celle des ÉCRANS de
l'application, pas celle des vrais DOCUMENTS (fichiers réels du module
Documents) — et surtout, cliquer sur un document ne montrait aucun
aperçu, juste un nouvel onglet. Corrigé.

`components/ApercuDocument.vue` (nouveau) : fenêtre modale (réutilise
`Modal.vue`) qui télécharge le fichier, en déduit le type par
l'extension de `document.fichier` (déjà connue côté liste, pas besoin
d'inspecter les en-têtes de réponse), et l'affiche :
- **PDF** : `<iframe>` — la visionneuse native du navigateur (PDF.js
  dans Chrome/Edge) s'affiche directement à l'intérieur, avec ses
  propres outils de zoom/pagination/impression déjà intégrés.
- **Image** : `<img>`.
- **Autre format** : pas de rendu HTML fiable possible, message honnête
  plutôt qu'un aperçu qui prétendrait fonctionner, plus un lien "Ouvrir
  dans un nouvel onglet".

Bouton "Imprimer" dédié à CE document (distinct de celui de
`GestionLayout.vue`, qui imprime l'écran/tableau) : ouvre le fichier
dans une fenêtre séparée puis y déclenche `print()` une fois chargée —
fonctionne pour tous les formats, contrairement à
`iframe.contentWindow.print()` qui ne s'applique proprement qu'aux PDF
affichés en iframe.

Branché sur les deux écrans Documents (desktop `DocumentsDesktopView.vue`
et mobile `DocumentsDossierView.vue`) : le bouton "Ouvrir" devient
"Aperçu", ouvre `ApercuDocument` au lieu d'un nouvel onglet direct.
`window.open(URL.createObjectURL(...))` retiré des deux écrans, toute la
logique de récupération/nettoyage du fichier vit maintenant dans le
composant partagé (avec `URL.revokeObjectURL` à la fermeture, pour ne
pas accumuler des URL blob en mémoire à chaque aperçu ouvert).

**Point trouvé en testant, pas supposé** : tous les documents
actuellement enregistrés dans l'application sont des `.docx`/`.xlsx`
(vérifié via `GET /documents` — aucun PDF, aucune image) — aucun
navigateur ne sait afficher ces formats nativement, contrairement au PDF.
Pour ces documents (la majorité du fonds documentaire réel aujourd'hui),
l'aperçu retombe donc sur le message "ne peut pas être prévisualisé" +
le lien d'ouverture externe, pas une vraie prévisualisation inline.
**Compromis assumé, à signaler explicitement** : une vraie prévisualisation
Word/Excel dans le navigateur demanderait soit un convertisseur
serveur (LibreOffice en mode headless ou équivalent — nouvelle
dépendance système, à discuter avant de l'ajouter, CLAUDE.md §9), soit un
service cloud tiers (contraire à l'esprit d'une application qui doit
fonctionner hors connexion) — hors périmètre de ce chantier, pas oublié.

**Vérifié en conditions réelles**, les deux cas : (1) document `.docx`
existant (FOR-SHEQ-001) → aperçu ouvert, message d'avertissement
présent, lien "Ouvrir dans un nouvel onglet" présent, bouton "Imprimer"
quand même proposé (ouvre le fichier, le système fait le relais vers
l'application associée) ; (2) un vrai PDF de test créé via le
formulaire "Nouveau document" (upload réel, pas simulé) → aperçu ouvert,
`<iframe>` chargé avec une URL `blob:`, **capture d'écran confirmant le
contenu réel du PDF affiché** ("Test document PDF") avec la barre
d'outils native du navigateur (pagination, zoom, impression,
téléchargement) visible par-dessus mon propre bouton "Imprimer" — la
meilleure preuve possible que l'aperçu fonctionne réellement, pas
seulement que l'iframe existe dans le DOM. 34 tests Vitest et build de
production toujours au vert.

## Écran d'accueil, histogrammes du tableau de bord, archivage des visiteurs (2026-09-09)

Trois retours directs de l'utilisateur.

### Écran d'accueil retravaillé

`AccueilView.vue` avait un double rôle jamais différencié : page
d'accueil avant connexion ET destination du bouton "Accueil" de la barre
d'onglets (~19 écrans mobiles) pour un utilisateur déjà connecté — dans
les deux cas, la même page générique s'affichait, montrant même le texte
brut de l'état de l'API ("API : connectee (development)") à
l'utilisateur final. Corrigé :
- Utilisateur déjà connecté → redirection immédiate vers Signalements
  (même destination que juste après une connexion réussie,
  `ConnexionView.vue`) : "Accueil" ramène à l'écran de travail réel, pas
  à une vitrine.
- Utilisateur non connecté → nouvelle présentation avec le vrai logo,
  `BandeauReseau.vue` (déjà utilisé partout ailleurs, absent jusqu'ici du
  tout premier écran vu) à la place du texte d'état brut de l'API.

**Vérifié en conditions réelles** : capture d'écran de la nouvelle page
(logo, indicateur réseau "En ligne · Synchronisé à l'instant", aucun
jargon de développement) ; utilisateur connecté qui revient sur `/` →
confirmé redirigé vers `/signalements`.

### Histogrammes du tableau de bord

Le tableau de bord avait déjà un vrai histogramme ("Signalements par
mois", colonnes verticales) — invisible en pratique avec les données de
démonstration actuelles (un seul mois renseigné, donc une seule
colonne, ressemblant à un simple rectangle plutôt qu'à un histogramme).
Un deuxième histogramme ajouté : "Avancement du plan d'action" (desktop
uniquement), qui remplace les 3 barres de progression horizontales par
un histogramme à 3 colonnes verticales (Réalisées/En cours/En retard),
même style visuel que celui des signalements — deux nouvelles classes
CSS (`.bcol .bar.g`, `.bcol .bar.o`), miroir de `.fl.g`/`.fl.o` déjà
utilisées pour les barres de progression ailleurs dans l'application,
pas de nouvelle dépendance de graphique.

**Écart assumé, à signaler** : aucune autre donnée du tableau de bord
(inspections, EPI, formations, documents, satisfaction) n'a de
répartition par catégorie ou par mois côté API (`tableau_bord_service.py`
— seule `SignalementsResume.par_mois` existe) : un troisième histogramme
demanderait d'étendre le backend, pas seulement l'écran — pas fait
faute de justification suffisante pour ce chantier précis.

**Vérifié en conditions réelles** : capture d'écran confirmant les deux
histogrammes réels côte à côte, colonnes multicolores visibles (vert/or/
orange selon le statut).

### Archivage des visiteurs

`Visiteur` hérite déjà `archive` (base commune à toutes les tables,
point 5 CLAUDE.md) mais rien ne l'exploitait — ni route, ni action de
service, et surtout **`lister_visiteurs()` ne filtrait même pas
`archive.is_(False)`** : un visiteur archivé serait resté visible dans
le registre général, l'archivage n'aurait servi à rien. Corrigé en même
temps que l'ajout de la fonctionnalité, pas après coup.

`archiver_visiteur()` (service) refuse d'archiver un visiteur encore
présent (400 explicite) — seul un visiteur déjà parti a une raison
légitime d'être archivé ; `visiteurs_presents()` (liste d'évacuation)
n'a pas besoin de filtrer sur `archive` pour cette raison même.
`POST /visiteurs/{id}/archiver`, réservé à aucun rôle particulier (même
principe que le reste du module — section 5.3.6, "aucun rôle accueil
distinct dans la matrice").

Frontend : nouvelle carte "Registre — visiteurs partis" sur
**desktop uniquement** (`VisiteursDesktopView.vue`) — écran de gestion/
historique, cohérent avec le principe déjà établi ailleurs dans l'appli
(desktop = pilotage, mobile = saisie rapide terrain) ; `visiteurs.liste`
était déjà chargée par `charger()` mais jamais affichée jusqu'ici.
Bouton "Archiver" par ligne, visible seulement pour les visiteurs déjà
partis.

**Incident de session, pas un défaut du code** : premier test en direct
échoué avec un 404 générique FastAPI (pas mon message "Visiteur
introuvable") sur la route pourtant fraîchement ajoutée — même symptôme
que pour la route PATCH Utilisateurs plus tôt dans la session : le
serveur backend tournait sur du code obsolète malgré `--reload actif`,
confirmé par les 6 tests pytest déjà au vert sur cette même route.
`netstat -ano` a de nouveau rapporté un PID trompeur ; `tasklist` a
retrouvé le vrai processus à arrêter. Reconfirme la leçon déjà notée :
ne pas se fier à `netstat` seul dans cet environnement pour identifier
le processus serveur à redémarrer.

**Repéré au passage, hors périmètre de cette demande, signalé plutôt
qu'ignoré** : `tests/test_export_pdf.py::test_export_permis` et
`tests/test_notifications.py::test_permis_en_attente_notifie_le_responsable`
échouent quand la suite tourne tard le soir — ces deux tests calculent
`fin_validite` comme `maintenant + 4h` sans tenir compte du passage à
minuit, ce qui déclenche légitimement la règle métier "un permis ne peut
couvrir qu'une seule journée" (422) plutôt qu'un vrai bug applicatif.
Confirmé sans rapport avec les changements de cette session via
`git diff --stat HEAD -- app/` (seuls des fichiers auth/visiteurs
modifiés). Test préexistant à corriger séparément, pas fait ici.

**Vérifié en conditions réelles**, bout en bout dans le navigateur, sur
le backend une fois réellement à jour : visiteur enregistré → départ
enregistré → apparaît dans le registre → "Archiver" cliqué → disparaît
du registre. Vérifié aussi directement côté API (`GET /visiteurs` avant/
après : le visiteur archivé n'apparaît plus, total passé de 5 à 4).
6 tests pytest sur `test_visiteurs.py` au vert (2 nouveaux), 36 tests
Vitest (2 nouveaux, `visiteurs.test.js`) et build de production tous
au vert.

---

## 2026-09-10 — Recherche + pagination des listes desktop (pilote Risques) ; suivi des actions ; emblème du logo

Trois demandes de l'utilisateur, dans l'ordre : (1) « pour les listes tu dois
[avoir] une possibilité de recherche, les listes doivent être paginées ET
TOUT DOIT ETRE BIEN OPTIMISER » ; (2) l'image du logo Hirondelle IT Lab
envoyée, à intégrer ; (3) « on ne peut pas modifier le statut de l'action ».

### 1. Recherche + pagination — mécanique réutilisable

`.pagin` / `.pg` / `.pg button.on` existaient dans `style.css` depuis l'import
de la maquette mais n'avaient jamais été câblés à un écran. Ajouté :

- **`composables/useRechercheEtPagination.js`** : filtre texte + découpage en
  pages, 100 % côté client (toutes les listes sont déjà chargées en entier par
  leur store ; volumes réels de l'ordre de quelques centaines de lignes, cf.
  CDC — pas de pagination serveur aujourd'hui). Retourne `recherche` (ref),
  `page`, `totalPages`, `resultats`, `elementsPage`, `allerPage`. Retour en
  page 1 à chaque nouvelle recherche ; `page` re-borné si la liste rétrécit
  (archivage).
- **`components/BarrePagination.vue`** : pied de tableau `.pagin` avec numéros
  de page (`.pg`), fenêtre autour de la page courante + « … » au-delà de
  7 pages. Le texte de décompte reste au choix de l'écran (slot).
- **`style.css`** : `.srch` (recherche par écran, repris de la recherche
  globale d'en-tête de la maquette) copié depuis la maquette ; `.pg button`
  passé de `background:#fff` en dur à `var(--surface)` (bouton blanc illisible
  en thème sombre — même classe de bug que `--side-bg` la veille), `.pg
  button:disabled` ajouté pour le « … ».
- **Écran pilote** : `RisquesDesktopView.vue` — champ de recherche dans
  l'en-tête de carte, `elementsPage` dans le `v-for`, `BarrePagination` en
  pied. Recherche sur danger / catégorie / numéro / mesures proposées.

**Bug réel trouvé et corrigé (coûteux à isoler).** La recherche ne filtrait
rien : taper dans le champ mettait bien à jour la valeur DOM mais `resultats`
ne se recalculait jamais, sans la moindre erreur en console. Cause : le
prédicat `correspond()` faisait `r.numero?.toLowerCase()`. Or `numero` est un
**entier** côté API (`"numero": 1`), pas une chaîne — `?.` ne court-circuite
pas sur un nombre, `.toLowerCase()` lève un `TypeError`. Cette exception,
levée dans le getter du `computed` `resultats` (lui-même lu pendant le flush
d'un `watch` interne au composable), était avalée silencieusement par
l'ordonnanceur de réactivité de Vue : la chaîne réactive se cassait sans
trace. Diagnostic par bissection (le composant minimal isolé fonctionnait, la
copie exacte de l'écran non → réduction progressive jusqu'à la ligne
fautive). Corrigé : `String(r.numero ?? "").toLowerCase()`. Mise en garde
explicite ajoutée dans le JSDoc du composable (« `filtrer` ne doit jamais
lever ») + test de régression `useRechercheEtPagination.test.js` avec un champ
numérique. `v-model` sur la ref déstructurée n'était PAS en cause (piste
explorée puis écartée) — c'était bien le prédicat.

**Vérifié en conditions réelles** dans le navigateur : recherche « zzz »
inexistante → tableau vide + message « Aucun risque ne correspond » ; champ
vidé → 4 lignes de nouveau ; recherche « électrique » → 0 ligne (aucune
catégorie de ce nom dans le jeu de test, filtrage correct). Décompte
« 0 sur 4 risques affichés » cohérent. 6 tests Vitest sur le composable.
Pagination numérotée non exerçable en l'état (4 risques → une seule page) ;
la mécanique est là, à propager aux autres écrans à liste.

**« TOUT DOIT ETRE BIEN OPTIMISER »** : demande vague, non précisée. La
pagination côté client (fin du rendu de listes non bornées) + la recherche
en couvrent l'essentiel pour les volumes actuels. Si de très gros volumes
apparaissaient, il faudrait une pagination serveur — l'API du composable
resterait identique côté vue, seule son implémentation changerait. À
reprendre avec l'utilisateur si un besoin de perf plus large se confirme.

### 2. Suivi d'une action (statut + avancement) — vue desktop

« On ne peut pas modifier le statut de l'action » : le back-end
(`PATCH /actions/{id}/avancement` et `/statut`) **et** le store
(`mettreAJourAvancement`, `changerStatut`) exposaient déjà tout ; la vue
mobile avait un panneau de suivi ; mais `ActionsDesktopView.vue` affichait la
colonne « Statut » en lecture seule, sans aucun bouton. Écart d'origine, pas
un choix.

Ajouté : bouton « Suivi » par ligne (« Voir » si clôturée) ouvrant une
**fenêtre modale** (motif desktop standard) :

- avancement (%) + indicateur de réalisation (texte) ;
- « Enregistrer l'avancement » → `mettreAJourAvancement` ;
- « Démarrer » (visible seulement si `ouverte`) → `changerStatut('en_cours')` ;
- « Clôturer » → enregistre d'abord avancement + indicateur, puis
  `changerStatut('cloturee')`. L'indicateur est **obligatoire** pour clôturer
  (règle serveur `action_service.changer_statut`, 409 sinon) : garde côté
  client (message explicite) + le refus serviteur est de toute façon remonté
  dans la modale.
- Action clôturée : modale en lecture seule (« aucun retour en arrière »).

**`stores/actions.js`** : `mettreAJourAvancement` n'envoie plus la clé
`indicateur` quand elle est vide (le serveur l'enregistrerait en `""`, ce qui
bloquerait ensuite la clôture) ; envoi de la valeur `trim()`ée sinon.

**Vérifié en conditions réelles** dans le navigateur, bout en bout :
- action « ouverte » → « Suivi » → « Démarrer » → statut serveur passé à
  `en_cours` (vérifié via `GET /actions/2`) ; l'affichage reste « En retard »
  car l'échéance est dépassée — précédence correcte de `en_retard` sur
  `en_cours` dans `etat()` ;
- « Clôturer » sans indicateur → message de garde « Renseigne l'indicateur de
  réalisation avant de clôturer. », modale maintenue ouverte ;
- indicateur renseigné → « Clôturer » → modale fermée, ligne passée à
  « Réalisée ».
6 tests Vitest ajoutés (`stores/actions.test.js`), 47 tests Vitest au total au
vert.

### 3. Emblème du logo

L'utilisateur a envoyé l'emblème Hirondelle IT Lab (cercle fin + hirondelle
vue de face, ailes relevées, queue fourchue + mot-symbole « HIRONDELLE / IT
LAB »). Le fichier étant un PNG non déposé dans le dépôt, `i-hirondelle`
(`components/IconeSprite.vue`) a été **redessiné en SVG au plus près** de
l'emblème : passage d'un tracé au trait à une **silhouette pleine** (`fill`
explicite, `stroke` neutralisé sur ce seul symbole ; le cercle garde un trait
de 2), viewBox `0 0 48 48`. Une marque pleine reste lisible dans les
pastilles `.mk` de 24-40 px là où le trait fin se perdait. Les 8 emplacements
qui utilisent déjà `<Icone nom="hirondelle">` (accueil, connexion, barre
latérale, etc.) reprennent la nouvelle forme sans changement.

**Reste à traiter** : pour un rendu strictement identique au PNG (dégradés,
proportions exactes du mot-symbole), déposer le fichier dans `src/assets/` et
le référencer là où le lockup complet a du sens (accueil, connexion) —
demandé à l'utilisateur.

---

## 2026-09-10 (suite) — Inspections d'équipements : quel équipement, où, par qui, quand

Retour direct de l'utilisateur : « pour les inspections des équipements on
doit savoir quel équipement a été inspecté, où et par qui et quand ».

Le back-end portait déjà toute l'information (`Inspection.equipement_id`,
`site_id`, `inspecteur_id`, `date`, tous dans `InspectionSortie`) — c'est la
restitution qui manquait, et le choix de l'équipement était absent côté
desktop.

**`stores/inspections.js`** :
- `equipementParId(id)` et `nomEquipement(id)` — libellé lisible d'un
  équipement inspecté : `identity` (code d'inventaire, ex. `BKO-AP-01`) +
  `marque modele`, comme dans le Parc. Repli sur la seule `identity` si
  marque/modèle absents, `null` si l'équipement est inconnu.

**`InspectionsDesktopView.vue`** :
- Colonne « Site / Objet » : quand `equipement_id` est renseigné, l'équipement
  (`nomEquipement`) devient la ligne principale, le site passe en sous-ligne.
  Sinon, le site seul comme avant. L'inspecteur et la date étaient déjà là.
- Modale « Nouvelle inspection » : sélecteur d'équipement affiché quand le
  type est « Équipements », **filtré sur les équipements du site retenu**
  (`equipementsDuSite`, un équipement appartient à un site). Facultatif
  (« Aucun en particulier »). `equipement_id` passé en query à
  `InspectionDetailView`, qui le transmet déjà à `POST /inspections`.

**`InspectionsView.vue` (mobile)** :
- Lignes de la liste : ligne équipement ajoutée quand `equipement_id` présent ;
  inspecteur ajouté à la ligne méta (n'y figurait pas).
- Le sélecteur d'équipement (déjà présent) est désormais filtré par site et
  affiche marque + modèle, cohérent avec le desktop.

**`InspectionDetailView.vue`** :
- En-tête enrichi : ligne équipement (`equipementInspecte`) + « site · date ·
  inspecteur ». Pour une inspection encore en création (`inspections.inspection`
  nul), l'équipement vient de la query et l'inspecteur est l'utilisateur
  connecté ; pour une fiche existante, tout vient de l'objet chargé.

**Vérifié en conditions réelles** dans le navigateur :
- liste desktop, inspection `#4` (type Équipements) → colonne Objet =
  « BKO-AP-01 — MikroTik hAP ac2 » + sous-ligne « Siège Bamako (démo) »,
  inspecteur « Démo Admin », date « 08/09/2026 » ; les inspections sans
  équipement affichent toujours le site seul ;
- modale « Nouvelle inspection », type Équipements + site choisi → sélecteur
  d'équipement présent, option « BKO-AP-01 — MikroTik hAP ac2 (Local
  technique) » ;
- fiche `/inspections/4` → en-tête « Équipements · BKO-AP-01 — MikroTik hAP
  ac2 · Siège Bamako (démo) · 08/09/2026 · Démo Admin » ; fiche `/inspections/1`
  (sans équipement) → « Incendie et extincteurs · Siège Bamako (démo) ·
  07/09/2026 · Démo Admin ».
4 tests Vitest ajoutés (`stores/inspections.test.js`), 51 tests au total au
vert, build de production OK.

---

## 2026-09-10 (suite) — Objet précis inspecté (extincteur, tableau…) : « lequel »

Retour direct de l'utilisateur : « après inspection d'un extincteur par
exemple, on ne sait pas lequel a été inspecté ».

Les inspections hors « équipements » (incendie, électricité, installations en
hauteur, locaux) portent une checklist mais aucun identifiant de l'objet
concret contrôlé — seulement le site. Le CDC ne prévoit pas de registre des
extincteurs / tableaux / lignes de vie ; un **champ libre** court suffit à
lever l'ambiguïté.

**Back-end** :
- `Inspection.objet_inspecte : str | None` (`String(200)`, nullable) — model,
  service `creer_inspection`, `InspectionCreation` (facultatif),
  `InspectionSortie`.
- Migration `3197fb535115` (après `129412013be2`) : `add_column` nullable,
  sans `server_default` — les inspections existantes restent à `NULL`, voulu.
  `alembic upgrade head` OK.

**Front-end** :
- Modales « Nouvelle inspection » (desktop + mobile) : champ « Objet / repère
  inspecté » — libellé « (recommandé) » pour les types non-équipement,
  « (facultatif) » pour « équipements » (où `equipement_id` identifie déjà).
  Placeholder adapté au type (« Ex. Extincteur EXT-03, hall RDC », « Ex.
  Tableau TGBT, local technique »…). Passé en query à
  `InspectionDetailView` → `creer()`.
- Colonne « Site / Objet » (desktop) et lignes de liste (mobile) : affichent
  `objet_inspecte` en ligne principale quand il est présent et qu'il n'y a
  pas d'équipement lié ; site en sous-ligne. Si équipement **et** objet, le
  second est ajouté en sous-ligne.
- En-tête `InspectionDetailView` : `cibleInspection` = équipement lié, sinon
  objet libre.
- `stores/inspections.js` : `objet_inspecte` propagé aussi dans l'objet
  d'inspection construit en fallback hors ligne.

**Vérifié en conditions réelles** dans le navigateur, bout en bout :
inspection « Incendie et extincteurs » créée depuis la modale desktop avec
« Extincteur EXT-TEST-… » → après cotation d'un point (persistée côté serveur,
`/inspections/7`), en-tête = « Incendie et extincteurs · Extincteur
EXT-TEST-… · Siège Bamako (démo) · 10/09/2026 · Démo Admin » ; dans la liste,
colonne Objet = « Extincteur EXT-TEST-… » + sous-ligne « Siège Bamako
(démo) », inspecteur « Démo Admin », date « 10/09/2026 ».
2 tests pytest (`test_inspections.py`, persistance + facultatif),
343 tests back-end au vert ; 51 tests Vitest au vert ; build de prod OK.

---

## 2026-09-10 (suite) — Gestion multi-sites

Retour direct de l'utilisateur : « dans l'application on a un seul site alors
que nous intervenons sur plusieurs sites ».

L'entité SITE (hors dictionnaire, section 5.2.3) n'avait qu'une route de
consultation (`GET /sites`) : les sites se créaient « directement en base ».

**Back-end** :
- `Permissions.GERER_SITES = (ADMINISTRATEUR,)` — les sites relèvent des
  « paramètres » du périmètre administrateur (CLAUDE.md §6). La consultation
  reste ouverte à tout le personnel.
- `schemas/site.py` : `SiteCreation` (nom obligatoire, non vide),
  `SiteMiseAJour` (partielle, `exclude_unset`).
- `services/site_service.py` : `creer_site`, `modifier_site`, `archiver_site`.
  **Archivage refusé (409)** tant qu'un équipement non archivé ou un permis en
  cours (`demande`/`delivre`) est rattaché au site — on ne fait pas
  disparaître un lieu encore exploité ; l'utilisateur doit d'abord traiter
  ces rattachements. Jamais de suppression physique (CLAUDE.md §2).
- `api/v1/sites.py` : `POST /sites`, `PATCH /sites/{id}`,
  `POST /sites/{id}/archiver` — tous `require_role(*GERER_SITES)`.
- `tests/test_sites.py` : 8 tests (création, nom vide refusé, 403 technicien,
  liste ouverte, modif partielle, archivage retire de la liste, archivage
  refusé si équipement rattaché, pas de route DELETE).

**Front-end** :
- `stores/sites.js` : `charger` / `creer` / `modifier` / `archiver` +
  `TYPES_SITE` + `libelleType`. `sites.test.js` : 4 tests.
- `views/SitesDesktopView.vue` : liste + fenêtre modale création/édition
  (Modal.vue) + « Archiver » (confirmation navigateur, refus serveur remonté
  dans le bandeau). Réservé à l'administrateur, aucun équivalent mobile
  (cohérent avec Utilisateurs & rôles).
- Route `gestion-sites` (`/gestion/sites`), entrée « Sites » dans la section
  ADMINISTRATION de la barre latérale (déjà masquée aux non-administrateurs).

**Vérifié en conditions réelles** dans le navigateur : écran `/gestion/sites`
ne montrait que « Siège Bamako (démo) » → création « Antenne Test … » (type
site client, adresse « Kayes, quartier Légal ») → les deux sites listés ; le
nouveau site apparaît immédiatement dans le sélecteur « Site » de la modale
« Nouvelle inspection » (donc disponible partout où un site_id est référencé :
inspections, permis, équipements, déchets, visiteurs). Lien « Sites » présent
dans la barre latérale. Aucune erreur console.
349 tests back-end au vert (8 nouveaux), 55 Vitest (4 nouveaux), build de
prod OK.

---

## 2026-09-10 (suite) — Fenêtres modales sur les écrans terrain (mobile)

Retour direct de l'utilisateur : « pour les écrans terrain les formulaires
doivent être des drop down aussi ».

Les écrans desktop avaient été convertis au motif `Modal.vue` (le formulaire
s'ouvre au-dessus de l'écran au clic, se ferme après l'action) ; les écrans
mobiles gardaient le motif d'origine « carte insérée dans le flux de la page »
(`<div v-if="formulaireOuvert" class="card">`).

9 écrans mobiles convertis à `Modal.vue`, même transformation qu'en desktop :
`ActionsView` (pilote), `RisquesView`, `ParcView`, `ParcFicheView`,
`DechetsView`, `DocumentsView`, `FormationsView`, `PermisView`,
`CoffreFortView`, `InspectionsView`. Le bouton déclencheur perd son
`v-if="!formulaireOuvert"` (il reste visible, la modale le recouvre) ; le
titre de section `.sec` est remplacé par le `titre` de la modale. `Modal.vue`
(`position: fixed; inset: 0`) se superpose au conteneur `.ecran-mobile` sans
adaptation supplémentaire — `.modal-boite` (`width: 100%; max-width: 560px`)
tient sur un viewport de 400 px.

`ParcFicheView` : cas particulier — le bouton était conditionné à
`marque === 'MikroTik'` ET `!formulaireOuvert` ; seul le second est retiré,
le `v-else-if="!formulaireOuvert"` du texte d'indisponibilité devient `v-else`.

`VisiteursView` **laissé tel quel** : son formulaire d'arrivée n'a pas de
bouton déclencheur, il est affiché en permanence (borne d'accueil, le
visiteur se saisit lui-même) — ce n'est pas le motif « clic → formulaire »
visé par la demande. À convertir si l'utilisateur le souhaite aussi.

**Vérifié en conditions réelles** (viewport 400 px) : sur les 8 écrans
testés en boucle (`/risques`, `/parc`, `/dechets`, `/documents`,
`/formations`, `/permis`, `/coffre-fort`, `/inspections`) le bouton ouvre une
`.modal-fond` avec le bon titre et le bon nombre de champs, la touche Échap
la referme. Flux complet vérifié sur `/risques` : ouverture → saisie danger +
mesures → « Enregistrer » → modale fermée, nouveau risque présent dans la
liste. Aucune erreur console. 55 tests Vitest au vert, build de prod OK.

**Complément (même jour)** : `VisiteursView` converti à son tour (l'utilisateur
a confirmé). Le formulaire d'arrivée, jusque-là affiché en permanence, s'ouvre
maintenant via « Enregistrer une arrivée » dans une modale « Arrivée d'un
visiteur » et se referme après l'enregistrement. Vérifié en conditions réelles
(viewport 400 px) : aucun formulaire au chargement → bouton → modale (5 champs
+ case consignes) → « J'accepte et je m'enregistre » → modale fermée, visiteur
présent dans la liste « SUR SITE ». Aucune erreur console. Les 10 écrans
terrain à formulaire sont désormais tous au motif modale.

---

## 2026-09-10 (suite) — Correction des points faibles de la revue (lot 1/n)

Suite à la revue d'ensemble, l'utilisateur demande la correction de tous les
points. Traité par lots, chacun testé et vérifié.

### Lot 1 — Noms au lieu d'identifiants, refus de permis, site du signalement

**`PermisValidationView`** — l'écran qui autorise un travail en hauteur
affichait « Site #1 » et « Utilisateur #3, Utilisateur #7 ». Refait :
- passe par `usePermisStore` (comme le reste de l'app) au lieu d'appeler
  l'API en direct ; nouveaux `chargerPourValidation(id)`, `valider(id)`,
  `refuser(id, motif)` dans le store ;
- affiche les noms résolus (site, intervenants, **surveillant** — n'était pas
  montré du tout) ;
- **bouton « Refuser »** ajouté (route `/permis/{id}/refuser` avec motif,
  jamais exposée) : un permis non conforme ne restait sinon ni validé ni
  refusé. Motif obligatoire, saisi dans une modale ;
- squelette de chargement au lieu de « Chargement… » brut.

**Backend signalements** — `SignalementSortie` gagne `auteur_nom` et
`site_nom` résolus **côté serveur** (`signalement_service.serialiser` /
`serialiser_plusieurs`, un seul aller-retour SQL pour la liste). `auteur_nom`
reste `None` pour un signalement anonyme — l'anonymat est garanti par le
serveur, pas laissé au client (CLAUDE.md §7.3). `SignalementsView` affiche
`auteur_nom`. 2 tests pytest (dont un vérifiant l'anonymat en liste, vu par
un référent).

**`NouveauSignalementView`** — sélecteur de **site** ajouté (un technicien
intervient sur plusieurs sites). Pré-rempli avec le site du compte,
modifiable. Liste des sites mise en cache `localStorage` pour rester
utilisable hors connexion (cet écran est le pilote du mode hors ligne).

### Lot 2 — Téléchargement des PDF officiels

Le back-end génère des PDF (signalements, inspections, permis, audits,
revues, SLAM, configurations) — **aucun bouton dans l'interface**. Or l'app
digitalise 36 documents papier, le PDF est le livrable.

- `utils/telechargement.js` : `telechargerPdf(chemin, nomFichier)` — récupère
  le blob via `api.requete(..., { brut: true })` (conserve l'en-tête
  Authorization, qu'un `<a href>` n'enverrait pas) et déclenche
  l'enregistrement.
- Icône `i-dl` (flèche vers le bac, style trait Lucide) ajoutée au sprite.
- Boutons « PDF » ajoutés : `InspectionsDesktopView` (par ligne),
  `PermisDesktopView` (par ligne). À étendre à Audits/Revues et à la fiche
  d'inspection / le détail permis.

**Vérifié en conditions réelles** : `/gestion/inspections` → 7 boutons PDF,
clic → téléchargement réel déclenché (`inspection-7.pdf`). `/signalements` →
noms d'auteur (« Démo Admin »), plus aucun « Utilisateur #n ».
`/signalements/nouveau` → sélecteur de site avec la vraie liste.
351 tests back-end au vert, 55 Vitest, build de prod OK.

### Reste à traiter (lots suivants)

- **Pagination + filtres serveur** sur `/actions`, `/inspections`, `/permis`,
  `/risques`, `/equipements`, `/documents`, `/dechets`, `/audits`,
  `/formations` (seul `/signalements` les a).
- **Routes PATCH d'édition** : corriger `danger`/`catégorie` d'un risque,
  `libellé`/`responsable`/`échéance` d'une action, un déchet, une séance de
  formation, les métadonnées d'un document, un permis avant validation.
  Archivage d'un déchet.
- **Recherche + pagination** sur les ~14 tableaux desktop restants
  (composant `BarrePagination` + `useRechercheEtPagination` déjà prêts,
  pilotés sur Risques).
- **PDF** : étendre les boutons à Audits/Revues + fiche inspection + détail
  permis + ligne signalement mobile.
- **Sauvegarde automatique de la base** : job APScheduler + rétention +
  vérifier le chiffrement des secrets dans le dump.
- **Tests instables** (`test_export_pdf::test_export_permis`,
  `test_notifications::test_permis_en_attente_notifie_le_responsable`) :
  corriger le passage de jour dans leur setup.
- **Lien SLAM ↔ permis** par clé étrangère plutôt que par date.
- **`RISQUE` sans `site_id`** : décider (global vs par site).
- **Design** : uniformiser les états de chargement, modale de confirmation
  réutilisable (remplace `window.confirm`), filtres site/période sur le
  tableau de bord, piège de focus clavier dans `Modal.vue`, recherche
  globale d'en-tête, intégration du vrai logo PNG.
- **PostgreSQL** : jamais testé (Docker en attente).
- **Revue de sécurité coffre-fort/auth** dédiée avant prod (§10).

### Lot 3 — Pagination/filtres serveur (capacité) + recherche/pagination sur tous les tableaux desktop

**Back-end** — `app/core/pagination.py` : dépendance FastAPI `pagination`
(`limite`/`decalage`, plafond dur `PLAFOND_ABSOLU = 500`). Sans `limite`, on
renvoie tout jusqu'au plafond (comportement inchangé, rétrocompatible) ;
`limite` reste disponible pour les écrans qui voudront paginer côté serveur.
Appliquée à `/actions` (avec `en_retard` désormais exprimé en SQL pour que la
pagination reste juste), `/inspections` (+ filtre `equipement_id`), `/permis`.
Les volumes réels (quelques centaines de lignes/module) ne justifient pas une
pagination serveur systématique — la vraie optimisation d'affichage est côté
client (ci-dessous).

**Front-end** — `useRechercheEtPagination` + `BarrePagination` (déjà prêts,
pilotés sur Risques) déployés sur **14 tableaux desktop** : Risques, Plan
d'action, Parc, Documents, Inspections, SLAM & permis, Déchets, EPI,
Utilisateurs, Sites, Registre des visiteurs partis, Coffre-fort, Satisfaction,
Matrice de compétences. Chaque écran : champ `.srch` dans l'en-tête,
`elementsPage` dans le `v-for`, `BarrePagination` en pied, ligne « aucune
correspondance ». Prédicats de recherche avec `String()` sur les champs
numériques (bug trouvé sur Risques le 2026-09-10 : `numero.toLowerCase()`
plante silencieusement la réactivité). `AuditsDesktopView` non concerné — pas
de liste plate (campagnes/chapitres imbriqués).

**Vérifié en conditions réelles** : sur les 6 premiers écrans, recherche d'un
terme improbable → message « ne correspond à la recherche », champ vidé →
liste restaurée ; sur les 8 suivants, `.srch` + `.pagin` présents, aucune
erreur de page, données affichées. Pagination serveur `?limite=2` sur
`/actions` → 200.
55 tests Vitest, build de prod OK.

### Lot 4 — Routes PATCH d'édition (corriger une fiche après création)

Aucune route ne permettait de corriger une faute de saisie : il fallait
archiver puis recréer. Ajouté :

- **`PATCH /risques/{id}`** (`RisqueModification`, `require_role
  GERER_RISQUES`) : corrige danger / catégorie / unité de travail / personnes
  exposées. **Ne touche pas la cotation** — elle reste gérée par `/reevaluer`,
  qui empile une nouvelle cotation sans effacer l'historique (§5.2.5).
- **`PATCH /actions/{id}`** (`ActionModification`) : libellé / type de mesure /
  responsable / échéance. Réservé au responsable désigné ou à un rôle de
  gestion ; **refusé (409) sur une action clôturée** (même esprit que le
  changement de statut, aucun retour en arrière). L'origine (risque_id…) ne se
  modifie pas.
- **`PATCH /dechets/{id}`** + **`POST /dechets/{id}/archiver`** : le module
  Déchets n'avait ni édition ni archivage (création + enlèvement seulement).

Piège Python 3.14 rencontré : un champ Pydantic nommé `date` **avec valeur par
défaut** (`date: date | None = None`) masque le type `datetime.date` au moment
de l'évaluation différée de l'annotation → `TypeError: unsupported operand |`.
Corrigé dans `schemas/dechet.py` en qualifiant ce seul champ par `_dt.date`.

**Front-end** : `stores/{risques,actions,dechets}.js` gagnent `modifier()` (et
`archiver()` pour dechets). Bouton « Modifier » + fenêtre modale de correction
sur `RisquesDesktopView`, `ActionsDesktopView` (masqué sur une action
clôturée), `DechetsDesktopView` (+ « Archiver » avec confirmation).

**Vérifié en conditions réelles** : `/gestion/risques` → « Modifier » → le
danger de la ligne change dans le tableau après enregistrement ;
`/gestion/dechets` → « Archiver » → le lot disparaît du registre (2 lignes →
1). 359 tests back-end (9 nouveaux : 3 risque, 3 action, 3 déchet), 55 Vitest,
build de prod OK.

### Lot 5 — Téléchargement des PDF (extension)

Boutons « PDF » ajoutés au-delà des listes Inspections/Permis (lot 2) :
`SignalementsView` (par ligne, mobile — le module est mobile uniquement) ;
`AuditsDesktopView` (« Rapport PDF » de la campagne d'audit en cours).
Vérifié : `/signalements` → 5 boutons, clic → téléchargement réel.

### Lot 6 — Sauvegarde automatique de la base

`Scripts/sauvegarde.py` existait mais n'était planifié nulle part (la contrainte
§2/§4 supposait pourtant des sauvegardes régulières et sans secrets en clair).

- `app/services/sauvegarde_service.py` : logique extraite du script (copie SQLite
  cohérente / `pg_dump` en prod, archive `storage.tar.gz`, manifeste JSON) +
  **rétention** (`purger_anciennes` garde les N plus récentes). `.env` n'est
  JAMAIS inclus (les secrets applicatifs en base sont chiffrés Fernet ; la clé
  maîtresse se conserve hors sauvegarde).
- `app/core/scheduler.py` : job `sauvegarde_quotidienne` (cron, 2 h du matin par
  défaut), erreur journalisée sans faire tomber le planificateur.
- `config.py` : `sauvegarde_active` / `sauvegarde_dir` / `sauvegarde_heure` /
  `sauvegarde_retention`.
- `Scripts/sauvegarde.py` réduit à un lanceur CLI de la fonction du service.
- `tests/test_sauvegarde.py` : 3 tests (archive + manifeste + relecture,
  absence de `.env`, rétention qui supprime les plus anciennes).

### Lot 7 — Tests instables + lien SLAM↔permis

- **Tests instables corrigés** : `test_export_pdf::test_export_permis` et
  `test_notifications::test_permis_en_attente_notifie_le_responsable`
  calculaient `fin_validite = now() + 4h` ; après 20 h ça basculait au
  lendemain et déclenchait la règle « un permis ne couvre qu'une seule
  journée » (422). Créneau ancré à 08 h-12 h du jour même.
- **Lien SLAM↔permis** : reste par heuristique de date (pas de clé étrangère).
  Établir ce lien proprement suppose de décider *quand* il se crée (SLAM saisie
  en amont sur mobile, permis créé ensuite) — c'est une question de flux
  métier, pas un bug ; à trancher avec l'utilisateur avant de toucher à une
  règle de sécurité. **Laissé en l'état, documenté.**

### Lot 8 — Finitions design

- **`components/Modal.vue`** — piège de focus clavier : à l'ouverture le focus
  entre dans la modale (1er champ), Tab/Shift+Tab bouclent à l'intérieur, à la
  fermeture le focus revient sur l'élément déclencheur. Vérifié (focus reste
  dans la modale après 3 Tab).
- **`components/ModalConfirmation.vue`** (nouveau) — confirmation stylée
  réutilisable, remplace `window.confirm()`. Câblée sur les archivages :
  `SitesDesktopView`, `DechetsDesktopView` (remplace `window.confirm`),
  `VisiteursDesktopView` (n'avait aucune confirmation).
- `PermisValidationView` : squelette de chargement (fait au lot 1).

**Reste, hors code / à cadrer avec l'utilisateur :**
- Filtres site + période sur le tableau de bord (le back-end accepte `site_id`).
- Recherche globale d'en-tête (maquette `.srch`).
- Intégration du **logo PNG** (fichier à déposer dans `src/assets/`).
- États « Chargement… » encore en texte brut sur SlamView / InspectionDetailView.
- **PostgreSQL** jamais testé (Docker à installer côté utilisateur).
- **Revue de sécurité coffre-fort / auth** dédiée avant prod (§10) — process,
  pas une tâche de code.

**Bilan des lots 1→8** : 362 tests back-end (au vert, +12 depuis le début de
la revue : signalement, risque, action, déchet, sauvegarde), 55 Vitest, build
de prod OK. Recherche + pagination sur 14 tableaux desktop. Édition possible
sur risques / actions / déchets. PDF téléchargeables. Sauvegarde quotidienne
planifiée. Noms au lieu des identifiants sur l'écran de validation de permis.

### Lot 7 (suite) — Lien SLAM ↔ permis enregistré

Retour de l'utilisateur : « il ne sont pas lié ». Le rapprochement existait
mais n'était que **recalculé à la volée** (par date) à chaque évaluation de la
règle de blocage — rien n'était stocké : impossible de savoir *après coup*
quelle SLAM avait justifié quel permis.

- **Migration `7901cba3e6ab`** : colonne `evaluation_slam.permis_id` (FK
  nullable, `batch_alter_table` pour SQLite comme PostgreSQL).
- **Modèles** : relation `Permis.evaluations_slam` ↔ `EvaluationSlam.permis`,
  + `EvaluationSlam.utilisateur` (avec `foreign_keys` explicite — BaseModel
  ajoute cree_par_id/modifie_par_id, le lien serait sinon ambigu).
- **`permis_service.lier_evaluations_slam(db, permis)`** : pour chaque
  intervenant, rattache son évaluation SLAM la plus récente du jour du
  créneau ; **idempotent** (détache d'abord ce qui ne correspond plus). Le
  rapprochement reste par date — seule clé disponible côté terrain (la SLAM se
  saisit avant que le permis existe) — mais le lien est désormais **écrit**.
  N'établit AUCUN blocage : `regle_blocage_permis.evaluer_controles` reste
  seule juge. Appelée à la création ET à la validation (une SLAM plus récente
  a pu être saisie entre-temps).
- **`PermisSortie.evaluations_slam`** : liste `{id, reference, utilisateur_id,
  utilisateur_nom, decision, date, motif}` — noms résolus côté serveur.
- **`PermisValidationView`** : nouvelle section « Évaluations SLAM
  rattachées » — le responsable voit concrètement quelle SLAM (GO/NO GO,
  horodatage, motif) justifie chaque intervenant.

**Vérifié en conditions réelles** (API) : SLAM GO créée pour l'admin →
création d'un permis avec l'admin en intervenant → réponse `statut: demande`
et `evaluations_slam: [{utilisateur_nom: "Démo Admin", decision: "GO", …}]`.
2 tests pytest (`test_permis.py`) : rattachement à la création ; re-rattachement
d'une SLAM plus récente à la validation (l'ancienne est détachée). 364 tests
back-end au vert, 55 Vitest, build de prod OK.

### Lot 9 — Filtres tableau de bord, recherche globale, dernières éditions, états de chargement

Reprise après une interruption de session ; suite directe de "et par la suite le
reste" (revue d'ensemble).

**Filtres du tableau de bord** — `TableauBordDesktopView` exposait déjà un
back-end acceptant `site_id`/`date_debut`/`date_fin` sans jamais les
proposer. Ajout d'un sélecteur de site + d'une période (30 j / 90 j / 12 mois
/ depuis le début), rechargement automatique au changement (`watch`).

**Recherche globale d'en-tête** — champ « Rechercher partout… » de la
maquette, jamais implémenté. Nouveau `GET /api/v1/recherche?q=` (backend,
`app/api/v1/recherche.py`) : interroge signalements (visibilité restreinte
identique à leur liste — technicien/collaborateur ne voient que les leurs),
risques, actions, permis, équipements, documents (filtrés par
`document_service.lister_documents`, donc déjà par visibilité) ; réponses
typées `{type, id, libelle, sous_libelle}`, plafonnées à 6 par type — recherche
« contient », pas un moteur d'indexation. Store `stores/recherche.js` +
menu déroulant dans `GestionLayout.vue` (debounce 250 ms, clic → navigation
vers l'écran du type). 4 tests pytest, dont un qui vérifie explicitement que
le technicien ne voit pas les signalements des autres dans les résultats.

**Édition — 2 entités restantes** :
- `PATCH /documents/{id}` (`DocumentModification`) : corrige référence /
  intitulé / niveau / confidentialité / date de revue — **uniquement en
  brouillon** (409 au-delà, la voie normale devient « nouvelle version »).
- `PATCH /formations/seances/{id}` (`SeanceModification`) : corrige thème /
  date / lieu / animateur / compétence — **uniquement tant que planifiée**
  (409 après clôture, émargements et quiz déjà rattachés).
Boutons « Modifier » + modales sur `DocumentsDesktopView` et
`FormationsDesktopView`. Même piège Python 3.14 que `dechet.py` rencontré à
nouveau sur `SeanceModification.date` (champ nommé comme son type, valeur par
défaut) — qualifié `_dt.date`.

**États de chargement** — dernier « Chargement… » en texte brut remplacé par
un squelette (`SlamView`, `InspectionDetailView`) : plus aucun écran de
l'application n'affiche ce texte brut.

**Audits — décision documentée, pas un oubli** : cet écran n'a pas de liste
plate (checklist par chapitre au sein d'une seule campagne ouverte, modale de
revue en deux étapes) — le motif `useRechercheEtPagination` / tableau ne s'y
applique pas sans dénaturer l'écran. Laissé tel quel.

**Vérifié en conditions réelles** : tableau de bord → changement de site →
les indicateurs se rechargent ; recherche « BKO » dans l'en-tête → menu avec
« Équipement — BKO-AP-01 MikroTik hAP ac2 » ; document brouillon
`TEST-PDF-…` → « Modifier » → modale → intitulé corrigé → visible
immédiatement dans le tableau ; séance planifiée → bouton « Modifier »
présent.

373 tests back-end (+9 : 2 documents, 3 formations, 4 recherche), 55 Vitest,
build de prod OK.

---

## 2026-09-10 (suite) — Module manquant dans la barre latérale : Paramètres

Retour direct de l'utilisateur : « le système n'affiche pas tous les modules
dans la barre latérale ». Vérification : la barre latérale rendait bien les
17 écrans de gestion existants pour un administrateur (confirmé en
conditions réelles, capture d'écran) — mais en comparant aux 19 écrans
desktop de la maquette (`docs/maquettes/Maquettes_SHEQ_Desktop.html`, tous
les `id="p-*"`), un seul n'avait **jamais été construit** : `#p-param`
(Paramètres). C'était le module manquant.

**Décision d'écart assumée** : la maquette montre des liens « Modifier » sur
les référentiels et les seuils métier. Ces seuils (criticité 4/8/15,
vérification EPI 12 mois, taux de conformité, délais…) sont des **règles
appliquées côté serveur** (CLAUDE.md règle 6, jamais seulement côté
interface — règle 7) : les rendre modifiables serait un changement de portée
sur des règles de sécurité/qualité, à traiter explicitement plutôt que glissé
dans cet écran. L'écran construit est donc **en lecture seule** — aucun
bouton « Modifier » qui ne ferait rien.

- **Backend** `GET /api/v1/parametres` (`app/api/v1/parametres.py`, réservé
  administrateur — `GERER_UTILISATEURS`) : comptages réels (sites,
  équipements, catégories de risques utilisées/total, types de déchets,
  modèles de checklist, compétences de formation) + état réel de la
  sauvegarde automatique (lot du 2026-09-10 — active/heure/rétention,
  nombre d'archives, dernière sauvegarde lue depuis son manifeste JSON).
  Quand aucune sauvegarde n'existe encore, l'écran l'affiche honnêtement
  (« Aucune sauvegarde encore créée », orange) plutôt que d'inventer une date.
- **Frontend** `ParametresDesktopView.vue` : Référentiels, Seuils et règles
  métier (texte de référence, non éditable), Notifications (table statique,
  reprise telle quelle de la maquette — les déclencheurs sont déjà fixes côté
  serveur), Sécurité et sauvegarde. Route `gestion-parametres`, lien ajouté
  dans la section ADMINISTRATION de la barre latérale (administrateur
  uniquement, même périmètre que Utilisateurs & Sites).
- 4 tests pytest : accès réservé admin, comptages réels non inventés,
  état "aucune sauvegarde" honnête, état avec une archive réelle.

**Vérifié en conditions réelles** : lien « Paramètres » présent et cliquable
dans la barre latérale, écran affiche les comptages réels (2 sites, 1
équipement, 3/12 catégories de risque utilisées, 5 modèles de checklist…) et
l'état réel de la sauvegarde (aucune encore créée — honnête, le job
planifié n'a pas encore tourné dans cet environnement de développement).

---

## 2026-09-10 (suite) — Gestion des rôles

Retour direct de l'utilisateur : « je ne vois pas la gestion des rôles ».
L'écran « Utilisateurs & rôles » existait déjà (lien admin-only, section
ADMINISTRATION) mais sa carte « Rôles et périmètres » était un tableau
statique de 5 lignes recopié de CLAUDE.md §6 — pas une gestion des rôles,
juste un mémo. La vraie source de vérité, `app/core/permissions.py`
(~20 constantes `Permissions.X`, chacune un tuple de rôles, vérifiées par
chaque route via `Depends(require_role(*Permissions.X))`), portait déjà ce
commentaire depuis un prompt antérieur : *« utile par exemple pour un futur
écran "gestion des rôles" »* — jamais construit jusqu'ici.

- **`GET /api/v1/roles`** (`app/api/v1/roles.py`, ouvert à tout utilisateur
  authentifié — connaître les périmètres n'est pas sensible, contrairement à
  la gestion des comptes eux-mêmes) : lit `Permissions` **par introspection**
  (`vars(Permissions)`), pas une recopie qui pourrait se désynchroniser du
  code qui applique réellement les droits. Un libellé lisible par clé
  (`LIBELLE_PERMISSION`) est la seule duplication assumée — les rôles
  titulaires de chaque permission sont toujours lus depuis le code réel.
  Garde-fou : `test_permissions_refletent_reellement_permissions_py` compare
  explicitement les clés renvoyées par l'API à celles de `Permissions`.
- **`UtilisateursDesktopView`** : nouvelle carte **« Permissions par rôle »**
  — grille réelle (21 permissions × 5 rôles, coche verte), remplace le
  tableau statique. Volontairement en lecture seule : les rôles sont un
  ensemble fermé de 5 valeurs et les permissions sont du code, pas des
  données de configuration — les rendre éditables serait un changement
  d'architecture (RBAC dynamique), pas un correctif d'affichage.
- 4 tests pytest, dont le garde-fou anti-désynchronisation ci-dessus et la
  vérification de deux permissions précises (`GERER_UTILISATEURS` →
  administrateur seul ; `VALIDER_PERMIS` → responsable + administrateur).

**Vérifié en conditions réelles** : `/gestion/utilisateurs` → 3 cartes
(Utilisateurs, Rôles et périmètres, Permissions par rôle) → grille de 21
lignes × 5 colonnes, cases cochées cohérentes avec le code (ex. « Valider
les permis de travail en hauteur » coché Responsable + Administrateur
seulement). 381 tests back-end (+4), 55 Vitest, build de prod OK.

---

## 2026-09-10 (suite) — Modules du sidebar qui ne s'affichaient pas (pour certains rôles)

Retour direct de l'utilisateur : « mais ils n'affichent [pas] dans les
écran[s] », précisé ensuite : « les modules du sidebar en général ».

**Diagnostic** : pour un administrateur, la barre latérale affichait bien
ses 19 liens (vérifié à plusieurs reprises cette session). Le problème
n'était pas visible pour ce rôle. J'ai donc testé les 4 autres rôles (comptes
de diagnostic créés puis désactivés en fin de vérification — jamais
supprimés) en forçant la navigation vers `/gestion/*` : **4 liens montraient
un module à des rôles qui ne pouvaient pas en charger les données**,
provoquant un écran vide/en erreur (403) au clic — le symptôme observable
correspond bien à « le module ne s'affiche pas » :

| Lien | Route bloquait pour | Permission réelle exigée |
|---|---|---|
| Tableau de bord | technicien, collaborateur | `CONSULTER_TABLEAU_BORD` |
| SLAM & permis | technicien, collaborateur | `CONSULTER_TABLEAU_BORD` (`GET /slam`) |
| Formations | responsable, technicien, collaborateur | `GERER_FORMATIONS` (`GET /formations/competences`) |
| Satisfaction | responsable, technicien, collaborateur | `TRAITER_SATISFACTION` |

Le menu **mobile** (`MenuView.vue`, `peutVoirTableauBord`) avait déjà la
bonne restriction pour le tableau de bord ; la barre latérale **desktop**
(`GestionLayout.vue`) ne l'a jamais reçue — chaque écran a été construit
« un module à la fois » (CLAUDE.md §9) sans revenir mettre à jour la liste
de liens partagée à chaque fois qu'une permission serveur plus étroite que
« tout le monde » était introduite.

**Correctif structurel, pas un simple ravalement** : plutôt que de recopier
à la main 4 listes de rôles de plus (le même geste qui a créé le bug),
`stores/roles.js` (nouveau) devient la **source unique** : il lit
`GET /api/v1/roles` (déjà construit pour la grille « Permissions par rôle »)
et expose `rolesPour(cle)`. Chaque lien sensible du sidebar porte maintenant
une clé `permission` (ex. `"CONSULTER_TABLEAU_BORD"`) au lieu d'une liste de
rôles recopiée ; `UtilisateursDesktopView` a été basculé sur ce même store
(elle avait son propre fetch local, source de duplication). Résultat : la
visibilité de la barre latérale et la grille de permissions ne peuvent plus
diverger l'une de l'autre, ni du code qui applique réellement les droits —
toute permission ajoutée à un futur module apparaîtra correctement des deux
côtés sans intervention manuelle. Coffre-fort (pas de permission unique,
dépend du `role_requis` par secret) garde sa liste de rôles figée, assumé.

Garde-fous ajoutés : une clé `permission` inconnue de l'API est traitée
comme « pas de restriction connue » (lien visible), jamais comme « masqué »
— une faute de frappe ne peut pas faire disparaître un module. Le rendu de
la barre latérale attend que le chargement des permissions ait abouti
(succès OU échec) avant de s'afficher, pour éviter qu'un lien apparaisse un
instant puis disparaisse pour les rôles non habilités.

4 tests Vitest (`stores/roles.test.js`) : un seul chargement par session,
erreur consignée sans être masquée, clé connue vs inconnue.

**Vérifié en conditions réelles** (5 rôles, comptes de diagnostic) :
- administrateur : 19 liens, inchangé (pas de régression) ;
- référent SHEQ : 15 liens, Tableau de bord/SLAM & permis/Formations/
  Satisfaction tous visibles (habilité pour les 4) ;
- responsable : 14 liens, Formations et Satisfaction **désormais masqués**
  (n'y avait pas accès de toute façon) ; Tableau de bord/SLAM & permis
  visibles ;
- technicien : 12 liens, les 4 modules pilotage masqués, Coffre-fort visible ;
- collaborateur : 11 liens, les 4 modules pilotage ET Coffre-fort masqués.

Plus aucune erreur 403 déclenchée par un clic dans la barre latérale, pour
aucun des 5 rôles. 381 tests back-end (inchangés, aucun code serveur modifié
dans ce lot), 59 Vitest (+4), build de prod OK.

**Correction (même jour)** : le gating `permission: "GERER_FORMATIONS"`
appliqué à « Formations » dans le lot précédent était une erreur —
vérification en conditions réelles à l'appui, `GET /formations/competences`
est en fait **ouvert à tous** (seule sa création est réservée) ; seul
`GET /formations/matrice` est restreint (`ROLES_VUE_ENSEMBLE`), et
`FormationsDesktopView` l'appelle déjà dans son propre `try/catch` dédié
(matrice vide affichée, pas d'erreur bloquante — décision déjà prise et
commentée avant cette revue). L'écran fonctionne réellement pour tous les
rôles ; la lecture statique du code qui m'avait fait croire le contraire
confondait le `Depends` de la route `POST /competences` (restreinte) avec
celui de `GET /competences` (ouverte), deux décorateurs voisins dans le
fichier. Retiré ; « Formations » redevient visible à tous, comme sur mobile.
Revérifié en conditions réelles avant et après (contenu affiché, pas de
bannière d'erreur, pour un compte technicien). Tableau de bord, SLAM &
permis et Satisfaction, eux, cassent réellement (bannière d'erreur, données
à zéro) pour les rôles non habilités — confirmé indépendamment pour chacun,
leur masquage reste justifié.

---

## 2026-09-10 (suite) — Déconnexion volontaire

Retour direct de l'utilisateur : « on crée un module pour la déconnexion ».

`auth.deconnecter()` existait déjà (utilisé automatiquement par
`api.definirGestionnaireSessionExpiree` à l'expiration de session, voir
`main.js`) mais n'était câblé à **aucun bouton** : impossible de se
déconnecter volontairement sans vider le stockage du navigateur à la main.

- Icône `i-logout` ajoutée au sprite (porte + flèche sortante, style trait
  Lucide, cohérent avec le reste du jeu).
- **Desktop** (`GestionLayout.vue`) : bouton dans le bloc profil en bas de la
  barre latérale (`.user`), à côté du nom/rôle.
- **Mobile** (`MenuView.vue`) : section « COMPTE » avec bouton « Se
  déconnecter », sous le sélecteur de thème.
- Les deux appellent `auth.deconnecter()` puis redirigent vers l'écran de
  connexion — même geste que la déconnexion automatique. Pas de confirmation
  : action non destructrice (aucune donnée perdue, il suffit de se
  reconnecter).

**Vérifié en conditions réelles** : bouton présent et cliquable sur les deux
interfaces ; après clic, le jeton disparaît de `localStorage` et l'écran de
connexion s'affiche, sur desktop comme sur mobile. 59 tests Vitest (aucune
régression), build de prod OK.

---

## 2026-09-10 (suite) — Photo de profil

Retour direct de l'utilisateur : « permettre à l'utilisateur d'insérer sa
photo lors de la connexion ». Compris comme un ajout en libre-service une
fois connecté (pas littéralement sur l'écran de connexion : aucune photo ne
peut raisonnablement se rattacher à un compte avant que l'identifiant/mot de
passe ne l'aient authentifié) — à confirmer avec l'utilisateur si l'intention
était différente.

**Backend** :
- `Utilisateur.photo` (colonne nullable, chemin relatif sous `storage_dir` —
  même convention que `Signalement.photos`/`Document.fichier`). Migration
  `5b9a3eb3a30b`.
- `POST /auth/moi/photo` (dépôt/remplacement, réutilise
  `core/fichiers.enregistrer_photos` — mêmes règles que les photos de
  signalement : JPEG/PNG/WebP, 5 Mo max) ; `POST /auth/moi/photo/retirer`.
  Toujours en libre-service sur SON PROPRE compte — aucune route ne prend
  d'`utilisateur_id`, impossible par construction de déposer la photo de
  quelqu'un d'autre.
- `auth_service.changer_photo()`/`retirer_photo()` suppriment l'ancien
  fichier du disque au remplacement/retrait : pas une donnée métier tracée
  (règle 2 CLAUDE.md, suppression physique interdite = pour les
  enregistrements, pas pour un blob orphelin), simple nettoyage pour ne pas
  accumuler indéfiniment des fichiers inutilisés.
- `GET /auth/utilisateurs/{id}/photo` : sert le fichier, même visibilité que
  `GET /auth/utilisateurs` (ouvert à tout utilisateur authentifié).
- `UtilisateurSortie.photo` exposé (chemin relatif, jamais l'URL complète).
- 8 tests pytest : dépôt, lecture, 404 sans photo, remplacement (ancien
  fichier bien supprimé), retrait, type de fichier refusé, impossible de
  déposer la photo de quelqu'un d'autre, authentification exigée.

**Frontend** :
- `composables/useAvatar.js` : charge la photo d'un utilisateur en URL objet
  via la route authentifiée (même principe que `ApercuDocument.vue` pour les
  documents — pas de montage statique) ; révoque proprement l'ancienne URL au
  changement/démontage. 4 tests Vitest.
- `components/ModalPhotoProfil.vue` : aperçu circulaire, sélection de
  fichier, "Enregistrer"/"Retirer la photo"/"Annuler" — un seul composant
  partagé entre desktop et mobile (pas de formulaire dupliqué).
- **Desktop** (`GestionLayout.vue`) : l'avatar du bloc profil devient un
  bouton cliquable qui ouvre la modale.
- **Mobile** (`MenuView.vue`) : nouvelle section « COMPTE » avec l'avatar,
  le nom/rôle et un bouton « Ma photo de profil » (au-dessus de « Se
  déconnecter », ajouté juste avant dans le même lot).
- `.av`/`.photo-apercu` (style.css) : `<img>` en `object-fit: cover`,
  repli sur les initiales déjà en place si aucune photo.

**Vérifié en conditions réelles** (desktop ET mobile) : avatar en initiales
au départ → clic → modale → fichier JPEG réel choisi → aperçu affiché →
Enregistrer → modale fermée, avatar affiche la photo → **rechargement complet
de la page → la photo persiste** (confirme qu'elle est bien enregistrée côté
serveur, pas un état local volatile) → Retirer la photo → retour aux
initiales. 389 tests back-end (+8), 63 Vitest (+4), build de prod OK.

## 2026-09-19 — Revue de compatibilité front/back : Signalements (lot 1/n de « tu corriges tout »)

Suite à l'audit statique front/back du prompt précédent (158 routes backend
comparées aux appels frontend) : ~49 routes existaient côté serveur sans
jamais être appelées depuis l'écran, dont plusieurs représentant des
fonctionnalités entières manquantes. Ce lot traite la première et la plus
prioritaire — Signalements, module central du CDC (chapitre 7.2.3) — puis on
descend la liste module par module.

**Constat** : `PATCH /signalements/{id}/statut` et `POST
/signalements/{id}/archiver` existaient depuis le tout premier prompt (1.1),
testés côté serveur, jamais câblés à aucun bouton — un signalement restait
éternellement « NOUVEAU » une fois créé, aucun moyen de le faire progresser
ni de l'archiver depuis l'interface. Autre trou plus surprenant : aucune
route ne permettait de RELIRE une photo jointe après l'envoi (seul son
décompte s'affichait dans la liste, `POST /signalements` acceptait bien les
fichiers mais rien ne les resservait).

**Backend** (`app/api/v1/signalements.py`) :
- Nouvelle route `GET /signalements/{id}/photos/{index}` : sert le fichier
  via `FileResponse`, même règle de visibilité que la consultation du
  signalement (`_visible_par` — 404, pas 403, pour ne pas confirmer
  l'existence d'un signalement hors périmètre). 3 tests pytest : lecture
  réussie, index hors bornes → 404, un technicien ne peut pas lire la photo
  d'un signalement d'un autre technicien (même s'il connaît l'id) alors que
  le référent SHEQ, qui voit tout, le peut.

**Frontend** :
- `stores/signalements.js` : actions `changerStatut(id, statut)`,
  `archiver(id)` et `obtenir(id)` (fiche individuelle, distincte de `liste`
  qui ne sert qu'à l'écran de liste).
- `views/SignalementDetailView.vue` (nouveau, route `/signalements/:id`,
  nom `signalement-detail`) : fiche mobile inspirée de la maquette desktop
  `#p-detail` mais volontairement réduite à ce que les données réelles
  supportent — **écart assumé** : pas de tableau de causes 5M (le champ
  `Signalement.causes` est un texte libre qu'aucune route ne permet encore
  de renseigner), pas d'historique/timeline (aucun modèle ne trace les
  changements de statut), pas de rattachement automatique à un risque. La
  fiche affiche : référence/type/statut, lieu/description, site/date/auteur
  (ou « Anonyme »), miniatures des photos (fetch authentifié en blob, même
  principe que `useAvatar.js`), et les boutons d'action pilotés par
  `TRANSITIONS_AUTORISEES` (Prendre en charge → Marquer les actions
  définies/Clôturer directement → Clôturer), réservés aux rôles habilités
  (`referent_sheq`, `administrateur` — reflet de
  `Permissions.TRAITER_SIGNALEMENTS`), plus Archiver (avec
  `ModalConfirmation`, une fois clôturé) et le téléchargement PDF.
- `views/SignalementsView.vue` : chaque ligne de la liste devient cliquable
  (`role="button" tabindex="0" @keydown.enter`, même convention que
  `ActionsView.vue`) et ouvre la fiche détail — sauf les éléments encore en
  attente de réseau (`enAttente`), qui n'existent pas encore côté serveur.

**Bug d'environnement rencontré pendant la vérification (pas un bug de
code)** : la nouvelle route photo renvoyait 404 alors que le fichier existait
bien sur disque. Cause : deux processus uvicorn zombies tournaient encore
(trouvés via `Get-CimInstance Win32_Process`, survivants d'une session
précédente), et `storage_dir` est configuré en chemin relatif (`./storage`)
— résolu depuis le mauvais répertoire de travail. Un redémarrage propre
depuis `backend/` a suffi ; aucune correction de code nécessaire.

**Vérifié en conditions réelles** (compte de diagnostic `diag.signalements`,
rôle référent SHEQ, créé avec mot de passe connu puis désactivé — jamais
supprimé — une fois la vérification terminée) : liste → clic sur un
signalement NOUVEAU avec photo → fiche détail affiche la photo (image réelle
3048×4064 chargée sans erreur console) → Prendre en charge → EN ANALYSE,
deux boutons proposés → Marquer les actions définies → ACTIONS DÉFINIES, un
seul bouton → Clôturer → CLÔTURÉ, section Traitement disparaît, bouton
Archiver apparaît → confirmation → retour à la liste, le signalement n'y
figure plus, le compteur passe de 5 à 4. 392 tests back-end (+3), 63 Vitest
(inchangé, pas de nouveau test JS ce lot-ci — logique restée côté store/vue
sans branche testable isolément), build de prod OK.

**Reste à traiter** (prochains lots de « tu corriges tout », par ordre de
priorité déjà établi) : EPI (création/affectation/retrait/réforme/
vérification avant utilisation), Formations (émargement, clôture de
séance), Documents (nouvelle version), Permis (clôture), Parc (édition,
import), Revues de direction (solder décision, historique, commentaire IA,
export PDF), boutons PDF restants (Configurations, Revues, SLAM).

## 2026-09-19 (suite) — Revue de compatibilité front/back : EPI (lot 2/n)

Deuxième module de la campagne « tu corriges tout ». Les cinq routes du
registre EPI (prompt 2.1) existaient et étaient testées côté serveur ;
l'écran desktop n'était qu'un tableau de lecture, et le mobile ne câblait
que la vérification périodique officielle.

**Frontend uniquement** (aucune route backend manquante ni modifiée ici) :
- `stores/epi.js` : actions `creer`, `affecter`, `retirer`, `reformer` et
  `verifierAvantUtilisation`.
- `views/EpiDesktopView.vue` : bouton « Nouvel EPI » (formulaire modal :
  type, marque/modèle, dates, porteur optionnel) et, par ligne, « Affecter »
  (sélecteur en ligne), « Retirer » (`ModalConfirmation`, réversible — masqué
  une fois déjà retiré) et « Réformer » (modal avec motif obligatoire,
  irréversible — masqué une fois déjà réformé). Le tout réservé à
  `peutGerer` (referent_sheq/administrateur, reflet de
  `Permissions.GERER_EPI`), même garde locale que le mobile.
- `views/EpiView.vue` : `POST /epi/{id}/verification-avant-utilisation`
  (contrôle léger par le porteur lui-même avant de monter, ouvert à tout
  utilisateur authentifié côté serveur) n'était pas distingué de la
  vérification périodique officielle — seule cette dernière était câblée,
  réservée à `peutVerifier`. Ajout de `estPorteur(item)` : le porteur d'un
  EPI qui n'a pas les droits de gestion voit désormais ce contrôle léger sur
  SES EPI affectés, distinct visuellement (« Contrôle avant utilisation »)
  de la vérification officielle.

**Bug réel trouvé en vérifiant en conditions réelles** (pas dans le code
touché lors des lots précédents, mais mis en évidence en câblant cette
action pour la première fois) : `etat()` (mobile) et `statutTag()`
(desktop) déduisaient le badge « À vérifier » uniquement de la proximité de
`prochaine_verification`, jamais du champ `statut` lui-même. Or un contrôle
NON CONFORME — qu'il soit avant utilisation ou périodique — peut passer
l'EPI à `a_verifier` sans rapprocher cette date (`enregistrer_verification_
avant_utilisation` ne la touche même pas du tout). Résultat observé : un
EPI tout juste déclaré non conforme continuait de s'afficher « EN SERVICE »
partout (liste mobile, tableau desktop, indicateurs « Vérifications dues »/
« dépassées »), alors que `Epi.est_conforme` (utilisé par le blocage réel
des permis, lui, correct) le considérait déjà non conforme. Corrigé dans
les deux écrans : `statut === "a_verifier"` est maintenant vérifié en
priorité, avant le calcul par date.

**Vérifié en conditions réelles** (comptes de diagnostic `diag.epi.referent`
et `diag.epi.tech`, créés puis désactivés) : création d'un EPI (C-002,
casque, affecté au technicien) → affectation modifiée puis rétablie →
retrait (H-001, statut passe à Retiré, bouton Retirer disparaît, compteur
« En service » diminue) → réforme (motif obligatoire rejeté vide, accepté
rempli, statut Réformé, plus aucune action possible, compteur Réformés
augmente) → côté mobile, connecté comme le porteur (pas de droits de
gestion) : la ligne C-002 est cliquable (celle d'un autre EPI ne l'est pas),
panneau « Contrôle avant utilisation » distinct → Non conforme → **badge
passé à « À VÉRIFIER » et bandeau d'alerte apparu** (après correction du
bug ci-dessus — avant, il restait à tort « EN SERVICE ») → confirmé côté
desktop : indicateur « Vérifications dues » passé de 0 à 1, « dont 1
dépassée ». 392 tests back-end (inchangés, aucune route backend touchée),
63 Vitest (inchangés — actions du store trop simples pour justifier un test
isolé, même principe que Signalements), build de prod OK.

**Reste à traiter** : Formations (émargement, clôture de séance), Documents
(nouvelle version), Permis (clôture), Parc (édition, import), Revues de
direction, boutons PDF restants (Configurations, Revues, SLAM).

## 2026-09-19 (suite) — Revue de compatibilité front/back : Formations (lot 3/n)

Troisième module. `POST .../emargement` et `POST .../cloturer` (prompt 4.2)
existaient et étaient testés côté serveur ; l'écran desktop ne permettait
que de créer/corriger des séances, jamais de les faire progresser. En
creusant, deux autres routes déjà écrites mais jamais atteintes : `POST
/formations/competences` (le référentiel de compétences ne pouvait jamais
être alimenté) et la sélection de `competence_id` à la création d'une
séance (le champ existait dans `SeanceCreation` mais aucun `<select>` ne le
proposait).

**Backend** :
- `GET /formations/seances/{id}/emargements` (nouvelle route + service
  `lister_emargements`) : sans elle, un écran d'émargement rouvert perdait
  toute trace des présences déjà enregistrées — seule l'écriture existait.
  1 test pytest (liste vide, puis relit deux présences dont une absence).
- **Bug réel trouvé en vérifiant en conditions réelles** (pas dans le
  périmètre initial de ce lot, découvert en testant le premier bout à bout
  émargement→clôture→matrice) : `GET /formations/matrice` renvoyait des
  `Habilitation` brutes (`HabilitationSortie`), sans jamais résoudre
  `libelle_competence` — la colonne « Compétence » du tableau desktop
  s'affichait vide pour toute la matrice, alors qu'un schéma
  `LigneMatriceCompetence` prévu pour exactement ce besoin existait dans
  `schemas/formation.py` sans jamais être utilisé nulle part. Corrigé en
  séparant `matrice_competences()` (inchangée, réutilisée par
  `/mes-habilitations` qui a besoin de l'`id`) d'une nouvelle
  `matrice_avec_libelles()` dédiée à `/matrice`, qui résout le libellé par
  une seule requête (pas de N+1). Renforcé le test existant
  (`test_matrice_restreinte_mais_mes_habilitations_ouvertes`) pour vérifier
  `libelle_competence` plutôt que la seule longueur de la liste.

**Frontend** :
- `stores/formations.js` : actions `listerEmargements` et `cloturerSeance`
  (`emarger()` existait déjà mais n'était appelée nulle part).
- `views/FormationsDesktopView.vue` : bouton « Nouvelle compétence »
  (modal libellé + périodicité) ; champ « Compétence liée » ajouté au
  formulaire de séance ; par séance encore planifiée, boutons « Émarger »
  (modal à cases à cocher, une par utilisateur, préremplie depuis la
  nouvelle route de lecture, chaque clic enregistre immédiatement) et
  « Clôturer » (`ModalConfirmation`, message qui prévient si des
  habilitations seront renouvelées ou non selon que la séance est liée à
  une compétence). Le tout, ainsi que « Nouvelle séance »/« Modifier »
  déjà existants, réservé à `peutGerer` (referent_sheq/administrateur,
  reflet de GERER_FORMATIONS) — ils ne l'étaient pas jusqu'ici, alors que
  le lien de la barre latérale n'a pas de garde de permission (même classe
  de bug que EPI ce jour).

**Incident d'environnement rencontré pendant la vérification** (pas un bug
de code) : après avoir relancé uvicorn "proprement", la route corrigée
continuait à renvoyer l'ancienne forme. Cause : sur Windows, `uvicorn
--reload` (et plus généralement les process lancés en arrière-plan depuis
Git Bash) peuvent laisser des processus enfants `multiprocessing.spawn`
orphelins qui gardent la socket d'écoute ouverte même après la mort du
parent — `netstat`/`Get-NetTCPConnection` continuaient de rapporter le PID
du parent déjà mort comme propriétaire du port 8000. Identifié en
remontant `parent_pid` depuis la ligne de commande des processus orphelins
(`Get-CimInstance Win32_Process`), puis tué explicitement ; un redémarrage
propre a suffi, aucune correction de code nécessaire.

**Vérifié en conditions réelles** (compte de diagnostic
`diag.form.referent`, créé puis désactivé) : création d'une compétence
(« Travail en hauteur », 12 mois) → création d'une séance liée à cette
compétence → émargement de deux participants présents → fermeture et
réouverture de la modale d'émargement (les cases cochées sont bien
préremplies depuis le serveur) → clôture (message d'avertissement exact
affiché, confirmé) → séance passée « Réalisée », boutons d'action
disparus → matrice de compétences : deux nouvelles lignes « Valide »,
20/09/2026 → 20/09/2027, **avec le libellé de compétence maintenant
affiché** (après correction du bug ci-dessus). 393 tests back-end (+1),
63 Vitest (inchangés — logique de store trop simple pour un test isolé,
même principe que les lots précédents), build de prod OK.

**Reste à traiter** : Documents (nouvelle version), Permis (clôture), Parc
(édition, import), Revues de direction, boutons PDF restants
(Configurations, Revues, SLAM).

## 2026-09-19 (suite) — Revue de compatibilité front/back : Documents et Permis (lots 4-5/n)

Deux lots plus courts, chacun une seule action manquante — aucune route
backend créée ni modifiée, uniquement du câblage frontend vers des routes
déjà écrites et testées.

**Documents — nouvelle version** :
- `stores/documents.js` : action `nouvelleVersion(id, fichier)`. Contrairement
  aux autres actions du store, ne remplace PAS la fiche existante dans la
  liste (`_remplacer`) mais en ajoute une nouvelle (`unshift`) : `POST
  .../nouvelle-version` crée un enregistrement distinct (nouvel id, reparti
  en brouillon), l'ancienne version en vigueur reste inchangée et
  consultable — c'est l'immutabilité des documents en vigueur (le pendant,
  pour ce module, de la règle 5 de CLAUDE.md sur les configurations).
- `views/DocumentsDesktopView.vue` : bouton « Nouvelle version » sur tout
  document `en_vigueur`, réservé à `peutGerer` (referent_sheq/
  administrateur) ; modal avec fichier optionnel (reprend l'ancien si omis,
  comportement déjà géré côté serveur). Pas ajouté à l'écran mobile
  (`DocumentsDossierView.vue`) : la création/révision de documents est déjà,
  par construction de cet écran, une action desktop uniquement (« Nouveau
  document » n'existe pas non plus côté mobile).

**Permis — clôture** :
- `stores/permis.js` : action `cloturer(id)`.
- `views/PermisValidationView.vue` : bouton « Clôturer le permis » quand le
  permis est `delivre`, réservé à un rôle habilité à valider
  (responsable/administrateur, reflet de VALIDER_PERMIS — même garde que
  Valider/Refuser sur ce même écran). Nouvel état d'affichage pour
  `statut === "cloture"` (« Ce permis est clôturé »), qui n'existait pas
  avant (un permis clôturé tombait dans la branche générique et
  réaffichait à tort le formulaire de validation).

**Vérifié en conditions réelles** :
- Documents (compte de diagnostic `diag.form.referent`, réactivé puis
  redésactivé) : clic sur « Nouvelle version » de FOR-SHEQ-001 (v01, en
  vigueur) → message de confirmation correct → création sans nouveau
  fichier → une seconde ligne FOR-SHEQ-001 apparaît, v02, statut brouillon,
  avec Modifier/Soumettre ; la v01 reste en vigueur, inchangée.
- Permis (compte de diagnostic `diag.permis.resp`, créé puis désactivé) :
  permis 2026-001 (délivré) → bouton « Clôturer le permis » visible →
  clic → statut passe à clôturé en base, écran affiche « Ce permis est
  clôturé », plus aucune action proposée.
- Build de prod OK, 63 Vitest inchangés (aucune branche nouvelle isolément
  testable — même principe que les lots précédents), suite pytest complète
  relancée par hygiène malgré l'absence de changement backend.

**Reste à traiter** : Parc (édition, import), Revues de direction, boutons
PDF restants (Configurations, Revues, SLAM).

## 2026-09-19 (suite) — Revue de compatibilité front/back : Parc d'équipements (lot 6/n)

`PATCH /equipements/{id}` et `POST /equipements/import` existaient côté
serveur (testés, prompt 3.1) sans aucune UI — le tableau desktop était en
lecture pour la correction, et l'import en masse (le point d'entrée normal
pour alimenter le parc au démarrage d'un chantier, depuis le gabarit
INV-SHEQ-001) n'était atteignable par aucun bouton.

**Découverte en creusant les permissions** : `Permissions.GERER_PARC =
(TECHNICIEN, ADMINISTRATEUR)` — pas `(REFERENT_SHEQ, ADMINISTRATEUR)` comme
la majorité des autres modules de gestion. C'est cohérent avec CLAUDE.md
§6 (« technicien : saisit configurations, inspections… ») mais ça change la
garde locale à poser côté desktop. Le bouton « Nouvel équipement », déjà
présent, n'avait lui-même **aucune** garde jusqu'ici — un référent SHEQ ou
un responsable atteignant l'écran desktop (le lien de la barre latérale n'a
pas de clé de permission) le voyait et essuyait un 403 au clic. Corrigé au
passage avec les deux mêmes lots.

**Frontend** (aucune route backend créée ni modifiée) :
- `stores/parc.js` : actions `modifierEquipement(id, donnees)` et
  `importerParc(fichier)`.
- `views/ParcDesktopView.vue` : bouton « Nouvel équipement » désormais
  gardé par `peutGerer` (technicien/administrateur, reflet exact de
  GERER_PARC) ; bouton « Modifier » par ligne (même garde), modal de
  correction identique au formulaire de création ; bouton « Importer »
  séparé, gardé par `peutImporter` (responsable/administrateur, reflet
  d'IMPORTER_PARC — rôle distinct et plus restrictif, aucun chevauchement
  avec GERER_PARC) : modal avec sélection de fichier .csv/.xlsx et rapport
  d'import affiché ligne par ligne (nombre importé/en erreur, motif de
  chaque rejet).

**Incident d'environnement rencontré pendant la vérification** (pas un bug
de code) : l'outil de navigateur automatisé a échoué au premier essai
(`ENOENT` sur chrome.exe) — l'extension VSCode dont il dépend s'était mise à
jour pendant l'interruption de session (3.24.64 → 3.24.71), avec une
version de patchright attendant une révision de Chromium différente
(1243) de celle déjà installée (1228). Résolu en installant la révision
manquante (`node node_modules/patchright/cli.js install chromium` depuis le
dossier de la nouvelle version) ; aucune correction de code nécessaire.

**Vérifié en conditions réelles** (comptes de diagnostic
`diag.parc.tech`/`diag.parc.resp`, créés puis désactivés) :
- Technicien : voit « Nouvel équipement » et « Modifier », pas
  « Importer » — modification de l'emplacement d'un équipement existant,
  changement reflété immédiatement dans le tableau.
- Responsable : voit « Importer », ni « Nouvel équipement » ni
  « Modifier » (confirmant l'absence de chevauchement des deux rôles) —
  import d'un CSV à deux lignes (gabarit réel) : 1 équipement importé,
  1 rejeté avec le message exact du serveur (« Site « Antenne Inexistante »
  introuvable »), le nouvel équipement apparaît dans le tableau après
  fermeture de la modale.
- 393 tests back-end (inchangés), 63 Vitest (inchangés), build de prod OK.

**Reste à traiter** : Revues de direction (solder décision, historique,
commentaire IA, export PDF), boutons PDF restants (Configurations, Revues,
SLAM).

## 2026-09-19 (suite) — Revue de compatibilité front/back : Revues de direction et derniers boutons PDF (lots 7-8/n, fin de campagne)

Dernier module substantiel de la campagne « tu corriges tout », plus les
trois boutons PDF encore manquants (Configurations, SLAM, Revues).

**Backend** — `GET /revues` (nouvelle route + service `lister_revues`,
réservée à GERER_REVUES) : aucune route ne permettait jusqu'ici de lister
les revues déjà créées — seules la création et la lecture par id
existaient, rendant une revue invisible dès l'écran de création quitté.
1 test pytest (liste vide, puis contient la revue créée, 403 pour un rôle
non habilité).

**Frontend** :
- `stores/audits.js` : `chargerRevueDetail`, `genererCommentaire`,
  `modifierCommentaire`, `validerCommentaire`, `solderDecision` — toutes
  ces routes (prompt 6.4 et 4.2) existaient côté serveur, testées, sans
  aucune UI pour les atteindre.
- `views/AuditsDesktopView.vue` : la carte « Revue de direction » n'était
  qu'un bouton « Nouvelle revue » sans aucune liste. Ajout d'un tableau des
  revues (référence, date, période, statut du commentaire, PDF) et d'une
  fiche détail (clic sur une ligne) avec commentaire de synthèse
  (génération/édition/validation, banner distinct si validé) et décisions
  (solde). Bouton « Nouvelle revue » et fiche détail réservés à
  `peutGererRevues` (referent_sheq/responsable/administrateur, reflet de
  GERER_REVUES) — même classe de bug que les lots précédents (aucune garde
  locale jusqu'ici, alors que le lien de la barre latérale n'en a pas non
  plus).
- Boutons PDF : `views/ParcFicheView.vue` (configurations,
  `GET /configurations/{id}/export-pdf`) et `views/PermisDesktopView.vue`
  (SLAM, `GET /slam/{id}/export-pdf`) — les deux dernières routes PDF
  jamais atteintes par un bouton.

**Bug réel trouvé et corrigé en vérifiant en conditions réelles** — le plus
sérieux de cette campagne, et le plus long à isoler : après avoir cliqué
« Générer » (commentaire IA), le bouton restait indéfiniment grisé et
aucun message d'erreur ne s'affichait, alors que la requête serveur
réussissait bel et bien (200, vérifié par capture réseau). Isolé par
instrumentation directe du composant (marqueurs `document.title` pour
contourner les artefacts de synchronisation des outils de test) : l'état
réactif local (`actionEnCours`, `erreurDetail`) était correctement mis à
jour en mémoire immédiatement après l'appel, mais **le DOM ne se
mettait jamais à jour pour le refléter** — un vrai bug de rendu Vue, pas
une erreur JS (aucune exception, aucun log). Cause : `genererCommentaire`/
`modifierCommentaire`/`validerCommentaire` **réaffectaient** `this.
revueDetail` à un tout nouvel objet à chaque appel (`this.revueDetail =
await api.requete(...)`), au lieu de muter l'objet existant — cette
réaffectation semble perturber la réconciliation de Vue pour l'ensemble du
sous-arbre `<template v-else-if="audits.revueDetail">` qui l'englobe, y
compris pour des refs locales du composant totalement indépendantes de
`revueDetail` (bouton disabled, banner d'erreur). Corrigé en remplaçant la
réaffectation par `Object.assign(this.revueDetail, resultat)` dans les
trois actions concernées (`solderDecision` était déjà correcte, elle
mutait `decisions[i]` en place) — comportement confirmé résolu par un
test complet en conditions réelles après correctif (voir ci-dessous).
Signalé ici en détail car la cause n'est pas évidente et pourrait
resurgir ailleurs si le même motif de réaffectation d'objet imbriqué est
réutilisé.

**Incidents d'environnement distincts rencontrés pendant l'investigation**
(qui ont considérablement allongé la recherche, mais ne sont pas liés au
bug ci-dessus) : (1) 18 sessions de navigateur automatisé laissées
ouvertes en parallèle sans être fermées ont épuisé les ressources système
(`ERR_INSUFFICIENT_RESOURCES`), provoquant des échecs intermittents sans
rapport avec le code (CORS, chargements de 30 à 70 s) — nettoyé en fermant
toutes les sessions et en tuant les processus Chrome orphelins ; (2) une
route testée par erreur (`/gestion/slam-permis` au lieu du vrai chemin
`/gestion/permis`, nom de route `gestion-permis`) a fait croire un instant
à un écran vide — erreur de frappe dans le test, pas un bug.

**Vérifié en conditions réelles** (comptes de diagnostic
`diag.revues.resp`, `diag.parc.tech`, `diag.permis.resp`, tous créés puis
désactivés) : création d'une revue avec une décision → fiche détail
ouverte → Générer (assistant indisponible en environnement de
développement, sans clé configurée — bandeau d'indisponibilité affiché
correctement, **bouton reste utilisable**, plus de blocage) → commentaire
rédigé manuellement → Enregistrer → Valider (bandeau « Commentaire validé »
affiché) → Solder la décision (statut passé à « Soldée ») → tableau des
revues reflète le nouveau statut « Validé » → téléchargement du PDF de la
revue réussi. Téléchargement PDF de configuration
(`ENR-SHEQ-2026-002.pdf`) et de SLAM (`slam-7.pdf`) confirmés également.
394 tests back-end (+1), 63 Vitest (inchangés), build de prod OK.

**Fin de la campagne « tu corriges tout »** : les 8 lots identifiés lors de
l'audit de compatibilité front/back sont traités (Signalements, EPI,
Formations, Documents, Permis, Parc, Revues de direction, boutons PDF
restants). Chaque route backend jusqu'ici jamais atteinte par un écran a
été soit câblée à une UI, soit — quand aucune UI n'existait pour la lire
(matrice de compétences, liste des revues) — complétée côté serveur par la
route de lecture manquante. Au passage, plusieurs boutons déjà existants
mais sans garde de permission locale ont été corrigés (EPI, Formations,
Parc, Revues) pour éviter des 403 à des rôles atteignant l'écran desktop
sans avoir le droit d'agir.
