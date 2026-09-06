"""LA RÈGLE CENTRALE du système (prompt 2.2, section 5.2.2 du CDC et règle 1 du
point 7 de CLAUDE.md) : un permis de travail en hauteur ne peut être délivré que
si quatre conditions sont réunies. Ce module ne fait QUE ça — évaluer ces
conditions — pour rester isolé, lisible et testé indépendamment de la gestion
du cycle de vie du permis (app/services/permis_service.py), qui l'appelle mais
ne réimplémente jamais la logique elle-même.

Appelée à la fois à la création ET à chaque tentative de validation d'un
permis (jamais une seule fois figée) : un permis créé conforme peut devenir
non conforme entre-temps (EPI qui expire, SLAM qui n'a pas eu lieu) — se fier à
un résultat mis en cache reviendrait à pouvoir contourner la règle en
retardant la validation. C'est ce qui rend la règle "impossible à contourner
par l'API", comme l'exige le prompt.
"""
from datetime import datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import DecisionSlam
from app.models.epi import Epi
from app.models.evaluation_slam import EvaluationSlam
from app.models.utilisateur import Utilisateur
from app.schemas.permis import ControleDetail, ControlesAutomatiquesSortie


def _epi_non_conformes_de(db: Session, intervenant_id: int) -> list[Epi]:
    epis = db.scalars(
        select(Epi).where(Epi.porteur_id == intervenant_id, Epi.archive.is_(False))
    )
    return [e for e in epis if not e.est_conforme]


def _a_un_slam_go_le_jour(db: Session, intervenant_id: int, jour: datetime) -> bool:
    debut_jour = datetime.combine(jour.date(), time.min, tzinfo=timezone.utc)
    fin_jour = datetime.combine(jour.date(), time.max, tzinfo=timezone.utc)
    derniere = db.scalar(
        select(EvaluationSlam)
        .where(
            EvaluationSlam.utilisateur_id == intervenant_id,
            EvaluationSlam.date >= debut_jour,
            EvaluationSlam.date <= fin_jour,
        )
        .order_by(EvaluationSlam.date.desc())
        .limit(1)
    )
    return derniere is not None and derniere.decision == DecisionSlam.GO


def evaluer_controles(
    db: Session,
    *,
    intervenant_ids: list[int],
    surveillant_id: int | None,
    debut_validite: datetime,
) -> ControlesAutomatiquesSortie:
    motifs: list[str] = []
    motifs_epi: list[str] = []
    motifs_slam: list[str] = []

    # (c) Aucun surveillant désigné.
    motif_surveillant_designe = None
    if surveillant_id is None:
        motif_surveillant_designe = "Aucun surveillant au sol n'est désigné"
        motifs.append(motif_surveillant_designe)

    # (d) Le surveillant figure parmi les intervenants.
    motif_surveillant_hors_intervenants = None
    if surveillant_id is not None and surveillant_id in intervenant_ids:
        motif_surveillant_hors_intervenants = "Le surveillant ne peut pas figurer parmi les intervenants"
        motifs.append(motif_surveillant_hors_intervenants)

    for intervenant_id in intervenant_ids:
        intervenant = db.get(Utilisateur, intervenant_id)
        nom = f"{intervenant.prenom} {intervenant.nom}" if intervenant else f"utilisateur {intervenant_id}"

        # (a) EPI non conforme affecté à un intervenant.
        for epi in _epi_non_conformes_de(db, intervenant_id):
            m = f"EPI {epi.numero} de {nom} non conforme (vérification dépassée ou statut {epi.statut.value})"
            motifs.append(m)
            motifs_epi.append(m)

        # (b) Pas de SLAM en GO le jour du permis.
        if not _a_un_slam_go_le_jour(db, intervenant_id, debut_validite):
            m = f"{nom} n'a pas d'évaluation SLAM en GO pour cette journée"
            motifs.append(m)
            motifs_slam.append(m)

    # Quatre lignes fixes, une par condition (a/b/c/d), pour l'écran de
    # validation responsable (prompt 2.3) : "liste des contrôles automatiques
    # avec leur résultat" suppose de voir les conditions qui PASSENT aussi,
    # pas seulement celles qui échouent (ce que `motifs` seul ne permet pas).
    details = [
        ControleDetail(
            cle="epi",
            libelle="Équipements de protection conformes",
            conforme=not motifs_epi,
            detail="; ".join(motifs_epi) or None,
        ),
        ControleDetail(
            cle="slam",
            libelle="Évaluations SLAM en GO du jour",
            conforme=not motifs_slam,
            detail="; ".join(motifs_slam) or None,
        ),
        ControleDetail(
            cle="surveillant_designe",
            libelle="Surveillant au sol désigné",
            conforme=motif_surveillant_designe is None,
            detail=motif_surveillant_designe,
        ),
        ControleDetail(
            cle="surveillant_hors_intervenants",
            libelle="Surveillant distinct des intervenants",
            conforme=motif_surveillant_hors_intervenants is None,
            detail=motif_surveillant_hors_intervenants,
        ),
    ]

    return ControlesAutomatiquesSortie(conforme=not motifs, motifs=motifs, details=details)
