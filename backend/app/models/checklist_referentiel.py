"""Contenu réel des 5 checklists d'inspection (prompt 2.4), repris tel quel des
formulaires papier du SMI existant — pas inventé :
- FOR-SHEQ-011_Checklists_Inspection.xlsx (feuilles Locaux, Incendie-Extincteurs,
  Électricité)
- FOR-SHEQ-005_Fiche_Inspection_Installations.docx
- FOR-SHEQ-010_Fiche_Inspection_Equipements.docx

Module partagé entre la migration Alembic qui sème ces 93 points en base
(alembic/versions/dafa396b65c4_...) et les fixtures de test
(tests/conftest.py) : dupliquer ce contenu dans les deux aurait fini par
diverger silencieusement.
"""

# Pas de catégorie dans le formulaire source pour ces trois checklists.
LOCAUX: list[str] = [
    "Les circulations et issues sont dégagées et non encombrées",
    "Les câbles électriques et informatiques sont rangés (goulottes, attaches)",
    "Les sols sont propres, secs et en bon état (pas de trous ni d'obstacles)",
    "L'éclairage des locaux est suffisant et fonctionnel",
    "Les postes de travail sont rangés (démarche 5S)",
    "Les sièges de bureau sont en bon état et réglables",
    "Les écrans sont positionnés à bonne hauteur (haut de l'écran au niveau des yeux)",
    "La température des locaux est confortable (climatisation fonctionnelle)",
    "Les locaux sont correctement aérés",
    "Les sanitaires sont propres et approvisionnés (savon, papier)",
    "Les déchets sont collectés et évacués régulièrement",
    "Les produits d'entretien sont stockés dans un endroit dédié et identifié",
    "Le point de rassemblement est identifié et accessible",
    "Les numéros d'urgence sont affichés et visibles",
    "La trousse de premiers secours est complète et accessible",
]

INCENDIE: list[str] = [
    "Les extincteurs sont présents aux emplacements prévus",
    "Les extincteurs sont adaptés aux risques (CO2 pour équipements électriques)",
    "Les extincteurs sont accessibles, visibles et non obstrués",
    "La goupille et le scellé de chaque extincteur sont intacts",
    "La pression des extincteurs est correcte (aiguille en zone verte)",
    "La date de vérification annuelle est valide (étiquette à jour)",
    "La signalisation des extincteurs est visible",
    "Le plan d'évacuation est affiché et à jour",
    "Les issues de secours sont dégagées et déverrouillables",
    "L'alarme incendie (ou moyen d'alerte) est fonctionnelle",
    "Les détecteurs de fumée sont en place et fonctionnels",
    "Aucun stockage de matériaux combustibles près des sources de chaleur",
    "Le personnel connaît la conduite à tenir en cas d'incendie",
    "Un exercice d'évacuation a été réalisé dans les 6 derniers mois",
]

ELECTRICITE: list[str] = [
    "Le tableau électrique est fermé, identifié et accessible",
    "Les disjoncteurs différentiels sont présents et testés",
    "Aucun câble dénudé, endommagé ou réparé au ruban adhésif",
    "Les prises et interrupteurs sont fixés et en bon état",
    "Pas de multiprises surchargées ni de branchements en cascade",
    "Les multiprises utilisées sont conformes (avec protection)",
    "Les rallonges ne traversent pas les zones de passage sans protection",
    "Les équipements présentent leurs fiches et cordons en bon état",
    "Les appareils inutilisés sont éteints en fin de journée",
    "Aucune intervention électrique réalisée par du personnel non habilité",
    "Les onduleurs sont fonctionnels et testés",
    "La vérification périodique par un électricien qualifié est à jour",
    "Aucun appareil de chauffage ou de cuisson non autorisé",
]

# (catégorie, libellé) — catégories reprises des sections A à E/F des formulaires.
INSTALLATIONS: list[tuple[str, str]] = [
    ("A. Structure porteuse et fixations", "La structure porteuse (pylône, mât, charpente de toiture) est saine : pas de corrosion avancée, déformation ou fissure"),
    ("A. Structure porteuse et fixations", "Les supports et brides de fixation des équipements sont serrés et en bon état"),
    ("A. Structure porteuse et fixations", "La boulonnerie est complète, serrée et protégée contre la corrosion"),
    ("A. Structure porteuse et fixations", "Les équipements installés sont solidement fixés (aucun jeu, aucune vibration anormale)"),
    ("A. Structure porteuse et fixations", "La charge ajoutée est compatible avec la structure (pas de surcharge visible)"),
    ("A. Structure porteuse et fixations", "L'étanchéité de la toiture est préservée aux points de fixation et de passage de câbles"),
    ("B. Câblage et alimentation électrique", "Les câbles sont correctement cheminés, fixés et protégés (chemins de câbles, gaines, colliers)"),
    ("B. Câblage et alimentation électrique", "Aucun câble dénudé, pincé, tendu ou endommagé"),
    ("B. Câblage et alimentation électrique", "Les connexions sont bien réalisées et protégées (boîtiers fermés, presse-étoupes serrés)"),
    ("B. Câblage et alimentation électrique", "Les câbles extérieurs sont adaptés à l'usage extérieur (UV, intempéries)"),
    ("B. Câblage et alimentation électrique", "Les alimentations sont protégées (disjoncteurs, parafoudres le cas échéant)"),
    ("B. Câblage et alimentation électrique", "Le repérage / étiquetage des câbles et équipements est en place"),
    ("C. Mise à la terre et protection foudre", "Les équipements et supports métalliques sont reliés à la terre"),
    ("C. Mise à la terre et protection foudre", "Les conducteurs de terre sont continus, fixés et en bon état"),
    ("C. Mise à la terre et protection foudre", "Le dispositif de protection contre la foudre est présent et raccordé (si applicable)"),
    ("C. Mise à la terre et protection foudre", "Les connexions de terre sont serrées et protégées de la corrosion"),
    ("D. Équipements installés", "Les équipements (antennes, caméras, boîtiers, panneaux...) sont en bon état, propres et orientés correctement"),
    ("D. Équipements installés", "Les équipements fonctionnent normalement (test de fonctionnement réalisé)"),
    ("D. Équipements installés", "Les coffrets et armoires sont fermés, verrouillés et étanches"),
    ("D. Équipements installés", "Aucun matériel, outil ou chute de câble n'est resté sur la structure ou la toiture"),
    ("E. Sécurité et accès", "Les moyens d'accès (échelles, crinolines, trappes) sont en bon état et sécurisés"),
    ("E. Sécurité et accès", "Les dispositifs d'ancrage / lignes de vie utilisés pour la maintenance sont en place et en bon état"),
    ("E. Sécurité et accès", "La signalisation de sécurité est présente (danger électrique, accès réservé...)"),
    ("E. Sécurité et accès", "L'accès à l'installation est restreint aux personnes autorisées"),
    ("E. Sécurité et accès", "La zone au sol est propre : aucun déchet ni matériel abandonné après l'intervention"),
]

EQUIPEMENTS: list[tuple[str, str]] = [
    ("A. État physique général", "L'équipement est propre, sans poussière excessive (grilles d'aération dégagées)"),
    ("A. État physique général", "Le boîtier est intact : pas de choc, fissure, trace de surchauffe ou de corrosion"),
    ("A. État physique général", "L'équipement est solidement fixé (rack, mur, mât) et correctement positionné"),
    ("A. État physique général", "L'étiquetage est présent et lisible (identity/nom, référence, date de configuration)"),
    ("A. État physique général", "Les voyants (LED) indiquent un fonctionnement normal"),
    ("B. Câblage et connectique", "Les câbles réseau sont en bon état, connectés et correctement organisés dans la baie"),
    ("B. Câblage et connectique", "Les connecteurs (RJ45, fibre, antenne) sont bien enfichés, sans jeu ni oxydation"),
    ("B. Câblage et connectique", "Les câbles d'alimentation et injecteurs PoE sont en bon état et adaptés"),
    ("B. Câblage et connectique", "Le repérage/étiquetage des câbles est présent et à jour"),
    ("C. Environnement de l'équipement", "La température du local/baie est correcte (ventilation ou climatisation fonctionnelle)"),
    ("C. Environnement de l'équipement", "L'équipement est protégé de l'eau, de la poussière et des nuisibles (rongeurs, insectes)"),
    ("C. Environnement de l'équipement", "Le local technique / la baie est fermé(e) et l'accès est restreint"),
    ("C. Environnement de l'équipement", "Aucun objet étranger ou stockage inapproprié à proximité de l'équipement"),
    ("D. Alimentation électrique et onduleur", "L'alimentation électrique est stable et les prises/multiprises sont conformes"),
    ("D. Alimentation électrique et onduleur", "L'onduleur fonctionne : test de coupure réalisé, autonomie suffisante"),
    ("D. Alimentation électrique et onduleur", "La batterie de l'onduleur est en bon état (pas de gonflement, date de remplacement suivie)"),
    ("D. Alimentation électrique et onduleur", "Les protections (parafoudre, disjoncteur dédié) sont en place"),
    ("E. Fonctionnement et supervision", "L'équipement est joignable (ping / interface de gestion / cloud)"),
    ("E. Fonctionnement et supervision", "Les performances sont normales : débit, signal (antennes), charge CPU/mémoire"),
    ("E. Fonctionnement et supervision", "Aucune alerte ou erreur anormale dans les journaux (logs)"),
    ("E. Fonctionnement et supervision", "L'heure système est correcte (NTP synchronisé)"),
    ("E. Fonctionnement et supervision", "Les équipements de la liaison sans fil affichent un signal dans les objectifs (dBm, CCQ)"),
    ("F. Logiciel, sécurité et sauvegarde", "Le firmware/logiciel est à jour (version stable supportée)"),
    ("F. Logiciel, sécurité et sauvegarde", "Les mots de passe par défaut sont modifiés et les accès de gestion restreints"),
    ("F. Logiciel, sécurité et sauvegarde", "La dernière sauvegarde de configuration est récente et stockée hors équipement"),
    ("F. Logiciel, sécurité et sauvegarde", "La fiche de configuration de l'équipement (FOR-SHEQ-006 à 009) est à jour"),
]


def lignes_a_semer() -> list[dict]:
    """Format neutre {type_inspection, categorie, ordre, libelle}, consommé par
    la migration (colonnes brutes) et par les fixtures de test (via le modèle
    PointChecklist)."""
    lignes = []
    for i, libelle in enumerate(LOCAUX, start=1):
        lignes.append({"type_inspection": "locaux", "categorie": None, "ordre": i, "libelle": libelle})
    for i, libelle in enumerate(INCENDIE, start=1):
        lignes.append({"type_inspection": "incendie", "categorie": None, "ordre": i, "libelle": libelle})
    for i, libelle in enumerate(ELECTRICITE, start=1):
        lignes.append({"type_inspection": "electricite", "categorie": None, "ordre": i, "libelle": libelle})
    for i, (categorie, libelle) in enumerate(INSTALLATIONS, start=1):
        lignes.append({"type_inspection": "installations", "categorie": categorie, "ordre": i, "libelle": libelle})
    for i, (categorie, libelle) in enumerate(EQUIPEMENTS, start=1):
        lignes.append({"type_inspection": "equipements", "categorie": categorie, "ordre": i, "libelle": libelle})
    return lignes
