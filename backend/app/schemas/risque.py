"""Schémas Pydantic du module Risques (prompt 4.1, section 5.2.5 du CDC)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import CategorieRisque, NiveauRisque


class CotationEntree(BaseModel):
    probabilite: int
    gravite: int
    mesures_existantes: str | None = None
    mesures_proposees: str
    date_evaluation: date | None = None

    @field_validator("probabilite", "gravite")
    @classmethod
    def _entre_1_et_5(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError("doit être compris entre 1 et 5")
        return v

    @field_validator("mesures_proposees")
    @classmethod
    def _non_vide(cls, v: str) -> str:
        # Règle 5.2.5 : "tout risque de gravité 4 ou 5 doit comporter au moins une
        # mesure de maîtrise, quelle que soit sa criticité" — déjà couverte pour
        # TOUTE gravité en rendant ce champ obligatoire et non vide sans condition
        # (le dictionnaire, 7.2.2, le marque "Oui" sans distinction de gravité).
        if not v.strip():
            raise ValueError("une mesure de maîtrise proposée est obligatoire")
        return v.strip()


class RisqueCreation(BaseModel):
    danger: str
    categorie: CategorieRisque
    unite_travail: str
    personnes_exposees: str | None = None
    cotation: CotationEntree


class CotationSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    risque_id: int
    probabilite: int
    gravite: int
    criticite: int
    niveau: NiveauRisque
    mesures_existantes: str | None
    mesures_proposees: str
    date_evaluation: date
    auteur_id: int
    cree_le: datetime


class RisqueSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    danger: str
    categorie: CategorieRisque
    unite_travail: str
    personnes_exposees: str | None
    archive: bool
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    # Cotation la plus récente (calculée, jamais stockée sur RISQUE) — None
    # uniquement dans un état transitoire impossible via l'API normale, puisque
    # la création exige toujours une cotation initiale.
    derniere_cotation: CotationSortie | None = None


class RisqueDetailSortie(RisqueSortie):
    # Historique complet (section 5.2.5 : "Consulter l'historique des cotations
    # d'un risque"), le plus récent en premier.
    cotations: list[CotationSortie] = []


class CelluleMatrice(BaseModel):
    probabilite: int
    gravite: int
    criticite: int
    niveau: NiveauRisque
    risques: list[RisqueSortie]


class RevueDueSortie(BaseModel):
    risque_id: int
    numero: int
    danger: str
    derniere_evaluation_le: date
    prochaine_revue_le: date
    jours_restants: int
    due: bool


class LigneErreurImportRisque(BaseModel):
    ligne: int
    numero: int | None = None
    erreurs: list[str]


class RapportImportRisques(BaseModel):
    total_lignes: int
    importes: int
    en_erreur: int
    risques: list[RisqueSortie]
    erreurs: list[LigneErreurImportRisque]
