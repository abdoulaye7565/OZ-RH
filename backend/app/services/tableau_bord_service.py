"""Service d'agrégation du tableau de bord (prompt 1.5, section 5.4 du CDC).

Étendu le 2026-09-08 : au prompt 1.5, seuls Signalements et Actions avaient
une API — les quatre familles d'indicateurs de la section 5.4 (sécurité et
santé, prévention, environnement et qualité, échéances) ne pouvaient pas
toutes être calculées, et étaient listées dans `modules_non_disponibles`
plutôt que simulées. EPI, Inspections, Formations, Documents et Satisfaction
existent désormais (chantier du 2026-09-07) : chacun alimente ici un
indicateur réel, calculé sur les mêmes données que son propre écran — jamais
une valeur recalculée séparément qui pourrait diverger. Seuls les incidents
environnementaux et la sécurité des données (coffre-fort, toujours bloqué)
restent sans module source.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.document import Document
from app.models.enums import (
    StatutDocument,
    StatutInspection,
    StatutSeance,
    StatutSignalement,
    TypeSignalement,
)
from app.models.epi import Epi
from app.models.habilitation import Habilitation
from app.models.inspection import Inspection
from app.models.reponse_satisfaction import ReponseSatisfaction
from app.models.seance import Seance
from app.models.signalement import Signalement
from app.models.utilisateur import Utilisateur
from app.schemas.tableau_bord import (
    DocumentsResume,
    EcheanceSortie,
    EpiResume,
    FormationsResume,
    InspectionsResume,
    Periode,
    SatisfactionResume,
    SecuriteResume,
    SignalementParMois,
    SignalementsResume,
    TableauBordSortie,
)
from app.services import action_service, document_service, epi_service

MODULES_NON_DISPONIBLES = [
    "incidents_environnementaux",
    "coffre_fort",
]

STATUTS_A_TRAITER = (StatutSignalement.NOUVEAU, StatutSignalement.EN_ANALYSE)
NOMBRE_MAX_A_TRAITER = 10
HORIZON_ECHEANCES_JOURS = 30
NOMBRE_MAX_ECHEANCES = 10
SEUIL_NOTE_RECLAMATION = 2


def _conditions_signalements(date_debut: datetime | None, date_fin: datetime | None, site_id: int | None) -> list:
    conditions = [Signalement.archive.is_(False)]
    if date_debut is not None:
        conditions.append(Signalement.date_saisie >= date_debut)
    if date_fin is not None:
        conditions.append(Signalement.date_saisie <= date_fin)
    if site_id is not None:
        conditions.append(Signalement.site_id == site_id)
    return conditions


def _securite(db: Session, conditions: list) -> SecuriteResume:
    accidents_periode = db.scalar(
        select(func.count()).select_from(Signalement).where(*conditions, Signalement.type == TypeSignalement.ACCIDENT)
    )
    presque_accidents_periode = db.scalar(
        select(func.count())
        .select_from(Signalement)
        .where(*conditions, Signalement.type == TypeSignalement.PRESQUE_ACCIDENT)
    )
    dernier_accident = db.scalar(
        select(func.max(Signalement.date_constat)).where(
            Signalement.archive.is_(False), Signalement.type == TypeSignalement.ACCIDENT
        )
    )
    # SQLite renvoie un datetime naïf même pour une colonne DateTime(timezone=True)
    # (contrairement à PostgreSQL) : toutes les dates de l'application sont
    # stockées en UTC (datetime.now(timezone.utc) partout à l'écriture), donc
    # naïve ici signifie UTC, jamais l'heure locale du serveur.
    if dernier_accident is not None and dernier_accident.tzinfo is None:
        dernier_accident = dernier_accident.replace(tzinfo=timezone.utc)
    jours_sans_accident = (datetime.now(timezone.utc) - dernier_accident).days if dernier_accident else None
    return SecuriteResume(
        accidents_periode=accidents_periode,
        presque_accidents_periode=presque_accidents_periode,
        jours_sans_accident=jours_sans_accident,
    )


def _inspections(db: Session, date_debut: datetime | None, date_fin: datetime | None) -> InspectionsResume:
    conditions = [Inspection.archive.is_(False), Inspection.statut == StatutInspection.CLOTUREE]
    if date_debut is not None:
        conditions.append(Inspection.date >= date_debut.date())
    if date_fin is not None:
        conditions.append(Inspection.date <= date_fin.date())
    inspections = list(db.scalars(select(Inspection).where(*conditions)))
    taux = [i.taux_conformite for i in inspections if i.taux_conformite is not None]
    return InspectionsResume(
        realisees_periode=len(inspections),
        taux_conformite_moyen=(sum(taux) / len(taux)) if taux else None,
    )


def _epi(db: Session) -> EpiResume:
    dues = epi_service.verifications_dues(db, horizon_jours=HORIZON_ECHEANCES_JOURS)
    aujourdhui = date.today()
    depassees = sum(1 for e in dues if e.prochaine_verification < aujourdhui)
    return EpiResume(a_verifier_bientot=len(dues) - depassees, verifications_depassees=depassees)


def _formations(db: Session) -> FormationsResume:
    seances_a_venir = db.scalar(
        select(func.count())
        .select_from(Seance)
        .where(Seance.archive.is_(False), Seance.statut == StatutSeance.PLANIFIEE, Seance.date >= date.today())
    )
    aujourdhui = date.today()
    personnel_forme = db.scalar(
        select(func.count(func.distinct(Habilitation.utilisateur_id))).where(Habilitation.date_expiration >= aujourdhui)
    )
    personnel_total = db.scalar(
        select(func.count())
        .select_from(Utilisateur)
        .where(Utilisateur.archive.is_(False), Utilisateur.actif.is_(True))
    )
    return FormationsResume(seances_a_venir=seances_a_venir, personnel_forme=personnel_forme, personnel_total=personnel_total)


def _documents(db: Session) -> DocumentsResume:
    a_reviser = document_service.alertes_revue(db, horizon_jours=HORIZON_ECHEANCES_JOURS)
    en_attente = db.scalar(
        select(func.count())
        .select_from(Document)
        .where(Document.archive.is_(False), Document.statut == StatutDocument.EN_APPROBATION)
    )
    return DocumentsResume(a_reviser_bientot=len(a_reviser), en_attente_approbation=en_attente)


def _satisfaction(db: Session, date_debut: datetime | None, date_fin: datetime | None) -> SatisfactionResume:
    conditions = [ReponseSatisfaction.necessite_analyse.is_(True)]
    if date_debut is not None:
        conditions.append(ReponseSatisfaction.date_reponse >= date_debut)
    if date_fin is not None:
        conditions.append(ReponseSatisfaction.date_reponse <= date_fin)
    reclamations = db.scalar(select(func.count()).select_from(ReponseSatisfaction).where(*conditions))

    toutes = list(db.scalars(select(ReponseSatisfaction)))
    notes = [n["note"] for r in toutes for n in r.notes]
    note_moyenne = (sum(notes) / len(notes)) if notes else None
    return SatisfactionResume(reclamations_periode=reclamations, note_moyenne=note_moyenne)


def _echeances_proches(db: Session, site_id: int | None) -> list[EcheanceSortie]:
    """Fusionne quatre sources en une seule liste triée par proximité,
    comme le montre la maquette (#p-dash, "Échéances proches") — la
    maquette mélange EPI, formation et document, pas seulement des actions."""
    resultats: list[EcheanceSortie] = []

    for a in action_service.echeances_proches(db, horizon_jours=HORIZON_ECHEANCES_JOURS, site_id=site_id, limite=NOMBRE_MAX_ECHEANCES):
        resultats.append(EcheanceSortie(type="action", reference=None, libelle=a.libelle, echeance=a.echeance))

    for e in epi_service.verifications_dues(db, horizon_jours=HORIZON_ECHEANCES_JOURS):
        resultats.append(
            EcheanceSortie(type="epi", reference=e.numero, libelle=f"{e.numero} — vérification EPI", echeance=e.prochaine_verification)
        )

    for d in document_service.alertes_revue(db, horizon_jours=HORIZON_ECHEANCES_JOURS):
        resultats.append(
            EcheanceSortie(
                type="document", reference=d["reference"], libelle=f"{d['reference']} — revue documentaire", echeance=d["date_revue"]
            )
        )

    seances = db.scalars(
        select(Seance).where(
            Seance.archive.is_(False),
            Seance.statut == StatutSeance.PLANIFIEE,
            Seance.date >= date.today(),
            Seance.date <= date.today() + timedelta(days=HORIZON_ECHEANCES_JOURS),
        )
    )
    for s in seances:
        resultats.append(EcheanceSortie(type="formation", reference=None, libelle=f"Sensibilisation — {s.theme}", echeance=s.date))

    resultats.sort(key=lambda e: e.echeance)
    return resultats[:NOMBRE_MAX_ECHEANCES]


def construire_tableau_de_bord(
    db: Session,
    *,
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    site_id: int | None = None,
) -> TableauBordSortie:
    conditions = _conditions_signalements(date_debut, date_fin, site_id)

    total_periode = db.scalar(select(func.count()).select_from(Signalement).where(*conditions))

    # Histogramme mensuel en une seule requête agrégée (GROUP BY année/mois).
    # extract() plutôt que strftime() (SQLite) ou date_trunc() (PostgreSQL),
    # spécifiques chacun à un seul des deux moteurs — extract() est traduit
    # correctement par SQLAlchemy vers les deux dialectes.
    requete_mois = (
        select(
            extract("year", Signalement.date_saisie).label("annee"),
            extract("month", Signalement.date_saisie).label("mois"),
            func.count().label("nombre"),
        )
        .where(*conditions)
        .group_by(extract("year", Signalement.date_saisie), extract("month", Signalement.date_saisie))
        .order_by(extract("year", Signalement.date_saisie), extract("month", Signalement.date_saisie))
    )
    par_mois = [
        SignalementParMois(annee=int(annee), mois=int(mois), nombre=nombre)
        for annee, mois, nombre in db.execute(requete_mois)
    ]

    # Liste "à traiter" : une seule requête, pas une par signalement (N+1 évité).
    requete_a_traiter = (
        select(Signalement)
        .where(*conditions, Signalement.statut.in_(STATUTS_A_TRAITER))
        .order_by(Signalement.date_saisie.desc())
        .limit(NOMBRE_MAX_A_TRAITER)
    )
    a_traiter = list(db.scalars(requete_a_traiter))

    synthese_actions = action_service.calculer_synthese(db, site_id=site_id)

    return TableauBordSortie(
        periode=Periode(debut=date_debut, fin=date_fin),
        site_id=site_id,
        signalements=SignalementsResume(
            total_periode=total_periode,
            par_mois=par_mois,
            nombre_a_traiter=len(a_traiter),
            a_traiter=a_traiter,
        ),
        securite=_securite(db, conditions),
        actions=synthese_actions,
        inspections=_inspections(db, date_debut, date_fin),
        epi=_epi(db),
        formations=_formations(db),
        documents=_documents(db),
        satisfaction=_satisfaction(db, date_debut, date_fin),
        echeances_proches=_echeances_proches(db, site_id),
        modules_non_disponibles=MODULES_NON_DISPONIBLES,
    )


def generer_pdf(tableau: TableauBordSortie, auteur) -> bytes:
    """Export PDF (chapitre 14 du CDC, cas de test 12). Le tableau de bord n'est
    pas un enregistrement individuel comme les huit autres modules exportés
    (prompt 5.1) mais un instantané calculé : pas de référence ENR-SHEQ (rien
    à numéroter — aucune ligne de base ne correspond à "ce tableau de bord"),
    seuls la date de génération et l'auteur de la demande sont portés, comme
    l'exige la traçabilité (règle 3, CLAUDE.md)."""
    pdf = DocumentPDF("TABLEAU DE BORD SHEQ")

    pdf.section(
        "Période",
        [
            ("Du", tableau.periode.debut.strftime("%d/%m/%Y") if tableau.periode.debut else "—"),
            ("Au", tableau.periode.fin.strftime("%d/%m/%Y") if tableau.periode.fin else "—"),
        ],
    )
    pdf.section(
        "Sécurité et santé",
        [
            ("Accidents (période)", tableau.securite.accidents_periode),
            ("Presque-accidents (période)", tableau.securite.presque_accidents_periode),
            ("Jours sans accident", tableau.securite.jours_sans_accident if tableau.securite.jours_sans_accident is not None else "—"),
            ("Signalements (période)", tableau.signalements.total_periode),
            ("À traiter", tableau.signalements.nombre_a_traiter),
        ],
    )
    pdf.section(
        "Prévention",
        [
            ("Inspections réalisées (période)", tableau.inspections.realisees_periode),
            (
                "Taux de conformité moyen",
                f"{tableau.inspections.taux_conformite_moyen * 100:.0f} %" if tableau.inspections.taux_conformite_moyen is not None else "—",
            ),
            ("Séances de sensibilisation à venir", tableau.formations.seances_a_venir),
            ("Personnel formé", f"{tableau.formations.personnel_forme} / {tableau.formations.personnel_total}"),
        ],
    )
    pdf.section(
        "Actions",
        [
            ("Ouvertes", tableau.actions.par_statut.get("ouverte", 0)),
            ("En cours", tableau.actions.par_statut.get("en_cours", 0)),
            ("Clôturées", tableau.actions.par_statut.get("cloturee", 0)),
            ("En retard", tableau.actions.nombre_en_retard),
            ("Taux d'avancement global", f"{tableau.actions.taux_avancement_global * 100:.0f} %"),
        ],
    )
    pdf.section(
        "Échéances",
        [
            ("EPI à vérifier bientôt", tableau.epi.a_verifier_bientot),
            ("EPI en retard de vérification", tableau.epi.verifications_depassees),
            ("Documents à réviser bientôt", tableau.documents.a_reviser_bientot),
            ("Documents en attente d'approbation", tableau.documents.en_attente_approbation),
        ],
    )
    if tableau.satisfaction.reclamations_periode or tableau.satisfaction.note_moyenne is not None:
        pdf.section(
            "Satisfaction client",
            [
                ("Réclamations (note ≤ 2, période)", tableau.satisfaction.reclamations_periode),
                (
                    "Note moyenne",
                    f"{tableau.satisfaction.note_moyenne:.1f} / 5" if tableau.satisfaction.note_moyenne is not None else "—",
                ),
            ],
        )
    if tableau.modules_non_disponibles:
        pdf.section(
            "Indicateurs sans module source",
            [("Modules", ", ".join(tableau.modules_non_disponibles))],
        )

    pdf.pied_de_page(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), f"{auteur.prenom} {auteur.nom}")
    return pdf.construire()
