"""Entité INSPECTION — non détaillée par le dictionnaire (chapitre 7.2), reconstituée
depuis le MCD et la section 5.3.1.

`taux_conformite` était une colonne stockée depuis le prompt 0.2 ; convertie en
propriété calculée au prompt 2.4, cohérent avec Action.en_retard et
Epi.est_conforme (jamais de valeur dérivée qui peut devenir périmée en base)."""
from datetime import date

from sqlalchemy import Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import CotationPoint, StatutInspection, TypeInspection


class Inspection(BaseModel):
    __tablename__ = "inspection"

    modele: Mapped[TypeInspection] = mapped_column(enum_column(TypeInspection, "type_inspection"), nullable=False)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), nullable=False)
    # Ajouté au prompt 3.1 : FOR-SHEQ-010 précise "une même fiche est remplie
    # par équipement ou par baie/site selon le contexte" — sans ce lien, la
    # fiche équipement du prompt 3.1 ("historique complet : configurations,
    # inspections, incidents") ne pourrait jamais retrouver ses inspections.
    # Nullable : seules les inspections de type "équipements" le renseignent.
    equipement_id: Mapped[int | None] = mapped_column(ForeignKey("equipement.id"), nullable=True)
    inspecteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    # Liste de {point_checklist_id, libelle, cotation: "C"|"NC"|"SO", observation,
    # photo}. `libelle` est un instantané du référentiel au moment de
    # l'inspection : si un point est reformulé plus tard, les inspections
    # passées gardent le texte tel qu'il était réellement lu sur le terrain.
    points: Mapped[list] = mapped_column(JSON, nullable=False)
    statut: Mapped[StatutInspection] = mapped_column(
        enum_column(StatutInspection, "statut_inspection"), default=StatutInspection.EN_COURS, nullable=False
    )

    @property
    def taux_conformite(self) -> float | None:
        """Calculé (règle 6, CLAUDE.md) : conformes / (conformes + non conformes),
        les « sans objet » exclus."""
        conformes = sum(1 for p in self.points if p["cotation"] == CotationPoint.CONFORME.value)
        non_conformes = sum(1 for p in self.points if p["cotation"] == CotationPoint.NON_CONFORME.value)
        total = conformes + non_conformes
        return (conformes / total) if total else None
