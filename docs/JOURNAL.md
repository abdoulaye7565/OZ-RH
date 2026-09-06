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
