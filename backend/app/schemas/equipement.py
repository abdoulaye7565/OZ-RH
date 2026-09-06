"""Schémas Pydantic du module Parc d'équipements (prompt 3.1, section 5.2.3 du CDC)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import MarqueEquipement, StatutEquipement, TypeIntervention


class EquipementCreation(BaseModel):
    identity: str
    marque: MarqueEquipement
    modele: str
    numero_serie: str
    adresse_mac: str | None = None
    site_id: int
    emplacement: str
    date_installation: date
    fin_garantie: date | None = None

    @field_validator("identity")
    @classmethod
    def _identity_normalisee(cls, v: str) -> str:
        from app.services.equipement_service import valider_format_identity

        return valider_format_identity(v)


class EquipementMiseAJour(BaseModel):
    """Le dictionnaire (7.2.4) ne distingue pas de champs non modifiables après
    création pour EQUIPEMENT (contrairement à CONFIGURATION, immuable par
    règle 5 de CLAUDE.md) : tous les champs sont donc ouverts à la mise à
    jour, y compris `identity` — utile par exemple si l'équipement change
    d'emplacement au sein du même site sans le remplacer."""

    identity: str | None = None
    marque: MarqueEquipement | None = None
    modele: str | None = None
    numero_serie: str | None = None
    adresse_mac: str | None = None
    site_id: int | None = None
    emplacement: str | None = None
    date_installation: date | None = None
    fin_garantie: date | None = None
    statut: StatutEquipement | None = None

    @field_validator("identity")
    @classmethod
    def _identity_normalisee(cls, v: str | None) -> str | None:
        if v is None:
            return None
        from app.services.equipement_service import valider_format_identity

        return valider_format_identity(v)


class EquipementSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identity: str
    marque: MarqueEquipement
    modele: str
    numero_serie: str
    adresse_mac: str | None
    site_id: int
    emplacement: str
    date_installation: date
    fin_garantie: date | None
    statut: StatutEquipement
    archive: bool
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None


class ConfigurationResumeSortie(BaseModel):
    """Résumé pour l'historique de la fiche équipement — pas les paramètres
    complets (déjà exposés par le prompt 3.2, hors périmètre de ce prompt)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    type_intervention: TypeIntervention
    technicien_id: int
    date_intervention: datetime


class InspectionResumeSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    statut: str
    taux_conformite: float | None = None


class IncidentResumeSortie(BaseModel):
    """Signalements de type incident/accident du même site que l'équipement —
    voir la limite documentée dans docs/JOURNAL.md (prompt 3.1) : SIGNALEMENT
    n'a pas de lien direct vers EQUIPEMENT dans le dictionnaire de données."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str | None
    type: str
    description: str
    date_constat: datetime
    statut: str


class FicheEquipementSortie(BaseModel):
    """Agrégat pour l'écran "fiche équipement" (figure A.31/A.33 selon la
    page) : équipement + historique complet, tel que demandé par le prompt
    3.1 et la section 5.2.3 du CDC ("configurations, inspections, incidents
    associés")."""

    equipement: EquipementSortie
    configurations: list[ConfigurationResumeSortie]
    inspections: list[InspectionResumeSortie]
    incidents: list[IncidentResumeSortie]


class LigneErreurImport(BaseModel):
    ligne: int
    identity: str | None = None
    erreurs: list[str]


class RapportImport(BaseModel):
    total_lignes: int
    importees: int
    en_erreur: int
    equipements: list[EquipementSortie]
    erreurs: list[LigneErreurImport]
