"""Schémas Pydantic du module EPI (prompt 2.1, section 5.3.2 du CDC)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatutEpi, TypeEpi


class EpiCreation(BaseModel):
    type: TypeEpi
    marque_modele: str
    date_fabrication: date | None = None
    date_mise_service: date
    date_limite: date
    porteur_id: int | None = None


class AffectationMiseAJour(BaseModel):
    porteur_id: int | None = None


class VerificationPeriodiqueEntree(BaseModel):
    conforme: bool
    observation: str | None = None


class VerificationAvantUtilisationEntree(BaseModel):
    conforme: bool
    observation: str | None = None


class ReformeEntree(BaseModel):
    motif: str


class EpiSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    type: TypeEpi
    marque_modele: str
    date_fabrication: date | None
    date_mise_service: date
    date_limite: date
    porteur_id: int | None
    derniere_verification: date | None
    prochaine_verification: date | None
    statut: StatutEpi
    motif_reforme: str | None
    archive: bool
    # Calculé (chapitre 7.3.2 du CDC) : voir Epi.est_conforme.
    est_conforme: bool
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None
