"""Entité EVALUATION_SLAM — non détaillée par le dictionnaire (chapitre 7.2),
reconstituée depuis le MCD et la section 5.2.2. Les quatre étapes et leurs points de
contrôle sont modélisés en JSON plutôt qu'en sous-tables (aucune entité ÉTAPE_SLAM
n'existe dans la liste des 14 entités demandées) — voir app/models/slam_referentiel.py
pour le contenu canonique des 4 étapes.

Point résolu au prompt 2.2 (ouvert depuis le 0.2) : le MCD ne relie pas
EVALUATION_SLAM à PERMIS, donc la règle de blocage cherche l'évaluation la plus
récente de l'intervenant DATÉE DU MÊME JOUR que le début du créneau du permis
(voir app/services/regle_blocage_permis.py) — pas une clé étrangère directe, pas
« la plus récente, point final » (une décision d'hier ne doit pas couvrir une
montée d'aujourd'hui). Choix à confirmer avec le référent SHEQ si la réalité du
terrain diffère.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import DecisionSlam


class EvaluationSlam(BaseModel):
    __tablename__ = "evaluation_slam"

    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    # Liste de 4 listes de 4 booléens (une par étape/point) — voir
    # app/models/slam_referentiel.py pour le libellé de chaque point.
    etapes_validees: Mapped[list] = mapped_column(JSON, nullable=False)
    decision: Mapped[DecisionSlam] = mapped_column(enum_column(DecisionSlam, "decision_slam"), nullable=False)
    # Obligatoire si décision NO_GO uniquement (règle de service, pas de contrainte SQL).
    motif: Mapped[str | None] = mapped_column(String(300), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
