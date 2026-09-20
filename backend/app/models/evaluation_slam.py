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
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, enum_column
from app.models.enums import DecisionSlam

if TYPE_CHECKING:
    from app.models.permis import Permis
    from app.models.utilisateur import Utilisateur


class EvaluationSlam(BaseModel):
    __tablename__ = "evaluation_slam"

    # Nullable : généré paresseusement au premier export PDF (prompt 5.1), pas
    # à la création — le SLAM n'a jamais eu besoin de référence avant cet
    # export, inutile d'en attribuer une à des évaluations qui ne seront
    # jamais exportées.
    reference: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    # Liste de 4 listes de 4 booléens (une par étape/point) — voir
    # app/models/slam_referentiel.py pour le libellé de chaque point.
    etapes_validees: Mapped[list] = mapped_column(JSON, nullable=False)
    decision: Mapped[DecisionSlam] = mapped_column(enum_column(DecisionSlam, "decision_slam"), nullable=False)
    # Obligatoire si décision NO_GO uniquement (règle de service, pas de contrainte SQL).
    motif: Mapped[str | None] = mapped_column(String(300), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Permis auquel cette évaluation a servi de justificatif SLAM (revue
    # d'ensemble 2026-09-10 : "ils ne sont pas liés"). Le rattachement se fait
    # à la création / re-validation du permis — pour chaque intervenant, son
    # évaluation la plus récente du jour du créneau. Nullable : une évaluation
    # SLAM peut exister sans permis (saisie en amont, ou intervention au sol).
    permis_id: Mapped[int | None] = mapped_column(ForeignKey("permis.id"), nullable=True)
    permis: Mapped["Permis | None"] = relationship("Permis", back_populates="evaluations_slam")
    # `foreign_keys` explicite : BaseModel ajoute aussi cree_par_id /
    # modifie_par_id (FK vers utilisateur), le lien serait sinon ambigu.
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur", foreign_keys=[utilisateur_id])
