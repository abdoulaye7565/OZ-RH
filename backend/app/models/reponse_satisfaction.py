"""Entité REPONSE_SATISFACTION — hors dictionnaire, section 5.3.6 combinée,
FOR-SHEQ-018. Immuable après création (une réponse client n'a pas vocation à
être corrigée après coup, contrairement à une configuration ou une cotation
de risque qui peuvent légitimement être réévaluées) : aucune route de
modification n'existe."""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import Recommandation


class ReponseSatisfaction(BaseModel):
    __tablename__ = "reponse_satisfaction"

    enquete_id: Mapped[int] = mapped_column(ForeignKey("enquete_satisfaction.id"), nullable=False)
    # Liste de {"critere": "...", "note": 1-5} — les 6 critères réels de
    # FOR-SHEQ-018 ne sont pas déclarés "paramétrables" par le CDC
    # (contrairement au quiz ou au référentiel de checklists) : traités comme
    # une constante Python (voir satisfaction_service.CRITERES), pas une
    # table de référence hors dictionnaire supplémentaire.
    notes: Mapped[list] = mapped_column(JSON, nullable=False)
    recommandation: Mapped[Recommandation] = mapped_column(
        enum_column(Recommandation, "recommandation"), nullable=False
    )
    remarques: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Calculé à la soumission (règle 5.3.6 : "toute note inférieure ou égale à
    # deux sur cinq déclenche...") : stocké ici (contrairement à d'autres
    # champs calculés de l'application) car c'est un fait historique de CETTE
    # réponse au moment où elle a été soumise, pas une valeur qui pourrait
    # devenir périmée par rapport à un référentiel qui évolue.
    necessite_analyse: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date_reponse: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
