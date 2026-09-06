"""Schémas Pydantic du module Actions (prompt 1.2)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import StatutAction, TypeMesureAction


class ActionCreation(BaseModel):
    libelle: str
    risque_id: int | None = None
    signalement_id: int | None = None
    inspection_id: int | None = None
    # Ajouté au prompt 4.2 : "Créer une action corrective à partir d'un écart"
    # (section 5.3.4) — anticipé dans le modèle Action depuis le prompt 1.2.
    cotation_audit_id: int | None = None
    # Ajouté au prompt 4.3 : section 5.3.6, "toute note ≤ 2 déclenche...
    # l'ouverture d'une analyse".
    reponse_satisfaction_id: int | None = None
    type_mesure: TypeMesureAction
    responsable_id: int
    echeance: date

    @model_validator(mode="after")
    def _une_seule_origine(self) -> "ActionCreation":
        origines = [
            self.risque_id,
            self.signalement_id,
            self.inspection_id,
            self.cotation_audit_id,
            self.reponse_satisfaction_id,
        ]
        if sum(o is not None for o in origines) != 1:
            raise ValueError(
                "Une action doit être rattachée à exactement une origine : "
                "risque_id, signalement_id, inspection_id, cotation_audit_id ou reponse_satisfaction_id"
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
    cotation_audit_id: int | None
    reponse_satisfaction_id: int | None
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
