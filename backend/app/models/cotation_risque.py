"""Entité COTATION_RISQUE — hors dictionnaire (chapitre 7), ajoutée au prompt 4.1
pour porter l'historique des réévaluations d'un risque (voir app/models/risque.py
pour la justification complète). Immuable après création : même principe que
CONFIGURATION (règle 5, CLAUDE.md) — une réévaluation crée une nouvelle ligne, la
précédente reste consultable telle quelle. Aucune route de modification/suppression
n'existe pour cette entité."""
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, enum_column
from app.models.enums import NiveauRisque


class CotationRisque(BaseModel):
    __tablename__ = "cotation_risque"
    __table_args__ = (
        # Nom bref : la convention de nommage (app/db/base.py) préfixe déjà
        # "ck_cotation_risque_" automatiquement — un nom déjà préfixé ici
        # produirait un doublon (bug préexistant sur RISQUE depuis le prompt
        # 0.2, non corrigé ici pour ne pas toucher une migration déjà appliquée
        # ailleurs, mais pas reproduit sur cette nouvelle table).
        CheckConstraint("probabilite BETWEEN 1 AND 5", name="probabilite_1_5"),
        CheckConstraint("gravite BETWEEN 1 AND 5", name="gravite_1_5"),
    )

    risque_id: Mapped[int] = mapped_column(ForeignKey("risque.id"), nullable=False)
    mesures_existantes: Mapped[str | None] = mapped_column(Text, nullable=True)
    probabilite: Mapped[int] = mapped_column(Integer, nullable=False)
    gravite: Mapped[int] = mapped_column(Integer, nullable=False)
    # Calculés (règle 6, CLAUDE.md) : renseignés par le service métier à l'écriture,
    # jamais recalculés en base — cohérent avec Epi.est_conforme, Inspection.taux_conformite.
    criticite: Mapped[int] = mapped_column(Integer, nullable=False)
    niveau: Mapped[NiveauRisque] = mapped_column(enum_column(NiveauRisque, "niveau_risque"), nullable=False)
    # Obligatoire (dictionnaire 7.2.2) pour TOUTE cotation, quelle que soit la
    # gravité : la règle de gestion 5.2.5 ("tout risque de gravité 4 ou 5 doit
    # comporter au moins une mesure de maîtrise, quelle que soit sa criticité")
    # est donc déjà couverte structurellement — aucune dérogation n'existe pour
    # les gravités 1 à 3 qui permettrait de la contourner par un autre chemin.
    mesures_proposees: Mapped[str] = mapped_column(Text, nullable=False)
    date_evaluation: Mapped[date] = mapped_column(Date, nullable=False)
    auteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"), nullable=False)
