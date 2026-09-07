"""Logique métier du module Signalements (prompt 1.1, section 5.2.1 du CDC et
point 7 de CLAUDE.md)."""
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.enums import StatutSignalement, TypeSignalement
from app.models.signalement import Signalement
from app.models.utilisateur import Utilisateur
from app.services.notification_service import notifier_nouveau_signalement

# Section 5.2.1 du CDC : "Exporter un signalement au format PDF conforme au
# modèle FOR-SHEQ-001 ou 002" — FOR-SHEQ-001 (situation dangereuse/presque-
# accident/anomalie) et FOR-SHEQ-002 (incident/accident) partagent la même
# entité SIGNALEMENT ; seul le modèle (titre, intitulés) diffère selon `type`.
_TYPES_INCIDENT_ACCIDENT = (TypeSignalement.INCIDENT, TypeSignalement.ACCIDENT)

logger = logging.getLogger("app.signalements")

# Workflow strictement séquentiel (section 5.2.1) : pas de retour en arrière, pas
# de saut d'étape. NOUVEAU -> CLOTURE directement est refusé : le CDC décrit le
# workflow comme "nouveau → en analyse → actions définies → clôturé", donc un
# signalement doit être passé en analyse avant d'être clos, même sans action
# (5.2.1 permet de clôturer "avec ou sans action", pas "sans analyse").
TRANSITIONS_AUTORISEES: dict[StatutSignalement, set[StatutSignalement]] = {
    StatutSignalement.NOUVEAU: {StatutSignalement.EN_ANALYSE},
    StatutSignalement.EN_ANALYSE: {StatutSignalement.ACTIONS_DEFINIES, StatutSignalement.CLOTURE},
    StatutSignalement.ACTIONS_DEFINIES: {StatutSignalement.CLOTURE},
    StatutSignalement.CLOTURE: set(),
}

_TENTATIVES_REFERENCE = 5


def _generer_reference(db: Session) -> str:
    annee = datetime.now(timezone.utc).year
    prefixe = f"SIG-{annee}-"
    dernier = db.scalar(
        select(Signalement.reference)
        .where(Signalement.reference.like(f"{prefixe}%"))
        .order_by(Signalement.reference.desc())
        .limit(1)
    )
    prochain_numero = int(dernier.rsplit("-", 1)[-1]) + 1 if dernier else 1
    return f"{prefixe}{prochain_numero:03d}"


def creer_signalement(
    db: Session,
    *,
    type_: TypeSignalement,
    site_id: int,
    lieu: str,
    description: str,
    anonyme: bool,
    date_constat: datetime,
    photos: list[str],
    auteur: Utilisateur,
) -> Signalement:
    """`auteur` est toujours l'utilisateur authentifié qui soumet la requête — mais
    s'il choisit l'anonymat, ni `auteur_id` ni `cree_par_id` ne doivent le
    référencer, y compris dans les tables techniques (règle 3, CLAUDE.md). C'est
    ici, et nulle part ailleurs, que cette règle est appliquée : ne jamais laisser
    un appelant passer cree_par_id indépendamment de `anonyme`.
    """
    createur_id = None if anonyme else auteur.id

    # Réessai en cas de collision de référence (deux créations quasi simultanées) :
    # le volume attendu (40 à 80 signalements par an, chapitre 7.4 du CDC) rend
    # ce cas rarissime, mais la contrainte UNIQUE sur `reference` doit rester la
    # garantie ultime, pas seulement cette lecture-puis-écriture non atomique.
    for tentative in range(_TENTATIVES_REFERENCE):
        signalement = Signalement(
            reference=_generer_reference(db),
            type=type_,
            site_id=site_id,
            lieu=lieu,
            description=description,
            photos=photos or None,
            anonyme=anonyme,
            auteur_id=None if anonyme else auteur.id,
            date_constat=date_constat,
            date_saisie=datetime.now(timezone.utc),
            statut=StatutSignalement.NOUVEAU,
            cree_par_id=createur_id,
        )
        db.add(signalement)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if tentative == _TENTATIVES_REFERENCE - 1:
                raise
            continue
        db.refresh(signalement)
        break

    # Notification du référent SHEQ (tableau 3, chapitre 6.3 — prompt 4.4).
    notifier_nouveau_signalement(db, signalement)
    if signalement.anonyme:
        logger.info("Nouveau signalement anonyme %s : référent SHEQ notifié", signalement.reference)
    else:
        logger.info(
            "Nouveau signalement %s par utilisateur id=%s : référent SHEQ notifié",
            signalement.reference,
            signalement.auteur_id,
        )

    return signalement


def changer_statut(
    db: Session, signalement: Signalement, nouveau_statut: StatutSignalement, modifie_par_id: int
) -> Signalement:
    autorises = TRANSITIONS_AUTORISEES[signalement.statut]
    if nouveau_statut not in autorises:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Transition invalide : impossible de passer de « {signalement.statut.value} » "
                f"à « {nouveau_statut.value} »"
            ),
        )
    signalement.statut = nouveau_statut
    signalement.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(signalement)
    return signalement


def archiver(db: Session, signalement: Signalement, modifie_par_id: int) -> Signalement:
    signalement.archive = True
    signalement.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(signalement)
    return signalement


def generer_pdf(signalement: Signalement, site, auteur: Utilisateur | None) -> bytes:
    """Export PDF (chapitre 14 du CDC, cas de test 12 ; section 5.2.1 : "modèle
    FOR-SHEQ-001 ou 002"). `auteur` est None pour un signalement anonyme — son
    identité ne doit alors apparaître nulle part, y compris sur ce PDF (règle 3,
    CLAUDE.md), le pied de page se limite alors à la date de génération."""
    modele_incident = signalement.type in _TYPES_INCIDENT_ACCIDENT
    titre = (
        "FICHE DE DÉCLARATION D'INCIDENT / ACCIDENT" if modele_incident else "FICHE DE SIGNALEMENT D'UNE SITUATION DANGEREUSE"
    )
    pdf = DocumentPDF(titre, signalement.reference)

    pdf.section(
        "Identification",
        [
            ("Type", signalement.type.value),
            ("Date et heure du constat", signalement.date_constat.strftime("%d/%m/%Y %H:%M")),
            ("Site", site.nom),
            ("Lieu / Zone concernée", signalement.lieu),
            ("Déclarant", f"{auteur.prenom} {auteur.nom}" if auteur else "Anonyme"),
        ],
    )
    pdf.section("Description", [("Faits observés", signalement.description)])
    if signalement.causes:
        pdf.section("Analyse des causes", [("Causes identifiées", signalement.causes)])
    pdf.section("Traitement", [("Statut", signalement.statut.value)])

    pdf.pied_de_page(
        datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
        f"{auteur.prenom} {auteur.nom}" if auteur else "Anonyme",
    )
    return pdf.construire()
