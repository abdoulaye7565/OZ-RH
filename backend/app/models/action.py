"""Entité ACTION — non détaillée par le dictionnaire (chapitre 7.2), reconstituée
depuis la section 5.2.5 et le MCD. Une action est rattachée à une origine parmi
RISQUE, SIGNALEMENT ou INSPECTION (les seules entités d'origine possibles déjà
modélisées ; AUDIT n'existe pas encore — colonne à ajouter par migration au lot 4)."""
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import StatutAction, TypeMesureAction


class Action(BaseModel):
    __tablename__ = "action"
    __table_args__ = (CheckConstraint("avancement BETWEEN 0 AND 100", name="ck_action_avancement_0_100"),)

    libelle: Mapped[str] = mapped_column(String(200), nullable=False)

    # Origine — au plus une renseignée en pratique (règle de service, pas de contrainte
    # SQL stricte à ce stade : à discuter si un point de blocage émerge à l'usage).
    risque_id: Mapped[int | None] = mapped_column(ForeignKey("risque.id"), nullable=True)
    signalement_id: Mapped[int | None] = mapped_column(ForeignKey("signalement.id"), nullable=True)
    inspection_id: Mapped[int | None] = mapped_column(ForeignKey("inspection.id"), nullable=True)

    type_mesure: Mapped[TypeMesureAction] = mapped_column(
        enum_column(TypeMesureAction, "type_mesure_action"), nullable=False
    )
    responsable_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    echeance: Mapped[date] = mapped_column(Date, nullable=False)
    avancement: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    statut: Mapped[StatutAction] = mapped_column(
        enum_column(StatutAction, "statut_action"), default=StatutAction.OUVERTE, nullable=False
    )
    # Obligatoire à la clôture uniquement (règle de service, prompt 1.2) : nullable ici.
    indicateur: Mapped[str | None] = mapped_column(Text, nullable=True)
