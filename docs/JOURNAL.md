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
