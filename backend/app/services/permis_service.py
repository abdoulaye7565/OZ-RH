"""Cycle de vie du module Permis (prompt 2.2, section 5.2.2 du CDC).

Ce module gère la création et les transitions de statut ; l'évaluation des
quatre conditions de blocage vit exclusivement dans
app/services/regle_blocage_permis.py — jamais dupliquée ici."""
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.enums import StatutPermis
from app.models.permis import Permis
from app.models.utilisateur import Utilisateur
from app.schemas.permis import PermisCreation
from app.services.notification_service import notifier_permis_en_attente
from app.services.regle_blocage_permis import evaluer_controles

logger = logging.getLogger("app.permis")

_TENTATIVES_REFERENCE = 5


def _generer_reference(db: Session) -> str:
    annee = datetime.now(timezone.utc).year
    prefixe = f"{annee}-"
    dernier = db.scalar(
        select(Permis.reference).where(Permis.reference.like(f"{prefixe}%")).order_by(Permis.reference.desc()).limit(1)
    )
    prochain_numero = int(dernier.rsplit("-", 1)[-1]) + 1 if dernier else 1
    return f"{prefixe}{prochain_numero:03d}"


def creer_permis(db: Session, donnees: PermisCreation, cree_par_id: int) -> Permis:
    intervenants = list(db.scalars(select(Utilisateur).where(Utilisateur.id.in_(donnees.intervenant_ids))))
    if len(intervenants) != len(set(donnees.intervenant_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un ou plusieurs intervenants sont introuvables")

    controles = evaluer_controles(
        db,
        intervenant_ids=donnees.intervenant_ids,
        surveillant_id=donnees.surveillant_id,
        debut_validite=donnees.debut_validite,
    )

    for tentative in range(_TENTATIVES_REFERENCE):
        permis = Permis(
            reference=_generer_reference(db),
            site_id=donnees.site_id,
            nature_travaux=donnees.nature_travaux,
            support=donnees.support,
            hauteur_estimee=donnees.hauteur_estimee,
            intervenants=intervenants,
            surveillant_id=donnees.surveillant_id,
            debut_validite=donnees.debut_validite,
            fin_validite=donnees.fin_validite,
            controles=controles.model_dump(),
            statut=StatutPermis.DEMANDE if controles.conforme else StatutPermis.BLOQUE,
            cree_par_id=cree_par_id,
        )
        db.add(permis)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if tentative == _TENTATIVES_REFERENCE - 1:
                raise
            continue
        db.refresh(permis)
        break

    if permis.statut == StatutPermis.BLOQUE:
        logger.warning("Permis %s bloqué à la création : %s", permis.reference, controles.motifs)
    else:
        notifier_permis_en_attente(db, permis)
        logger.info("Permis %s créé, en attente de validation — responsable notifié", permis.reference)

    return permis


def valider(db: Session, permis: Permis, validateur_id: int) -> Permis:
    if permis.statut not in (StatutPermis.DEMANDE, StatutPermis.BLOQUE):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Impossible de valider un permis au statut « {permis.statut.value} »",
        )

    # Réévalué à neuf, jamais à partir du `controles` stocké à la création :
    # c'est cette relecture qui rend la règle impossible à contourner en
    # validant après coup un permis devenu non conforme entre-temps.
    controles = evaluer_controles(
        db,
        intervenant_ids=[u.id for u in permis.intervenants],
        surveillant_id=permis.surveillant_id,
        debut_validite=permis.debut_validite,
    )
    permis.controles = controles.model_dump()

    if not controles.conforme:
        permis.statut = StatutPermis.BLOQUE
        permis.modifie_par_id = validateur_id
        db.commit()
        db.refresh(permis)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Validation bloquée", "motifs": controles.motifs},
        )

    permis.statut = StatutPermis.DELIVRE
    permis.validateur_id = validateur_id
    permis.modifie_par_id = validateur_id
    db.commit()
    db.refresh(permis)
    logger.info("Permis %s délivré par utilisateur id=%s — intervenants à notifier", permis.reference, validateur_id)
    return permis


def refuser(db: Session, permis: Permis, motif: str, modifie_par_id: int) -> Permis:
    if permis.statut not in (StatutPermis.DEMANDE, StatutPermis.BLOQUE):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Impossible de refuser un permis au statut « {permis.statut.value} »",
        )
    permis.statut = StatutPermis.REFUSE
    controles = permis.controles or {}
    controles["motif_refus_humain"] = motif
    permis.controles = controles
    permis.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(permis)
    return permis


def cloturer(db: Session, permis: Permis, modifie_par_id: int) -> Permis:
    if permis.statut != StatutPermis.DELIVRE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Impossible de clôturer un permis au statut « {permis.statut.value} »",
        )
    permis.statut = StatutPermis.CLOTURE
    permis.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(permis)
    return permis


def generer_pdf(permis: Permis, site, surveillant, validateur) -> bytes:
    """Export PDF (chapitre 14 du CDC, cas de test 12 ; FOR-SHEQ-012 « Permis de
    travail en hauteur »)."""
    pdf = DocumentPDF("PERMIS DE TRAVAIL EN HAUTEUR", permis.reference)

    pdf.section(
        "Description des travaux",
        [
            ("Date", permis.debut_validite.strftime("%d/%m/%Y")),
            ("Validité", f"{permis.debut_validite.strftime('%H:%M')} à {permis.fin_validite.strftime('%H:%M')}"),
            ("Site", site.nom),
            ("Nature des travaux", permis.nature_travaux),
            ("Support", permis.support.value),
            ("Hauteur estimée", f"{permis.hauteur_estimee} m" if permis.hauteur_estimee else "—"),
            ("Intervenant(s)", ", ".join(f"{i.prenom} {i.nom}" for i in permis.intervenants) or "—"),
            ("Surveillant au sol", f"{surveillant.prenom} {surveillant.nom}" if surveillant else "Non désigné"),
        ],
    )

    controles = permis.controles or {}
    pdf.tableau(
        "Vérifications automatiques",
        ["Condition", "Résultat"],
        [[d.get("libelle", d.get("cle", "?")), "Conforme" if d.get("conforme") else "Non conforme"] for d in controles.get("details", [])],
    )

    pdf.section(
        "Autorisation",
        [
            ("Statut", permis.statut.value),
            ("Validé par", f"{validateur.prenom} {validateur.nom}" if validateur else "—"),
        ],
    )

    pdf.pied_de_page(
        datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
        f"{validateur.prenom} {validateur.nom}" if validateur else "—",
    )
    return pdf.construire()
