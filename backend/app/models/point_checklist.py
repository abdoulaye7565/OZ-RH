"""Entité POINT_CHECKLIST — n'appartient PAS aux 14 entités du dictionnaire
(CLAUDE.md point 5). Ajoutée délibérément au prompt 2.4 : le CDC demande des
« modèles de checklists paramétrables » (section 5.3.1, "Données gérées"), et
les 5 checklists réelles (locaux, incendie, électricité, installations,
équipements — FOR-SHEQ-005, 010, 011) totalisent 93 points répartis en
catégories. Un contenu de ce volume, destiné à être ajusté par le référent
SHEQ sans déploiement de code, ne peut pas rester une constante Python (à la
différence du référentiel SLAM, fixe et jamais qualifié de « paramétrable »
par le CDC — voir app/models/slam_referentiel.py).

Pas de suppression physique (règle transversale) : un point obsolète est
archivé (colonne `archive` héritée de BaseModel), jamais supprimé — les
inspections passées qui le référencent gardent un `point_checklist_id` valide.
"""
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import TypeInspection


class PointChecklist(BaseModel):
    __tablename__ = "point_checklist"

    type_inspection: Mapped[TypeInspection] = mapped_column(
        enum_column(TypeInspection, "type_inspection_point"), nullable=False
    )
    # Regroupement thématique ("A. STRUCTURE PORTEUSE ET FIXATIONS"...), présent
    # uniquement pour installations et équipements dans les formulaires sources.
    categorie: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    libelle: Mapped[str] = mapped_column(String(300), nullable=False)
