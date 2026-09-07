"""Entité NOTIFICATION — hors dictionnaire (chapitre 7 : aucune entité pour ce
module), chapitre 6.3 du CDC (tableau 3, "Règles de notification").

`objet_type`/`objet_id`/`declencheur` forment ensemble la clé de
déduplication des notifications périodiques (actions, EPI, inspections,
documents) : le planificateur (app/core/scheduler.py) s'exécute chaque jour
et ne doit jamais créer deux fois la même alerte "à sept jours" pour la même
action si le job est rejoué ou si le serveur redémarre le même jour. Les
notifications immédiates (signalement, permis, NO GO, satisfaction) laissent
`declencheur` à `None` : un seul événement réel les déclenche, pas de risque
de doublon par relecture périodique."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import CanalNotification, TypeNotification


class Notification(BaseModel):
    __tablename__ = "notification"
    __table_args__ = (
        UniqueConstraint(
            "type", "objet_type", "objet_id", "destinataire_id", "declencheur",
            name="uq_notification_deduplication",
        ),
    )

    destinataire_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
    type: Mapped[TypeNotification] = mapped_column(enum_column(TypeNotification, "type_notification"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # Référence libre vers l'objet à l'origine de la notification (ex. type
    # "action", id 42) — pas une clé étrangère polymorphe stricte, cohérent
    # avec le choix déjà fait sur ACTION (risque_id/signalement_id/... séparés)
    # plutôt qu'une table de jointure générique non demandée par le CDC.
    objet_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    objet_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # "j-7", "j", "retard", "j-30" — None pour les notifications immédiates.
    declencheur: Mapped[str | None] = mapped_column(String(10), nullable=True)
    canal: Mapped[CanalNotification] = mapped_column(
        enum_column(CanalNotification, "canal_notification"), nullable=False
    )
    lue: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lue_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # None : courriel non applicable à cette notification (canal "application"
    # seul). True/False : tentative réellement effectuée, avec son résultat —
    # jamais une réussite supposée en silence (règle "ne masque pas les
    # erreurs", CLAUDE.md point 9).
    courriel_envoye: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    courriel_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)
