"""Schémas Pydantic du module Actions (prompt 1.2)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import StatutAction, TypeMesureAction


class ActionCreation(BaseModel):
    libelle: str
    risque_id: int | None = None
    signalement_id: int | None = None
    inspection_id: int | None = None
    type_mesure: TypeMesureAction
    responsable_id: int
    echeance: date

    @model_validator(mode="after")
    def _une_seule_origine(self) -> "ActionCreation":
        origines = [self.risque_id, self.signalement_id, self.inspection_id]
        if sum(o is not None for o in origines) != 1:
            raise ValueError(
                "Une action doit être rattachée à exactement une origine : "
                "risque_id, signalement_id ou inspection_id"
            )
        return self


class AvancementMiseAJour(BaseModel):
    avancement: int
    indicateur: str | None = None


class StatutMiseAJour(BaseModel):
    statut: StatutAction


class ActionSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str
    risque_id: int | None
    signalement_id: int | None
    inspection_id: int | None
    type_mesure: TypeMesureAction
    responsable_id: int
    echeance: date
    avancement: int
    statut: StatutAction
    indicateur: str | None
    archive: bool
    # Calculé (chapitre 7.3.2 du CDC), jamais stocké : voir action_service.est_en_retard.
    en_retard: bool
    # Traçabilité (règle 3, CLAUDE.md ; cas de recette 13, CDC chapitre 14).
    cree_le: datetime
    cree_par_id: int | None
    modifie_le: datetime
    modifie_par_id: int | None


class SyntheseActions(BaseModel):
    par_statut: dict[str, int]
    nombre_en_retard: int
    taux_avancement_global: float
