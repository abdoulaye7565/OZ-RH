"""Cycle de vie du module Inspections (prompt 2.4, section 5.3.1 du CDC)."""
import logging
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.action import Action
from app.models.enums import CotationPoint, StatutAction, StatutInspection, TypeInspection, TypeMesureAction
from app.models.inspection import Inspection
from app.models.point_checklist import PointChecklist
from app.schemas.inspection import InspectionCreation, PointInspectionEntree
from app.services.reference_service import obtenir_ou_generer_reference

logger = logging.getLogger("app.inspections")

# Le CDC ne fixe pas de délai par défaut pour les actions correctives générées
# automatiquement (règle 6, CLAUDE.md) : 30 jours choisi par cohérence avec
# l'alerte "actions à J-7" (tableau 3, chapitre 6.3 du CDC) — à confirmer avec
# le référent SHEQ.
DELAI_ACTION_CORRECTIVE_JOURS = 30

# Fréquences reprises telles quelles des formulaires papier sources (mentions
# explicites "Fréquence recommandée" / "recommandation" dans FOR-SHEQ-005,
# 010, 011) — pas inventées. Équipements varie selon la criticité dans le
# formulaire d'origine (trimestrielle/semestrielle) : trimestrielle retenue
# par défaut, à affiner si un jour la criticité est modélisée sur EQUIPEMENT.
PERIODICITE_JOURS = {
    TypeInspection.LOCAUX: 30,
    TypeInspection.INCENDIE: 30,
    TypeInspection.ELECTRICITE: 90,
    TypeInspection.INSTALLATIONS: 180,
    TypeInspection.EQUIPEMENTS: 90,
}


def _valider_points(db: Session, modele, points: list[PointInspectionEntree]) -> dict[int, PointChecklist]:
    ids = [p.point_checklist_id for p in points]
    trouves = {
        pc.id: pc
        for pc in db.scalars(select(PointChecklist).where(PointChecklist.id.in_(ids)))
    }
    manquants = set(ids) - set(trouves)
    if manquants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Points de checklist introuvables : {sorted(manquants)}",
        )
    for pc in trouves.values():
        if pc.type_inspection != modele:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le point {pc.id} n'appartient pas au modèle « {modele.value} »",
            )
        if pc.archive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le point {pc.id} est archivé, il ne peut plus être utilisé",
            )
    return trouves


def _construire_points_json(points: list[PointInspectionEntree], referentiel: dict[int, PointChecklist]) -> list[dict]:
    return [
        {
            "point_checklist_id": p.point_checklist_id,
            # Instantané du libellé au moment de l'inspection (voir
            # app/models/inspection.py) : jamais recalculé depuis le
            # référentiel après coup.
            "libelle": referentiel[p.point_checklist_id].libelle,
            "cotation": p.cotation.value,
            "observation": p.observation,
            "photo": None,
        }
        for p in points
    ]


def creer_inspection(db: Session, donnees: InspectionCreation, inspecteur_id: int) -> Inspection:
    referentiel = _valider_points(db, donnees.modele, donnees.points)
    inspection = Inspection(
        modele=donnees.modele,
        site_id=donnees.site_id,
        equipement_id=donnees.equipement_id,
        objet_inspecte=donnees.objet_inspecte,
        inspecteur_id=inspecteur_id,
        date=date.today(),
        points=_construire_points_json(donnees.points, referentiel),
        statut=StatutInspection.EN_COURS,
        cree_par_id=inspecteur_id,
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


def mettre_a_jour_points(
    db: Session, inspection: Inspection, points: list[PointInspectionEntree], modifie_par_id: int
) -> Inspection:
    if inspection.statut == StatutInspection.CLOTUREE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une inspection clôturée n'est plus modifiable",
        )
    referentiel = _valider_points(db, inspection.modele, points)
    # Les photos déjà déposées sur un point sont conservées si ce point est
    # simplement recoté, pas remplacé — sinon une correction d'observation
    # effacerait une photo déjà prise.
    photos_existantes = {p["point_checklist_id"]: p.get("photo") for p in inspection.points}
    nouveaux_points = _construire_points_json(points, referentiel)
    for p in nouveaux_points:
        p["photo"] = photos_existantes.get(p["point_checklist_id"])
    inspection.points = nouveaux_points
    inspection.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(inspection)
    return inspection


def ajouter_photo(db: Session, inspection: Inspection, point_checklist_id: int, chemin: str, modifie_par_id: int) -> Inspection:
    if inspection.statut == StatutInspection.CLOTUREE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une inspection clôturée n'est plus modifiable",
        )
    # `points` est une colonne JSON brute (pas de MutableList/MutableDict) :
    # SQLAlchemy ne détecte un changement que par comparaison de valeur à la
    # réassignation. `list(inspection.points)` ne copie que la liste
    # externe — les dictionnaires internes restent partagés avec l'objet
    # déjà suivi par la session ; les muter en place corrompt donc l'état
    # "avant" que SQLAlchemy compare à l'état "après", qui deviennent
    # identiques : aucun UPDATE n'est émis (bug réel trouvé en testant
    # l'upload de photo en conditions réelles — le point restait `photo:
    # null` malgré une réponse 200). Corrigé en reconstruisant des
    # dictionnaires neufs, sans aucune référence partagée avec l'ancienne
    # valeur.
    points = [dict(p) for p in inspection.points]
    for p in points:
        if p["point_checklist_id"] == point_checklist_id:
            p["photo"] = chemin
            break
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce point ne fait pas partie de l'inspection")
    inspection.points = points
    inspection.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(inspection)
    return inspection


def cloturer(db: Session, inspection: Inspection, modifie_par_id: int) -> tuple[Inspection, list[Action]]:
    if inspection.statut == StatutInspection.CLOTUREE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette inspection est déjà clôturée",
        )

    inspection.statut = StatutInspection.CLOTUREE
    inspection.modifie_par_id = modifie_par_id

    # Règle du prompt 2.4 : chaque point non conforme génère automatiquement
    # une action corrective, à la clôture (pas à chaque saisie intermédiaire,
    # pour ne pas dupliquer les actions si l'inspection est corrigée avant
    # d'être close).
    actions_creees: list[Action] = []
    for p in inspection.points:
        if p["cotation"] != CotationPoint.NON_CONFORME.value:
            continue
        action = Action(
            libelle=f"[{inspection.modele.value}] {p['libelle']}",
            inspection_id=inspection.id,
            type_mesure=TypeMesureAction.CORRECTIVE,
            responsable_id=inspection.inspecteur_id,
            echeance=date.today() + timedelta(days=DELAI_ACTION_CORRECTIVE_JOURS),
            avancement=0,
            statut=StatutAction.OUVERTE,
            cree_par_id=modifie_par_id,
        )
        db.add(action)
        actions_creees.append(action)

    db.commit()
    db.refresh(inspection)
    for a in actions_creees:
        db.refresh(a)

    logger.info(
        "Inspection %s (%s) clôturée : %d action(s) corrective(s) créée(s)",
        inspection.id,
        inspection.modele.value,
        len(actions_creees),
    )

    return inspection, actions_creees


def planification(db: Session, horizon_jours: int = 7) -> list[dict]:
    """Planification et alerte des inspections périodiques (prompt 2.4).

    Pour chaque couple (site, modèle) déjà inspecté au moins une fois,
    calcule l'échéance de la prochaine inspection à partir de la périodicité
    du modèle (PERIODICITE_JOURS) et signale celles dues dans `horizon_jours`
    — 7 jours par défaut, comme l'alerte "Inspection planifiée" du tableau 3
    (chapitre 6.3 du CDC). Repose sur les inspections CLÔTURÉES uniquement :
    une inspection en cours ne compte pas comme faite.
    """
    from sqlalchemy import func

    derniere_par_couple = db.execute(
        select(Inspection.site_id, Inspection.modele, func.max(Inspection.date).label("derniere"))
        .where(Inspection.statut == StatutInspection.CLOTUREE, Inspection.archive.is_(False))
        .group_by(Inspection.site_id, Inspection.modele)
    ).all()

    resultats = []
    aujourdhui = date.today()
    for site_id, modele, derniere in derniere_par_couple:
        prochaine = derniere + timedelta(days=PERIODICITE_JOURS[modele])
        jours_restants = (prochaine - aujourdhui).days
        resultats.append(
            {
                "site_id": site_id,
                "modele": modele,
                "derniere_inspection_le": derniere,
                "prochaine_prevue_le": prochaine,
                "jours_restants": jours_restants,
                "due": jours_restants <= horizon_jours,
            }
        )
    return sorted(resultats, key=lambda r: r["jours_restants"])


def generer_pdf(db: Session, inspection: Inspection, inspecteur, site) -> bytes:
    """Export PDF (chapitre 14 du CDC, cas de test 12 ; FOR-SHEQ-005/010/011
    selon le modèle)."""
    reference = obtenir_ou_generer_reference(db, inspection, Inspection)
    pdf = DocumentPDF(f"FICHE D'INSPECTION — {inspection.modele.value.upper()}", reference)

    pdf.section(
        "Inspection",
        [
            ("Date", inspection.date.strftime("%d/%m/%Y")),
            ("Site", site.nom),
            ("Inspecteur", f"{inspecteur.prenom} {inspecteur.nom}"),
            ("Statut", inspection.statut.value),
            ("Taux de conformité", f"{inspection.taux_conformite * 100:.0f} %" if inspection.taux_conformite is not None else "—"),
        ],
    )

    pdf.tableau(
        "Points contrôlés",
        ["Point", "Cotation", "Observation"],
        [
            [p["libelle"], {"C": "Conforme", "NC": "Non conforme", "SO": "Sans objet"}.get(p["cotation"], p["cotation"]), p.get("observation") or "—"]
            for p in inspection.points
        ],
    )

    pdf.pied_de_page(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), f"{inspecteur.prenom} {inspecteur.nom}")
    return pdf.construire()
