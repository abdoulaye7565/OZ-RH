"""Entité INSPECTION — non détaillée par le dictionnaire (chapitre 7.2), reconstituée
depuis le MCD et la section 5.3.1. Comme pour EVALUATION_SLAM, les points de
checklist et leur cotation (C/NC/SO) sont modélisés en JSON : aucune entité
MODELE_CHECKLIST ou POINT_INSPECTION ne figure dans la liste des 14 entités
demandées. Une entité dédiée aux modèles de checklists paramétrables sera
probablement nécessaire pour gérer leur cycle de vie propre (créer/modifier un
modèle) — à évaluer au prompt 2.4."""
from datetime import date

from sqlalchemy import Date, ForeignKey, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutInspection, TypeInspection


class Inspection(BaseModel):
    __tablename__ = "inspection"

    modele: Mapped[TypeInspection] = mapped_column(enum_column(TypeInspection, "type_inspection"), nullable=False)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), nullable=False)
    inspecteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    # Liste des points : {libelle, cotation: "C"|"NC"|"SO", observation, photo}.
    points: Mapped[list] = mapped_column(JSON, nullable=False)
    # Calculé (règle 6, CLAUDE.md) : conformes / (conformes + non conformes), SO exclus.
    taux_conformite: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    statut: Mapped[StatutInspection] = mapped_column(
        enum_column(StatutInspection, "statut_inspection"), default=StatutInspection.EN_COURS, nullable=False
    )
