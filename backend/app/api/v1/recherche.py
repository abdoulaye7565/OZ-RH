"""Recherche globale (revue d'ensemble 2026-09-10).

La maquette prévoit un champ « Rechercher partout… » dans l'en-tête desktop,
jamais implémenté. Cet endpoint interroge les entités les plus consultées
(référence, libellé) et renvoie des résultats typés avec un lien exploitable
côté interface. Volontairement simple : recherche « contient » insensible à
la casse, plafonnée par type — pas un moteur d'indexation.

Visibilité : les signalements suivent la même restriction que leur liste
(technicien / collaborateur ne voient que les leurs) ; les autres entités
sont en consultation ouverte à tout le personnel (cf. leurs routes de liste).
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.action import Action
from app.models.document import Document
from app.models.enums import RoleUtilisateur
from app.models.equipement import Equipement
from app.models.permis import Permis
from app.models.risque import Risque
from app.models.signalement import Signalement
from app.models.utilisateur import Utilisateur

router = APIRouter(prefix="/recherche", tags=["recherche"])

LIMITE_PAR_TYPE = 6
_ROLES_SIGNALEMENTS_RESTREINTS = {RoleUtilisateur.TECHNICIEN, RoleUtilisateur.COLLABORATEUR}


class ResultatRecherche(BaseModel):
    type: str  # "signalement" | "risque" | "action" | "permis" | "equipement" | "document"
    id: int
    libelle: str
    sous_libelle: str | None = None


def _like(colonne, terme: str):
    return colonne.ilike(f"%{terme}%")


@router.get("", response_model=list[ResultatRecherche])
def rechercher(
    q: str = Query(min_length=2, description="Texte recherché (2 caractères minimum)"),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> list[ResultatRecherche]:
    terme = q.strip()
    resultats: list[ResultatRecherche] = []

    # --- Signalements (visibilité restreinte pour technicien / collaborateur) ---
    req_sig = select(Signalement).where(Signalement.archive.is_(False)).where(
        or_(
            _like(Signalement.reference, terme),
            _like(Signalement.lieu, terme),
            _like(Signalement.description, terme),
        )
    )
    if utilisateur.role in _ROLES_SIGNALEMENTS_RESTREINTS:
        req_sig = req_sig.where(Signalement.auteur_id == utilisateur.id)
    for s in db.scalars(req_sig.order_by(Signalement.date_saisie.desc()).limit(LIMITE_PAR_TYPE)):
        resultats.append(
            ResultatRecherche(type="signalement", id=s.id, libelle=s.reference or s.lieu, sous_libelle=s.lieu)
        )

    # --- Risques ---
    req_risque = select(Risque).where(Risque.archive.is_(False)).where(
        or_(_like(Risque.danger, terme), _like(cast(Risque.numero, String), terme))
    )
    for r in db.scalars(req_risque.order_by(Risque.numero.desc()).limit(LIMITE_PAR_TYPE)):
        resultats.append(
            ResultatRecherche(type="risque", id=r.id, libelle=f"#{r.numero} — {r.danger}", sous_libelle=r.categorie.value)
        )

    # --- Actions ---
    req_action = select(Action).where(Action.archive.is_(False)).where(_like(Action.libelle, terme))
    for a in db.scalars(req_action.order_by(Action.echeance.asc()).limit(LIMITE_PAR_TYPE)):
        resultats.append(ResultatRecherche(type="action", id=a.id, libelle=a.libelle, sous_libelle=a.statut.value))

    # --- Permis ---
    req_permis = select(Permis).where(Permis.archive.is_(False)).where(
        or_(_like(Permis.reference, terme), _like(Permis.nature_travaux, terme))
    )
    for p in db.scalars(req_permis.order_by(Permis.debut_validite.desc()).limit(LIMITE_PAR_TYPE)):
        resultats.append(
            ResultatRecherche(type="permis", id=p.id, libelle=p.reference or p.nature_travaux, sous_libelle=p.nature_travaux)
        )

    # --- Équipements ---
    req_equip = select(Equipement).where(Equipement.archive.is_(False)).where(
        or_(
            _like(Equipement.identity, terme),
            _like(Equipement.modele, terme),
            _like(Equipement.numero_serie, terme),
        )
    )
    for e in db.scalars(req_equip.order_by(Equipement.identity.asc()).limit(LIMITE_PAR_TYPE)):
        resultats.append(
            ResultatRecherche(type="equipement", id=e.id, libelle=e.identity, sous_libelle=f"{e.marque.value} {e.modele}")
        )

    # --- Documents (uniquement ceux visibles par l'appelant) ---
    from app.services.document_service import lister_documents

    docs = [
        d
        for d in lister_documents(db, utilisateur)
        if terme.lower() in (d.reference or "").lower() or terme.lower() in (d.intitule or "").lower()
    ][:LIMITE_PAR_TYPE]
    for d in docs:
        resultats.append(
            ResultatRecherche(type="document", id=d.id, libelle=d.reference or d.intitule, sous_libelle=d.intitule)
        )

    return resultats
