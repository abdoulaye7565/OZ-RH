"""Pagination des listes (revue d'ensemble 2026-09-10).

Contexte : seul `/signalements` acceptait `limite`/`decalage`. Les volumes
réels de l'application (quelques centaines de lignes par module au plus, cf.
CDC) ne justifient pas une pagination serveur systématique côté interface —
mais une borne dure protège d'une requête qui renverrait un volume anormal,
et les paramètres restent disponibles pour les écrans qui voudront paginer.

Comportement : sans `limite`, on renvoie tout jusqu'à `PLAFOND_ABSOLU`. Avec
`limite`, on renvoie au plus `min(limite, PLAFOND_ABSOLU)` lignes à partir de
`decalage`.
"""
from dataclasses import dataclass

from fastapi import Query
from sqlalchemy import Select

PLAFOND_ABSOLU = 500


@dataclass
class Pagination:
    limite: int | None
    decalage: int

    def appliquer(self, requete: Select) -> Select:
        requete = requete.offset(max(0, self.decalage))
        effective = self.limite if self.limite is not None else PLAFOND_ABSOLU
        return requete.limit(min(max(1, effective), PLAFOND_ABSOLU))


def pagination(
    limite: int | None = Query(default=None, ge=1, description="Nombre max de lignes (défaut : tout, plafonné à 500)"),
    decalage: int = Query(default=0, ge=0, description="Nombre de lignes à sauter"),
) -> Pagination:
    return Pagination(limite=limite, decalage=decalage)
