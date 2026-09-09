"""Entité SEGMENT_DOCUMENT — hors dictionnaire (chapitre 7 : projet antérieur
au lot 6), chapitre 16.3.2 du CDC : "Les documents en vigueur sont découpés en
segments et indexés lors de leur approbation" / "les segments issus d'une
version archivée sont retirés".

Contrairement à APPEL_ASSISTANCE (écriture seule), une ligne SEGMENT_DOCUMENT
est bien supprimée — pas modifiée, pas archivée, réellement retirée — quand sa
version de document devient ARCHIVE : c'est la donnée elle-même que le CDC
demande de retirer du corpus, pas une trace de son existence passée. N'hérite
pas de BaseModel pour la même raison que JOURNAL_ACCES/APPEL_ASSISTANCE :
aucune des colonnes modifie_le/modifie_par_id/archive n'a de sens ici — un
segment n'est jamais modifié en place, une nouvelle version du document
produit un nouveau jeu de segments entièrement recalculé."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SegmentDocument(Base):
    __tablename__ = "segment_document"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False)
    # Étiquette lisible d'origine (titre de section pour un .docx, "Page 3"
    # pour un PDF, nom de feuille pour un .xlsx) — restituée dans les
    # références de la réponse générée (16.3.2 : "la réponse restitue les
    # références des segments utilisés").
    section: Mapped[str] = mapped_column(Text, nullable=False)
    texte: Mapped[str] = mapped_column(Text, nullable=False)
    # Liste de flottants (JSON plutôt qu'un type vectoriel dédié : aucune
    # extension vectorielle SQLite/PostgreSQL déployée par ce projet, et la
    # volumétrie réelle — 36 documents — ne le justifie pas ; la similarité
    # cosinus se calcule en Python à la volée, voir
    # app/services/assistance/recherche_documentaire.py).
    embedding: Mapped[list] = mapped_column(JSON, nullable=False)
    # Ordre d'origine dans le document (pas un tri alphabétique de `section`) :
    # restitue les segments dans un ordre lisible si plusieurs proviennent du
    # même document.
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
