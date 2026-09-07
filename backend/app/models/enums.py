"""Énumérations Python pour tous les champs de type énuméré du dictionnaire de données
(cahier des charges, chapitre 7) et des modules fonctionnels associés (chapitre 5).
"""
import enum


class RoleUtilisateur(str, enum.Enum):
    """Chapitre 4 du CDC utilise le libellé « referent » ; CLAUDE.md (point 6) utilise
    « referent_sheq ». Les deux documents de référence se contredisent sur ce point
    précis : c'est le libellé de CLAUDE.md qui est retenu ici, car c'est lui qui porte
    la matrice des droits détaillée par rôle. À signaler."""

    ADMINISTRATEUR = "administrateur"
    REFERENT_SHEQ = "referent_sheq"
    RESPONSABLE = "responsable"
    TECHNICIEN = "technicien"
    COLLABORATEUR = "collaborateur"


class TypeSite(str, enum.Enum):
    """Non détaillé au dictionnaire (chapitre 7) ; déduit de la section 5.2.3, qui
    distingue les équipements « déployés au siège ou chez un client »."""

    SIEGE = "siege"
    CLIENT = "client"


class CategorieRisque(str, enum.Enum):
    """Le CDC (chapitre 7.2.2) annonce « dix valeurs » sans les lister. Les valeurs
    ci-dessous sont reprises telles quelles du registre réel en service
    (docs/REG-SHEQ-001_Registre_des_Risques.xlsx, feuille « Registre », colonne B) :
    on y trouve en réalité 12 libellés distincts, dont deux variantes proches
    (« Incendie » et « Incendie / Urgences ») qui semblent relever de la même
    famille sans avoir été harmonisées dans le classeur source. Conservées
    séparément par fidélité à la donnée réelle plutôt que fusionnées arbitrairement
    — à trancher avec le référent SHEQ avant l'import prévu au prompt 4.1."""

    ERGONOMIQUE = "Ergonomique"
    ELECTRIQUE = "Électrique"
    INCENDIE = "Incendie"
    CHUTE_CIRCULATION = "Chute / Circulation"
    PSYCHOSOCIAL = "Psychosocial (RPS)"
    MANUTENTION = "Manutention"
    AMBIANCES_PHYSIQUES = "Ambiances physiques"
    HYGIENE_BIOLOGIQUE = "Hygiène / Biologique"
    SECURITE_INFORMATION = "Sécurité de l'information"
    SECURITE_SURETE = "Sécurité / Sûreté"
    ROUTIER_TRAJET = "Routier / Trajet"
    INCENDIE_URGENCES = "Incendie / Urgences"


class NiveauRisque(str, enum.Enum):
    """Calculé — jamais saisi. Seuils exacts confirmés par le classeur réel
    (feuille « Cotation ») : faible si criticité < 4, modéré si 4 ≤ c < 8,
    élevé si 8 ≤ c < 15, critique si criticité ≥ 15."""

    FAIBLE = "faible"
    MODERE = "modéré"
    ELEVE = "élevé"
    CRITIQUE = "critique"


class TypeMesureAction(str, enum.Enum):
    """Non énuméré au dictionnaire ; valeurs usuelles en prévention SHEQ, à confirmer
    avec le référent SHEQ."""

    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"
    AMELIORATION = "amelioration"


class StatutAction(str, enum.Enum):
    """Non énuméré au dictionnaire. Le statut « en retard » du prompt 1.2 est traité
    comme un état calculé à partir de l'échéance, pas comme une valeur stockée
    supplémentaire — voir la propriété calculée sur le modèle Action."""

    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    CLOTUREE = "cloturee"


class TypeSignalement(str, enum.Enum):
    SITUATION_DANGEREUSE = "situation_dangereuse"
    PRESQUE_ACCIDENT = "presque_accident"
    ANOMALIE = "anomalie"
    INCIDENT = "incident"
    ACCIDENT = "accident"


class StatutSignalement(str, enum.Enum):
    NOUVEAU = "nouveau"
    EN_ANALYSE = "en_analyse"
    ACTIONS_DEFINIES = "actions_definies"
    CLOTURE = "cloture"


class MarqueEquipement(str, enum.Enum):
    MIKROTIK = "MikroTik"
    GRANDSTREAM = "Grandstream"
    UBIQUITI = "Ubiquiti"
    RUIJIE = "Ruijie"
    AUTRE = "autre"


class StatutEquipement(str, enum.Enum):
    EN_SERVICE = "en_service"
    EN_PANNE = "en_panne"
    EN_MAINTENANCE = "en_maintenance"
    RETIRE = "retire"


class TypeIntervention(str, enum.Enum):
    INSTALLATION = "installation"
    RECONFIGURATION = "reconfiguration"
    MISE_A_JOUR = "mise_a_jour"
    DEPANNAGE = "depannage"
    ALIGNEMENT = "alignement"


class TypeAcces(str, enum.Enum):
    ADMINISTRATION = "administration"
    CLE_RESEAU = "cle_reseau"
    COMPTE_CLOUD = "compte_cloud"
    AUTRE = "autre"


class ActionJournal(str, enum.Enum):
    CONSULTATION = "consultation"
    CREATION = "creation"
    MODIFICATION = "modification"


class TypeEpi(str, enum.Enum):
    HARNAIS = "harnais"
    LONGE = "longe"
    ANTICHUTE_MOBILE = "antichute_mobile"
    CASQUE = "casque"
    CONNECTEUR = "connecteur"
    LIGNE_DE_VIE = "ligne_de_vie"


class StatutEpi(str, enum.Enum):
    EN_SERVICE = "en_service"
    A_VERIFIER = "a_verifier"
    RETIRE = "retire"
    REFORME = "reforme"


class SupportPermis(str, enum.Enum):
    PYLONE = "pylone"
    TOITURE = "toiture"
    ECHELLE = "echelle"
    AUTRE = "autre"


class StatutPermis(str, enum.Enum):
    DEMANDE = "demande"
    BLOQUE = "bloque"
    DELIVRE = "delivre"
    CLOTURE = "cloture"
    REFUSE = "refuse"


class DecisionSlam(str, enum.Enum):
    GO = "GO"
    NO_GO = "NO_GO"


class TypeInspection(str, enum.Enum):
    """Modèles de checklists cités au prompt 2.4 (section 5.3.1 du CDC ne les énumère
    pas explicitement)."""

    LOCAUX = "locaux"
    INCENDIE = "incendie"
    ELECTRICITE = "electricite"
    INSTALLATIONS = "installations"
    EQUIPEMENTS = "equipements"


class StatutInspection(str, enum.Enum):
    EN_COURS = "en_cours"
    CLOTUREE = "cloturee"


class CotationPoint(str, enum.Enum):
    CONFORME = "C"
    NON_CONFORME = "NC"
    SANS_OBJET = "SO"


class NiveauDocument(int, enum.Enum):
    """Reprend la hiérarchie à quatre niveaux du SMI documentaire existant
    (01-Politique, 02-Pilotage, 03-Procédures, 04-Formulaires)."""

    POLITIQUE = 1
    PILOTAGE = 2
    PROCEDURE = 3
    FORMULAIRE = 4


class StatutDocument(str, enum.Enum):
    """Non énuméré explicitement ; déduit des règles de gestion 5.3.5 (approbation,
    version unique en vigueur, archivage)."""

    BROUILLON = "brouillon"
    EN_APPROBATION = "en_approbation"
    EN_VIGUEUR = "en_vigueur"
    ARCHIVE = "archive"


class ConfidentialiteDocument(str, enum.Enum):
    NORMAL = "normal"
    CONFIDENTIEL = "confidentiel"


class StatutSeance(str, enum.Enum):
    """Non énuméré par le CDC (section 5.3.3 ne détaille pas de cycle de vie
    explicite) ; déduit du couple "séances planifiées et réalisées" (données
    gérées) et de la fonctionnalité d'émargement, qui suppose une séance déjà
    tenue."""

    PLANIFIEE = "planifiee"
    REALISEE = "realisee"
    ANNULEE = "annulee"


class StatutDecisionRevue(str, enum.Enum):
    """Non énuméré par le CDC ; déduit de la règle 5.3.4 "les décisions de revue
    non soldées sont automatiquement reportées"."""

    OUVERTE = "ouverte"
    SOLDEE = "soldee"


class Recommandation(str, enum.Enum):
    """Trois valeurs reprises telles quelles de FOR-SHEQ-018 ("Recommanderiez-vous
    Hirondelles IT Lab ?")."""

    OUI_CERTAINEMENT = "oui_certainement"
    PROBABLEMENT = "probablement"
    NON = "non"


class TypeNotification(str, enum.Enum):
    """Reprend une à une les huit lignes du tableau 3 (chapitre 6.3 du CDC,
    "Règles de notification")."""

    NOUVEAU_SIGNALEMENT = "nouveau_signalement"
    PERMIS_EN_ATTENTE = "permis_en_attente"
    DECISION_NO_GO = "decision_no_go"
    ACTION_ECHEANCE = "action_echeance"
    EPI_VERIFICATION = "epi_verification"
    INSPECTION_PLANIFIEE = "inspection_planifiee"
    SATISFACTION_FAIBLE = "satisfaction_faible"
    DOCUMENT_REVUE = "document_revue"


class CanalNotification(str, enum.Enum):
    """Colonne "Canal" du tableau 3 : "Application", "Application et courriel"
    ou "Courriel" (jamais "courriel seul" en dehors de la satisfaction faible,
    mais la valeur existe pour rester fidèle à chaque ligne du tableau)."""

    APPLICATION = "application"
    COURRIEL = "courriel"
    LES_DEUX = "les_deux"
