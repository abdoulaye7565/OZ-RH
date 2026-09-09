"""Entité APPEL_ASSISTANCE — hors dictionnaire (chapitre 7 : projet antérieur au
lot 6), chapitre 16.3.1 et tableau 10 du CDC ("Le coût est maîtrisé et suivi" :
"chaque appel est journalisé avec sa fonction, son volume et son coût estimé").

Écriture seule, sur le même principe que JOURNAL_ACCES (coffre-fort, prompt 3.3
pour le service, modèle provisionné au prompt 0.2) : n'hérite volontairement pas
de BaseModel, qui porte modifie_le/modifie_par_id/archive — colonnes qui
suggéreraient à tort qu'un appel journalisé peut être modifié ou archivé après
coup. Un échec est journalisé au même titre qu'un succès (`succes=False`) :
consigner un appel raté n'est pas une erreur à masquer (CLAUDE.md, "ne masque
pas les erreurs"), c'est la donnée elle-même — le tableau de suivi (16.4)
distingue précisément succès et échecs."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AppelAssistance(Base):
    __tablename__ = "appel_assistance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    cree_par_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id", use_alter=True), nullable=True)
    organisation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Clé de fonction libre (ex. "assistant_documentaire"), pas une énumération :
    # les fonctions du lot 6 se construisent une à une (6.2, 6.3...), une
    # énumération figée obligerait une migration à chaque nouvelle fonction pour
    # une colonne qui n'a besoin d'aucune contrainte d'intégrité référentielle.
    fonction: Mapped[str] = mapped_column(String(60), nullable=False)
    utilisateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateur.id"), nullable=True)
    # Volume transmis (caractères), pas un nombre de jetons du fournisseur —
    # mesure indépendante du fournisseur choisi, disponible même sur un appel
    # en échec avant tout retour du service externe.
    volume_caracteres: Mapped[int] = mapped_column(Integer, nullable=False)
    duree_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    # Nullable : un appel en échec avant réponse du fournisseur n'a aucun coût
    # réel à estimer (ni jetons de sortie, ni parfois d'entrée facturée).
    cout_estime_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    succes: Mapped[bool] = mapped_column(Boolean, nullable=False)
    horodatage: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
