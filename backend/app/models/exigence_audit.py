"""Entité EXIGENCE_AUDIT — hors dictionnaire (chapitre 7 : aucune entité Audit,
aucune liste des « 22 exigences » citées par le prompt 4.2). Référentiel repris
tel quel de FOR-SHEQ-017 « Grille d'audit interne du système SHEQ (base ISO
45001 simplifiée) », classée non confidentielle (contrairement aux fiches de
configuration) — son contenu (22 exigences réelles, réparties en 6 chapitres)
vit dans app/models/audit_referentiel.py, semé par migration de données, même
principe que checklist_referentiel.py (prompt 2.4)."""
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class ExigenceAudit(BaseModel):
    __tablename__ = "exigence_audit"

    numero: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    chapitre: Mapped[str] = mapped_column(String(60), nullable=False)
    libelle: Mapped[str] = mapped_column(Text, nullable=False)
