"""Entité EVALUATION_SLAM — non détaillée par le dictionnaire (chapitre 7.2),
reconstituée depuis le MCD et la section 5.2.2. Les quatre étapes et leurs points de
contrôle sont modélisés en JSON plutôt qu'en sous-tables (aucune entité ÉTAPE_SLAM
n'existe dans la liste des 14 entités demandées) — à revoir au prompt 2.2/2.3 si la
UI a besoin d'interroger les points individuellement côté serveur.

Point non résolu, à traiter explicitement au prompt 2.2 : le MCD ne relie pas
EVALUATION_SLAM à PERMIS. La règle de blocage ("un intervenant n'a pas de SLAM en
GO") devra donc chercher la évaluation la plus récente de l'intervenant plutôt que
suivre une clé étrangère directe — la fenêtre de validité ("la plus récente" =
aujourd'hui ? avant le créneau du permis ?) reste à définir avec le référent SHEQ.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import DecisionSlam


class EvaluationSlam(BaseModel):
    __tablename__ = "evaluation_slam"

    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    # Liste des 4 étapes, chacune avec ses points de contrôle et leur validation.
    etapes_validees: Mapped[dict] = mapped_column(JSON, nullable=False)
    decision: Mapped[DecisionSlam] = mapped_column(enum_column(DecisionSlam, "decision_slam"), nullable=False)
    # Obligatoire si décision NO_GO uniquement (règle de service, pas de contrainte SQL).
    motif: Mapped[str | None] = mapped_column(String(300), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
