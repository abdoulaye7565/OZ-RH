"""Service d'agrégation du tableau de bord (prompt 1.5, section 5.4 du CDC).

Portée volontairement réduite à ce qui existe réellement : seuls les modules
Signalements (1.1) et Actions (1.2) ont une API à ce stade. Le CDC prévoit
quatre familles d'indicateurs (sécurité et santé, prévention, environnement et
qualité, échéances) ; la plupart dépendent de modules non construits (EPI,
inspections, formations, documents, déchets, satisfaction, coffre-fort). Plutôt
que d'inventer des valeurs, ces familles sont listées dans
`modules_non_disponibles` — voir docs/JOURNAL.md pour le détail.
"""
from datetime import datetime, timezone

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.core.pdf import DocumentPDF
from app.models.enums import StatutSignalement
from app.models.signalement import Signalement
from app.schemas.tableau_bord import Periode, SignalementParMois, SignalementsResume, TableauBordSortie
from app.services import action_service

MODULES_NON_DISPONIBLES = [
    "epi",
    "inspections",
    "formations",
    "documents",
    "environnement",
    "satisfaction",
    "coffre_fort",
]

STATUTS_A_TRAITER = (StatutSignalement.NOUVEAU, StatutSignalement.EN_ANALYSE)
NOMBRE_MAX_A_TRAITER = 10


def _conditions_signalements(date_debut: datetime | None, date_fin: datetime | None, site_id: int | None) -> list:
    conditions = [Signalement.archive.is_(False)]
    if date_debut is not None:
        conditions.append(Signalement.date_saisie >= date_debut)
    if date_fin is not None:
        conditions.append(Signalement.date_saisie <= date_fin)
    if site_id is not None:
        conditions.append(Signalement.site_id == site_id)
    return conditions


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
    echeances = action_service.echeances_proches(db, site_id=site_id)

    return TableauBordSortie(
        periode=Periode(debut=date_debut, fin=date_fin),
        site_id=site_id,
        signalements=SignalementsResume(
            total_periode=total_periode,
            par_mois=par_mois,
            nombre_a_traiter=len(a_traiter),
            a_traiter=a_traiter,
        ),
        actions=synthese_actions,
        echeances_proches=echeances,
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
        "Signalements",
        [
            ("Total sur la période", tableau.signalements.total_periode),
            ("À traiter", tableau.signalements.nombre_a_traiter),
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
    if tableau.modules_non_disponibles:
        pdf.section(
            "Modules sans indicateur disponible",
            [("Modules", ", ".join(tableau.modules_non_disponibles))],
        )

    pdf.pied_de_page(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), f"{auteur.prenom} {auteur.nom}")
    return pdf.construire()
