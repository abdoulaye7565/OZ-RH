"""Logique métier du module Audits (prompt 4.2, section 5.3.4 du CDC)."""
from collections import defaultdict
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.campagne_audit import CampagneAudit
from app.models.cotation_audit import CotationAudit
from app.models.enums import StatutInspection
from app.models.exigence_audit import ExigenceAudit
from app.schemas.audit import CampagneCreation, CotationEntree
from app.services.reference_service import obtenir_ou_generer_reference

# Seuils repris littéralement de FOR-SHEQ-017 ("Interprétation indicative :
# ≥ 80 % système mature | 50-79 % en construction | < 50 % prioriser les écarts").
SEUIL_MATURE_POURCENT = 80.0
SEUIL_EN_CONSTRUCTION_POURCENT = 50.0


def lister_exigences(db: Session) -> list[ExigenceAudit]:
    return list(
        db.scalars(select(ExigenceAudit).where(ExigenceAudit.archive.is_(False)).order_by(ExigenceAudit.numero))
    )


def creer_campagne(db: Session, donnees: CampagneCreation, auditeur_id: int) -> CampagneAudit:
    campagne = CampagneAudit(
        date=donnees.date or date.today(),
        auditeur_id=auditeur_id,
        statut=StatutInspection.EN_COURS,
        cree_par_id=auditeur_id,
    )
    db.add(campagne)
    db.commit()
    db.refresh(campagne)
    return campagne


def obtenir_campagne(db: Session, campagne_id: int) -> CampagneAudit:
    campagne = db.get(CampagneAudit, campagne_id)
    if campagne is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campagne d'audit introuvable")
    return campagne


def soumettre_cotations(
    db: Session, campagne: CampagneAudit, cotations: list[CotationEntree], modifie_par_id: int
) -> list[CotationAudit]:
    if campagne.statut == StatutInspection.CLOTUREE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette campagne est déjà clôturée")

    exigences_valides = {e.id for e in lister_exigences(db)}
    existantes = {
        c.exigence_id: c
        for c in db.scalars(select(CotationAudit).where(CotationAudit.campagne_id == campagne.id))
    }

    resultat = []
    for entree in cotations:
        if entree.exigence_id not in exigences_valides:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exigence {entree.exigence_id} introuvable ou archivée"
            )
        if entree.exigence_id in existantes:
            cotation = existantes[entree.exigence_id]
            cotation.cotation = entree.cotation
            cotation.constat = entree.constat
            cotation.ecart = entree.ecart
            cotation.modifie_par_id = modifie_par_id
        else:
            cotation = CotationAudit(
                campagne_id=campagne.id,
                exigence_id=entree.exigence_id,
                cotation=entree.cotation,
                constat=entree.constat,
                ecart=entree.ecart,
                cree_par_id=modifie_par_id,
            )
            db.add(cotation)
        resultat.append(cotation)

    db.commit()
    for c in resultat:
        db.refresh(c)
    return resultat


def cloturer_campagne(db: Session, campagne: CampagneAudit, modifie_par_id: int) -> CampagneAudit:
    if campagne.statut == StatutInspection.CLOTUREE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette campagne est déjà clôturée")
    campagne.statut = StatutInspection.CLOTUREE
    campagne.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(campagne)
    return campagne


def cotations_de_campagne(db: Session, campagne_id: int) -> list[CotationAudit]:
    return list(db.scalars(select(CotationAudit).where(CotationAudit.campagne_id == campagne_id)))


def _cotations_avec_chapitre(db: Session, campagne_id: int) -> list[tuple[CotationAudit, str]]:
    lignes = db.execute(
        select(CotationAudit, ExigenceAudit.chapitre)
        .join(ExigenceAudit, CotationAudit.exigence_id == ExigenceAudit.id)
        .where(CotationAudit.campagne_id == campagne_id)
    )
    return [(cotation, chapitre) for cotation, chapitre in lignes]


def interpretation(taux_pourcent: float) -> str:
    if taux_pourcent >= SEUIL_MATURE_POURCENT:
        return "Système mature"
    if taux_pourcent >= SEUIL_EN_CONSTRUCTION_POURCENT:
        return "En construction"
    return "Prioriser les écarts"


def calculer_score(db: Session, campagne_id: int) -> dict:
    """Formule du chapitre 7.3.2 du CDC : "somme des cotations rapportée au
    double du nombre d'exigences cotées" — le dénominateur ne compte QUE les
    exigences déjà cotées à cet instant (une campagne en cours, partiellement
    remplie, a un score cohérent), pas les 22 exigences du référentiel entier."""
    cotations_avec_chapitre = _cotations_avec_chapitre(db, campagne_id)
    score_total = sum(c.cotation for c, _ in cotations_avec_chapitre)
    score_maximal = 2 * len(cotations_avec_chapitre)
    taux = (score_total / score_maximal * 100) if score_maximal else 0.0

    par_chapitre: dict[str, list[int]] = defaultdict(list)
    for cotation, chapitre in cotations_avec_chapitre:
        par_chapitre[chapitre].append(cotation.cotation)

    score_par_chapitre = [
        {
            "chapitre": chapitre,
            "score": sum(valeurs),
            "score_maximal": 2 * len(valeurs),
            "taux_pourcent": (sum(valeurs) / (2 * len(valeurs)) * 100) if valeurs else 0.0,
        }
        for chapitre, valeurs in sorted(par_chapitre.items())
    ]

    return {
        "score_total": score_total,
        "score_maximal": score_maximal,
        "taux_conformite_pourcent": taux,
        "interpretation": interpretation(taux),
        "score_par_chapitre": score_par_chapitre,
    }


def comparer_campagnes(db: Session, campagne_reference_id: int, campagne_comparee_id: int) -> dict:
    reference = obtenir_campagne(db, campagne_reference_id)
    comparee = obtenir_campagne(db, campagne_comparee_id)

    score_reference = calculer_score(db, campagne_reference_id)
    score_compare = calculer_score(db, campagne_comparee_id)

    chapitres_par_nom_ref = {c["chapitre"]: c for c in score_reference["score_par_chapitre"]}
    chapitres_par_nom_comp = {c["chapitre"]: c for c in score_compare["score_par_chapitre"]}
    tous_chapitres = sorted(set(chapitres_par_nom_ref) | set(chapitres_par_nom_comp))

    par_chapitre = []
    for chapitre in tous_chapitres:
        taux_ref = chapitres_par_nom_ref.get(chapitre, {}).get("taux_pourcent", 0.0)
        taux_comp = chapitres_par_nom_comp.get(chapitre, {}).get("taux_pourcent", 0.0)
        par_chapitre.append(
            {
                "chapitre": chapitre,
                "taux_reference_pourcent": taux_ref,
                "taux_compare_pourcent": taux_comp,
                "evolution_points": taux_comp - taux_ref,
            }
        )

    return {
        "campagne_reference": reference,
        "campagne_comparee": comparee,
        "taux_reference_pourcent": score_reference["taux_conformite_pourcent"],
        "taux_compare_pourcent": score_compare["taux_conformite_pourcent"],
        "evolution_points": score_compare["taux_conformite_pourcent"] - score_reference["taux_conformite_pourcent"],
        "par_chapitre": par_chapitre,
    }


def generer_pdf(db: Session, campagne: CampagneAudit, auditeur) -> bytes:
    """Export PDF (chapitre 14 du CDC, cas de test 12) — reprend l'ordre de
    FOR-SHEQ-017 (« Grille d'audit interne ») : cotation 0/1/2 par exigence,
    regroupées par chapitre, puis score total et interprétation (mêmes seuils
    que le classeur réel)."""
    reference = obtenir_ou_generer_reference(db, campagne, CampagneAudit)
    score = calculer_score(db, campagne.id)
    cotations_avec_chapitre = _cotations_avec_chapitre(db, campagne.id)
    exigences = {e.id: e for e in lister_exigences(db)}

    pdf = DocumentPDF("RAPPORT D'AUDIT INTERNE DU SYSTÈME SHEQ", reference)
    pdf.section(
        "Audit",
        [("Date", campagne.date.strftime("%d/%m/%Y")), ("Auditeur", f"{auditeur.prenom} {auditeur.nom}"), ("Statut", campagne.statut.value)],
    )

    par_chapitre: dict[str, list[tuple[CotationAudit, str]]] = defaultdict(list)
    for cotation, chapitre in cotations_avec_chapitre:
        libelle = exigences[cotation.exigence_id].libelle if cotation.exigence_id in exigences else "?"
        par_chapitre[chapitre].append((cotation, libelle))

    for chapitre, lignes in sorted(par_chapitre.items()):
        pdf.tableau(
            chapitre,
            ["Exigence", "Cotation", "Constat", "Écart"],
            [
                [libelle, {0: "0 – Absent", 1: "1 – Partiel", 2: "2 – Conforme"}[c.cotation], c.constat or "—", c.ecart or "—"]
                for c, libelle in lignes
            ],
        )

    pdf.section(
        "Score de maturité",
        [
            ("Score total", f"{score['score_total']} / {score['score_maximal']}"),
            ("Taux de conformité", f"{score['taux_conformite_pourcent']:.0f} %"),
            ("Interprétation", score["interpretation"]),
        ],
    )

    pdf.pied_de_page(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), f"{auditeur.prenom} {auditeur.nom}")
    return pdf.construire()
