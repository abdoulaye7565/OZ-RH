"""Schémas Pydantic du module Fiches de configuration (prompt 3.2, section 5.2.3
du CDC). Champs propres à chaque marque, repris des fiches papier réelles
(FOR-SHEQ-006 à 009, CONFIDENTIEL — lues localement pour leur seule structure de
champs, jamais copiées ni versionnées, voir docs/formulaires/LISEZ-MOI.txt),
à l'exclusion explicite de leur section « Identifiants d'accès (CONFIDENTIEL) » :
aucun champ mot de passe/identifiant ne doit exister ici (règle de conception,
section 5.2.3 : « toute saisie d'identifiant se fait exclusivement dans le
module coffre-fort »). `extra="forbid"` sur chaque schéma de paramètres est la
garantie structurelle de cette règle : une liste blanche de champs autorisés
empêche par construction qu'un champ mot de passe s'y glisse, plutôt que de
compter sur une liste noire de noms interdits."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MarqueEquipement, TypeIntervention


class ParametresReseauMikroTik(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adresse_ip_masque: str | None = None
    passerelle: str | None = None
    dns: str | None = None
    dhcp_serveur: str | None = None
    bridge_vlan: str | None = None
    nat_masquerade: bool | None = None


class ParametresSansFilMikroTik(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str
    frequence: str
    protocole: str | None = None


class ParametresReseauGrandstream(BaseModel):
    """Le formulaire papier (FOR-SHEQ-007) place la téléphonie (SIP) dans une
    section dédiée, distincte du réseau — mais le dictionnaire de données
    (7.2.5) ne prévoit que deux champs "Structure" pour CONFIGURATION
    (parametres_reseau, parametres_sansfil), et Grandstream n'a pas de volet
    sans fil : les champs SIP sont donc regroupés ici plutôt que d'ajouter une
    troisième colonne JSON pour cette seule marque — à signaler."""

    model_config = ConfigDict(extra="forbid")

    mode_ip: str | None = None
    adresse_ip_masque: str | None = None
    passerelle: str | None = None
    dns: str | None = None
    vlan_voix: str | None = None
    serveur_sip: str
    extension: str
    codecs: str | None = None
    trunks: str | None = None


class ParametresReseauUbiquiti(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adresse_ip_masque: str | None = None
    passerelle: str | None = None
    mode_reseau: str | None = None
    vlan_gestion: str | None = None


class ParametresSansFilUbiquiti(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    frequence: str
    airmax_active: bool | None = None
    capacite_mbps: float | None = None


class ParametresReseauRuijie(BaseModel):
    """Même compromis que Grandstream : VLAN/ports/mode de gestion cloud sont des
    champs explicitement demandés par le prompt 3.2 pour cette marque, regroupés
    ici faute de troisième champ "structure" dédié — pas de volet sans fil
    distinct construit pour Ruijie dans ce prompt (le formulaire papier réel en
    a un, hors périmètre explicite du prompt)."""

    model_config = ConfigDict(extra="forbid")

    vlan: str | None = None
    ports: str | None = None
    mode_gestion_cloud: str


class ConfigurationCreation(BaseModel):
    equipement_id: int
    type_intervention: TypeIntervention
    version_logicielle: str | None = None
    parametres_reseau: dict
    parametres_sansfil: dict | None = None
    # Section 4 des fiches réelles (MikroTik, Ubiquiti) : "objectif : -50 à -65"
    # / "objectif : > 90" — sans objet pour Grandstream/Ruijie (laissés à None).
    signal_dbm: float | None = None
    ccq_pourcent: int | None = None
    date_intervention: datetime | None = None


class ConfigurationSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    equipement_id: int
    type_intervention: TypeIntervention
    version_logicielle: str | None
    parametres_reseau: dict | None
    parametres_sansfil: dict | None
    signal_dbm: float | None
    ccq_pourcent: int | None
    tests_realises: dict | None
    fichiers_sauvegarde: list[str] | None
    technicien_id: int
    date_intervention: datetime
    archive: bool
    cree_le: datetime
    cree_par_id: int | None
    # Calculés (comparaison aux seuils paramétrés, chapitre 5.2.3 : "Les valeurs
    # mesurées hors des seuils paramétrés sont signalées visuellement") : None
    # tant que la mesure correspondante est absente (marque sans signal/CCQ).
    signal_conforme: bool | None = None
    ccq_conforme: bool | None = None
