"""Entité COMPETENCE — hors dictionnaire (chapitre 7 : aucune entité Formations
n'y existe, section 5.3.3 ne donne que des exigences fonctionnelles). Référentiel
paramétrable des compétences/habilitations suivies dans la matrice, sur le même
principe que POINT_CHECKLIST (prompt 2.4) : géré par le référent SHEQ, pas une
constante Python figée dans le code."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Competence(BaseModel):
    __tablename__ = "competence"

    libelle: Mapped[str] = mapped_column(String(120), nullable=False)
    # Le CDC ne donne aucune périodicité de recyclage (contrairement à l'EPI,
    # chapitre 7.3.2 : "+12 mois" explicite) : paramétrable par compétence,
    # pas une valeur unique codée en dur.
    periodicite_mois: Mapped[int] = mapped_column(Integer, nullable=False)
