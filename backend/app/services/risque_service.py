"""Logique métier du module Risques (prompt 4.1, section 5.2.5 du CDC)."""
from datetime import date

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cotation_risque import CotationRisque
from app.models.enums import CategorieRisque, NiveauRisque
from app.models.risque import Risque
from app.schemas.risque import CotationEntree, CotationSortie, RisqueCreation, RisqueSortie

# Seuils littéraux du classeur réel (docs source, feuille "Cotation" :
# "C ≥ 15 CRITIQUE / 8 ≤ C < 15 ÉLEVÉ / 4 ≤ C < 8 MODÉRÉ / C < 4 FAIBLE"),
# identiques à ceux déjà documentés sur NiveauRisque (prompt 0.2).
SEUIL_MODERE = 4
SEUIL_ELEVE = 8
SEUIL_CRITIQUE = 15

# Le CDC énonce la règle ("revue annuelle obligatoire, rappelée automatiquement")
# sans donner de formule, à la différence d'EPI ("dernière vérification + 12
# mois", chapitre 7.3.2) : périodicité annuelle retenue par cohérence directe
# avec le mot "annuelle" du texte, pas une valeur inventée sans ancrage.
PERIODICITE_REVUE = relativedelta(years=1)


def calculer_criticite_niveau(probabilite: int, gravite: int) -> tuple[int, NiveauRisque]:
    criticite = probabilite * gravite
    if criticite >= SEUIL_CRITIQUE:
        niveau = NiveauRisque.CRITIQUE
    elif criticite >= SEUIL_ELEVE:
        niveau = NiveauRisque.ELEVE
    elif criticite >= SEUIL_MODERE:
        niveau = NiveauRisque.MODERE
    else:
        niveau = NiveauRisque.FAIBLE
    return criticite, niveau


def _prochain_numero(db: Session) -> int:
    dernier = db.scalar(select(func.max(Risque.numero)))
    return (dernier or 0) + 1


def _creer_cotation(db: Session, risque_id: int, donnees: CotationEntree, auteur_id: int) -> CotationRisque:
    criticite, niveau = calculer_criticite_niveau(donnees.probabilite, donnees.gravite)
    cotation = CotationRisque(
        risque_id=risque_id,
        mesures_existantes=donnees.mesures_existantes,
        probabilite=donnees.probabilite,
        gravite=donnees.gravite,
        criticite=criticite,
        niveau=niveau,
        mesures_proposees=donnees.mesures_proposees,
        date_evaluation=donnees.date_evaluation or date.today(),
        auteur_id=auteur_id,
        cree_par_id=auteur_id,
    )
    db.add(cotation)
    return cotation


def creer_risque(db: Session, donnees: RisqueCreation, auteur_id: int) -> Risque:
    risque = Risque(
        numero=_prochain_numero(db),
        danger=donnees.danger,
        categorie=donnees.categorie,
        unite_travail=donnees.unite_travail,
        personnes_exposees=donnees.personnes_exposees,
        cree_par_id=auteur_id,
    )
    db.add(risque)
    db.flush()  # obtient risque.id avant de créer la cotation liée
    _creer_cotation(db, risque.id, donnees.cotation, auteur_id)
    db.commit()
    db.refresh(risque)
    return risque


def reevaluer(db: Session, risque: Risque, donnees: CotationEntree, auteur_id: int) -> CotationRisque:
    """Ne modifie jamais `risque` lui-même : une réévaluation ajoute une ligne à
    l'historique, elle ne remplace rien (règle explicite, section 5.2.5)."""
    cotation = _creer_cotation(db, risque.id, donnees, auteur_id)
    db.commit()
    db.refresh(cotation)
    return cotation


def modifier_risque(db: Session, risque: Risque, donnees, modifie_par_id: int) -> Risque:
    """Corrige les champs descriptifs (danger, catégorie, unité, personnes
    exposées). Ne touche pas aux cotations. Revue d'ensemble 2026-09-10."""
    for champ, valeur in donnees.model_dump(exclude_unset=True).items():
        setattr(risque, champ, valeur)
    risque.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(risque)
    return risque


def cotations_de(db: Session, risque_id: int) -> list[CotationRisque]:
    return list(
        db.scalars(
            select(CotationRisque)
            .where(CotationRisque.risque_id == risque_id)
            .order_by(CotationRisque.date_evaluation.desc(), CotationRisque.id.desc())
        )
    )


def dernieres_cotations(db: Session, risque_ids: list[int] | None = None) -> dict[int, CotationRisque]:
    """Une cotation par risque : la plus récente par (date_evaluation, id) — id en
    départage puisque l'application ne permet pas de saisir deux cotations pour
    la même date dans un ordre différent de leur création réelle."""
    sous_requete = (
        select(CotationRisque.risque_id, func.max(CotationRisque.id).label("dernier_id"))
        .group_by(CotationRisque.risque_id)
    )
    if risque_ids is not None:
        sous_requete = sous_requete.where(CotationRisque.risque_id.in_(risque_ids))
    sous_requete = sous_requete.subquery()

    lignes = db.scalars(
        select(CotationRisque).join(sous_requete, CotationRisque.id == sous_requete.c.dernier_id)
    )
    return {c.risque_id: c for c in lignes}


def lister_risques(
    db: Session,
    niveau: NiveauRisque | None = None,
    categorie: CategorieRisque | None = None,
    unite_travail: str | None = None,
) -> list[tuple[Risque, CotationRisque | None]]:
    requete = select(Risque).where(Risque.archive.is_(False))
    if categorie is not None:
        requete = requete.where(Risque.categorie == categorie)
    if unite_travail:
        requete = requete.where(Risque.unite_travail.ilike(f"%{unite_travail.strip()}%"))
    risques = list(db.scalars(requete.order_by(Risque.numero)))
    cotations = dernieres_cotations(db, [r.id for r in risques])
    resultat = [(r, cotations.get(r.id)) for r in risques]
    if niveau is not None:
        resultat = [(r, c) for r, c in resultat if c is not None and c.niveau == niveau]
    return resultat


def vers_sortie(risque: Risque, cotation: CotationRisque | None) -> RisqueSortie:
    """Conversion explicite plutôt qu'une simple `RisqueSortie.model_validate`,
    car `derniere_cotation` n'existe pas comme attribut sur le modèle ORM
    `Risque` (elle exige une requête séparée, voir `dernieres_cotations`) — sans
    cette étape, le champ resterait toujours à `None` par défaut."""
    sortie = RisqueSortie.model_validate(risque)
    sortie.derniere_cotation = CotationSortie.model_validate(cotation) if cotation else None
    return sortie


def obtenir_risque(db: Session, risque_id: int) -> Risque:
    risque = db.get(Risque, risque_id)
    if risque is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risque introuvable")
    return risque


def matrice_criticite(db: Session) -> list[dict]:
    """Grille 5x5 complète (probabilité × gravité) — section 5.2.5 : "Visualiser
    la matrice de criticité avec positionnement des risques". Une cellule peut
    être vide (aucun risque actuellement coté à cette combinaison)."""
    risques = list(db.scalars(select(Risque).where(Risque.archive.is_(False))))
    cotations = dernieres_cotations(db, [r.id for r in risques])
    risques_par_case: dict[tuple[int, int], list[Risque]] = {}
    for risque in risques:
        cotation = cotations.get(risque.id)
        if cotation is None:
            continue
        risques_par_case.setdefault((cotation.probabilite, cotation.gravite), []).append(risque)

    grille = []
    for probabilite in range(1, 6):
        for gravite in range(1, 6):
            criticite, niveau = calculer_criticite_niveau(probabilite, gravite)
            risques_case = risques_par_case.get((probabilite, gravite), [])
            grille.append(
                {
                    "probabilite": probabilite,
                    "gravite": gravite,
                    "criticite": criticite,
                    "niveau": niveau,
                    "risques": [vers_sortie(r, cotations[r.id]) for r in risques_case],
                }
            )
    return grille


def revues_dues(db: Session, horizon_jours: int = 60) -> list[dict]:
    """Rappel de la revue annuelle (section 5.2.5). Périodicité : voir
    PERIODICITE_REVUE. Basé sur la date de la dernière cotation, quelle qu'elle
    soit — une réévaluation reporte donc naturellement la prochaine échéance."""
    risques = list(db.scalars(select(Risque).where(Risque.archive.is_(False))))
    cotations = dernieres_cotations(db, [r.id for r in risques])
    aujourdhui = date.today()
    resultats = []
    for risque in risques:
        cotation = cotations.get(risque.id)
        if cotation is None:
            continue
        prochaine = cotation.date_evaluation + PERIODICITE_REVUE
        jours_restants = (prochaine - aujourdhui).days
        resultats.append(
            {
                "risque_id": risque.id,
                "numero": risque.numero,
                "danger": risque.danger,
                "derniere_evaluation_le": cotation.date_evaluation,
                "prochaine_revue_le": prochaine,
                "jours_restants": jours_restants,
                "due": jours_restants <= horizon_jours,
            }
        )
    return sorted(resultats, key=lambda r: r["jours_restants"])
