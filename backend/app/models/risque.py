"""Entité RISQUE — CDC chapitre 7.2.2.

Le dictionnaire modélise RISQUE avec une seule cotation (probabilite/gravite/
criticite/niveau/date_evaluation) intégrée à l'entité elle-même. Mais la
section 5.2.5 ("Une réévaluation ne remplace pas la cotation antérieure :
elle s'ajoute à l'historique") est incompatible avec des colonnes à valeur
unique — le dictionnaire décrit la fonctionnalité sans donner de structure
pour l'historique (aucune entité COTATION/HISTORIQUE n'existe au chapitre 7).
Scindé au prompt 4.1 : RISQUE ne porte plus que l'identité stable du risque
(numéro, danger, catégorie, unité de travail, personnes exposées) ; la
cotation (probabilité, gravité, mesures, date, auteur) vit dans la nouvelle
entité CotationRisque — une par (ré)évaluation, jamais modifiée après coup.
Même principe que POINT_CHECKLIST (prompt 2.4) : une 16e table hors du
dictionnaire des 14, ajoutée par nécessité fonctionnelle et signalée comme
telle plutôt que d'être passée sous silence.
"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import CategorieRisque


class Risque(BaseModel):
    __tablename__ = "risque"

    numero: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    danger: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[CategorieRisque] = mapped_column(
        enum_column(CategorieRisque, "categorie_risque"), nullable=False
    )
    unite_travail: Mapped[str] = mapped_column(String(80), nullable=False)
    personnes_exposees: Mapped[str | None] = mapped_column(String(120), nullable=True)
