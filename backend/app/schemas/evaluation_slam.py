"""Schémas Pydantic du module SLAM (prompt 2.2, section 5.2.2 du CDC).

L'évaluation est soumise en un seul envoi (pas d'appel serveur par étape) : le
mobile déroule les 4 écrans localement, y compris hors connexion, puis
transmet le résultat complet à la fin. "Empêcher le passage à l'étape
suivante tant que tout n'est pas validé" est donc traduit ici en une règle
serveur équivalente mais non identique : impossible d'enregistrer une
décision GO si un seul des 16 points (4 étapes × 4) n'est pas coché — le
détail de la progression écran par écran reste une responsabilité du client
(prompt 2.3), la donnée qui compte pour le serveur est le résultat final.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import DecisionSlam
from app.models.slam_referentiel import NOMBRE_ETAPES, NOMBRE_POINTS_PAR_ETAPE


class EvaluationSlamCreation(BaseModel):
    etapes_validees: list[list[bool]]
    decision: DecisionSlam
    motif: str | None = None

    @model_validator(mode="after")
    def _valider_forme_et_coherence(self) -> "EvaluationSlamCreation":
        if len(self.etapes_validees) != NOMBRE_ETAPES or any(
            len(etape) != NOMBRE_POINTS_PAR_ETAPE for etape in self.etapes_validees
        ):
            raise ValueError(
                f"etapes_validees doit contenir exactement {NOMBRE_ETAPES} étapes de "
                f"{NOMBRE_POINTS_PAR_ETAPE} points chacune"
            )
        if self.decision == DecisionSlam.GO and not all(all(etape) for etape in self.etapes_validees):
            raise ValueError(
                "Impossible d'enregistrer une décision GO : tous les points des 4 étapes "
                "doivent être validés"
            )
        if self.decision == DecisionSlam.NO_GO and not self.motif:
            raise ValueError("Un motif est obligatoire pour une décision NO GO")
        return self


class EvaluationSlamSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str | None
    utilisateur_id: int
    etapes_validees: list[list[bool]]
    decision: DecisionSlam
    motif: str | None
    date: datetime
    archive: bool
