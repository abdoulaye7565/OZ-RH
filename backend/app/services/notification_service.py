"""Service de notifications (prompt 4.4, chapitre 6.3 du CDC, tableau 3
« Règles de notification »).

Chaque ligne du tableau devient une fonction `notifier_...` (événements
immédiats) ou une entrée du rapport `executer_taches_planifiees` (rappels
d'échéance). Aucune ligne du tableau n'est réinterprétée : le canal, le délai
et le destinataire de chaque événement sont repris tels quels — les seules
interprétations portent sur des champs que l'application ne modélise pas
(voir les commentaires ci-dessous et docs/JOURNAL.md, prompt 4.4).
"""
import logging
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.email import envoyer_courriel
from app.models.action import Action
from app.models.document import Document
from app.models.enums import (
    CanalNotification,
    RoleUtilisateur,
    StatutAction,
    StatutDocument,
    StatutEpi,
    StatutInspection,
    TypeNotification,
)
from app.models.epi import Epi
from app.models.inspection import Inspection
from app.models.notification import Notification
from app.models.permis import Permis
from app.models.utilisateur import Utilisateur
from app.services.inspection_service import PERIODICITE_JOURS

logger = logging.getLogger("app.notifications")

# Délais de la colonne "Délai" du tableau 3, en jours avant l'échéance —
# valeurs littérales du CDC, pas inventées.
DELAI_ACTION_ALERTE_JOURS = 7
DELAI_EPI_ALERTE_LOINTAINE_JOURS = 30
DELAI_EPI_ALERTE_PROCHE_JOURS = 7
DELAI_INSPECTION_ALERTE_JOURS = 7
DELAI_DOCUMENT_ALERTE_JOURS = 30


def _utilisateurs_par_role(db: Session, role: RoleUtilisateur) -> list[Utilisateur]:
    return list(db.scalars(select(Utilisateur).where(Utilisateur.role == role, Utilisateur.actif.is_(True))))


def _creer(
    db: Session,
    *,
    destinataire: Utilisateur,
    type_: TypeNotification,
    message: str,
    canal: CanalNotification,
    objet_type: str | None = None,
    objet_id: int | None = None,
    declencheur: str | None = None,
    sujet_courriel: str | None = None,
) -> Notification | None:
    """Renvoie None sans rien créer si une notification identique existe déjà
    (déduplication par la contrainte unique du modèle) — ne lève jamais
    d'erreur pour ce cas normal et attendu, notamment pour les rappels
    périodiques rejoués chaque jour par le planificateur."""
    notification = Notification(
        destinataire_id=destinataire.id,
        type=type_,
        message=message,
        objet_type=objet_type,
        objet_id=objet_id,
        declencheur=declencheur,
        canal=canal,
    )

    if canal in (CanalNotification.COURRIEL, CanalNotification.LES_DEUX):
        if destinataire.courriel:
            succes, erreur = envoyer_courriel(destinataire.courriel, sujet_courriel or message, message)
            notification.courriel_envoye = succes
            notification.courriel_erreur = erreur
        else:
            notification.courriel_envoye = False
            notification.courriel_erreur = "Aucune adresse courriel renseignée pour ce destinataire"

    db.add(notification)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Contrainte de déduplication déclenchée : cas normal et attendu pour
        # un rappel périodique déjà envoyé (le planificateur rejoue le même
        # calcul chaque jour) — pas une erreur applicative.
        return None
    db.refresh(notification)
    return notification


# ---------------------------------------------------------------------------
# Événements immédiats (tableau 3, lignes 1 à 3 et 7)
# ---------------------------------------------------------------------------


def notifier_nouveau_signalement(db: Session, signalement) -> None:
    for destinataire in _utilisateurs_par_role(db, RoleUtilisateur.REFERENT_SHEQ):
        _creer(
            db,
            destinataire=destinataire,
            type_=TypeNotification.NOUVEAU_SIGNALEMENT,
            message=f"Nouveau signalement {signalement.reference or '(hors connexion)'} : {signalement.lieu}",
            canal=CanalNotification.LES_DEUX,
            objet_type="signalement",
            objet_id=signalement.id,
            sujet_courriel="SHEQ — Nouveau signalement",
        )


def notifier_permis_en_attente(db: Session, permis: Permis) -> None:
    # "Responsable désigné" (tableau 3) : PERMIS ne modélise aucun responsable
    # assigné à l'avance (dictionnaire, 7.2.7) — diffusé à tous les
    # utilisateurs du rôle RESPONSABLE, comme les autres alertes de rôle de ce
    # tableau (EPI, documents).
    for destinataire in _utilisateurs_par_role(db, RoleUtilisateur.RESPONSABLE):
        _creer(
            db,
            destinataire=destinataire,
            type_=TypeNotification.PERMIS_EN_ATTENTE,
            message=f"Permis {permis.reference} en attente de validation",
            canal=CanalNotification.APPLICATION,
            objet_type="permis",
            objet_id=permis.id,
        )


def notifier_decision_no_go(db: Session, evaluation) -> None:
    destinataires = _utilisateurs_par_role(db, RoleUtilisateur.RESPONSABLE) + _utilisateurs_par_role(
        db, RoleUtilisateur.REFERENT_SHEQ
    )
    for destinataire in destinataires:
        _creer(
            db,
            destinataire=destinataire,
            type_=TypeNotification.DECISION_NO_GO,
            message=f"Décision NO GO enregistrée (motif : {evaluation.motif or 'non précisé'})",
            canal=CanalNotification.APPLICATION,
            objet_type="evaluation_slam",
            objet_id=evaluation.id,
        )


def notifier_satisfaction_faible(db: Session, reponse) -> None:
    destinataires = _utilisateurs_par_role(db, RoleUtilisateur.REFERENT_SHEQ) + _utilisateurs_par_role(
        db, RoleUtilisateur.RESPONSABLE
    )
    for destinataire in destinataires:
        _creer(
            db,
            destinataire=destinataire,
            type_=TypeNotification.SATISFACTION_FAIBLE,
            message="Note de satisfaction client faible (≤ 2/5) : une analyse est requise",
            canal=CanalNotification.COURRIEL,
            objet_type="reponse_satisfaction",
            objet_id=reponse.id,
            sujet_courriel="SHEQ — Note de satisfaction faible",
        )


def notifier_plafond_assistance_atteint(
    db: Session, *, annee: int, mois_numero: int, depense_usd: float, plafond_usd: float
) -> None:
    """Chapitre 16.4 du CDC : "son atteinte désactive les fonctions non
    essentielles et alerte l'administrateur". Hors tableau 3 (module IA
    postérieur, prompt 6.1) — mêmes conventions que le reste de ce service.

    `objet_id` ET `declencheur` renseignés (jamais `None`) : la contrainte
    unique du modèle porte sur les deux, et en SQL une valeur NULL n'est
    jamais égale à une autre valeur NULL, y compris dans une contrainte
    UNIQUE — laisser l'un des deux à `None` désactiverait silencieusement
    toute déduplication (une notification recréée à chaque appel, un
    courriel renvoyé à chaque fois). Trouvé en écrivant le test de
    déduplication de ce prompt, pas en le supposant correct."""
    mois_libelle = f"{annee:04d}-{mois_numero:02d}"
    for destinataire in _utilisateurs_par_role(db, RoleUtilisateur.ADMINISTRATEUR):
        _creer(
            db,
            destinataire=destinataire,
            type_=TypeNotification.PLAFOND_ASSISTANCE,
            message=(
                f"Plafond mensuel du service d'assistance atteint pour {mois_libelle} "
                f"({depense_usd:.2f} $ / {plafond_usd:.2f} $) : les fonctions non essentielles sont désactivées"
            ),
            canal=CanalNotification.LES_DEUX,
            objet_type="assistance",
            objet_id=annee * 100 + mois_numero,
            declencheur=mois_libelle,
            sujet_courriel="SHEQ — Plafond du service d'assistance atteint",
        )


# ---------------------------------------------------------------------------
# Rappels d'échéance périodiques (tableau 3, lignes 4, 5, 6, 8)
# ---------------------------------------------------------------------------


def _notifier_actions_echeance(db: Session) -> int:
    aujourdhui = date.today()
    actions = db.scalars(select(Action).where(Action.statut != StatutAction.CLOTUREE, Action.archive.is_(False)))
    nombre = 0
    for action in actions:
        jours_restants = (action.echeance - aujourdhui).days
        if jours_restants > DELAI_ACTION_ALERTE_JOURS:
            continue
        declencheur = "retard" if jours_restants < 0 else ("j" if jours_restants == 0 else "j-7")
        responsable = db.get(Utilisateur, action.responsable_id)
        if responsable is None:
            continue
        libelle = {"j-7": "à échéance dans 7 jours", "j": "échoit aujourd'hui", "retard": "en retard"}[declencheur]
        resultat = _creer(
            db,
            destinataire=responsable,
            type_=TypeNotification.ACTION_ECHEANCE,
            message=f"Action « {action.libelle} » {libelle} (échéance : {action.echeance})",
            canal=CanalNotification.LES_DEUX,
            objet_type="action",
            objet_id=action.id,
            declencheur=declencheur,
            sujet_courriel="SHEQ — Action à échéance",
        )
        if resultat is not None:
            nombre += 1
    return nombre


def _notifier_epi_verification(db: Session) -> int:
    aujourdhui = date.today()
    epis = db.scalars(
        select(Epi).where(
            Epi.archive.is_(False),
            Epi.statut.notin_((StatutEpi.RETIRE, StatutEpi.REFORME)),
            Epi.prochaine_verification.is_not(None),
        )
    )
    nombre = 0
    for epi in epis:
        jours_restants = (epi.prochaine_verification - aujourdhui).days
        if jours_restants > DELAI_EPI_ALERTE_LOINTAINE_JOURS:
            continue
        # Le suffixe de date rend le déclencheur unique à CE cycle de
        # vérification : la même ligne EPI est réutilisée indéfiniment
        # (prochaine_verification avancée de 12 mois à chaque vérification,
        # prompt 2.1) — sans ce suffixe, la contrainte de déduplication
        # bloquerait tout rappel futur après le tout premier cycle.
        etiquette = "j-7" if jours_restants <= DELAI_EPI_ALERTE_PROCHE_JOURS else "j-30"
        declencheur = f"{etiquette}-{epi.prochaine_verification.isoformat()}"
        message = f"Vérification de l'EPI {epi.numero} due le {epi.prochaine_verification}"
        destinataires = _utilisateurs_par_role(db, RoleUtilisateur.REFERENT_SHEQ)
        if epi.porteur_id is not None:
            porteur = db.get(Utilisateur, epi.porteur_id)
            if porteur is not None:
                destinataires.append(porteur)
        for destinataire in destinataires:
            resultat = _creer(
                db,
                destinataire=destinataire,
                type_=TypeNotification.EPI_VERIFICATION,
                message=message,
                canal=CanalNotification.APPLICATION,
                objet_type="epi",
                objet_id=epi.id,
                declencheur=declencheur,
            )
            if resultat is not None:
                nombre += 1
    return nombre


def _notifier_inspections_planifiees(db: Session) -> int:
    """"Inspecteur désigné" (tableau 3) : aucune affectation d'inspecteur
    n'existe pour une inspection future non encore créée (PLANIFICATION,
    section 5.3.1, n'est qu'une prévision calculée à partir de la
    périodicité) — notifié au dernier inspecteur ayant réalisé une inspection
    de ce couple (site, modèle), interprétation la plus proche du texte faute
    d'un champ d'affectation dédié. À confirmer avec le référent SHEQ."""
    aujourdhui = date.today()
    sous_requete = (
        select(
            Inspection.site_id,
            Inspection.modele,
            func.max(Inspection.id).label("dernier_id"),
        )
        .where(Inspection.statut == StatutInspection.CLOTUREE, Inspection.archive.is_(False))
        .group_by(Inspection.site_id, Inspection.modele)
        .subquery()
    )
    dernieres = db.scalars(
        select(Inspection).join(sous_requete, Inspection.id == sous_requete.c.dernier_id)
    )
    nombre = 0
    for derniere in dernieres:
        prochaine = derniere.date + timedelta(days=PERIODICITE_JOURS[derniere.modele])
        jours_restants = (prochaine - aujourdhui).days
        if jours_restants > DELAI_INSPECTION_ALERTE_JOURS:
            continue
        inspecteur = db.get(Utilisateur, derniere.inspecteur_id)
        if inspecteur is None:
            continue
        resultat = _creer(
            db,
            destinataire=inspecteur,
            type_=TypeNotification.INSPECTION_PLANIFIEE,
            message=f"Inspection « {derniere.modele.value} » prévue le {prochaine} (site {derniere.site_id})",
            canal=CanalNotification.APPLICATION,
            # Pas d'id d'inspection réel (elle n'existe pas encore, seulement
            # prévue) : le couple (site, modèle) encodé dans objet_type sert de
            # clé, avec la date prévue dans le déclencheur pour rester unique
            # à chaque nouveau cycle de périodicité.
            objet_type=f"inspection_planifiee_{derniere.modele.value}",
            objet_id=derniere.site_id,
            declencheur=f"j-7-{prochaine.isoformat()}",
        )
        if resultat is not None:
            nombre += 1
    return nombre


def _notifier_documents_a_reviser(db: Session) -> int:
    aujourdhui = date.today()
    documents = db.scalars(
        select(Document).where(Document.statut == StatutDocument.EN_VIGUEUR, Document.date_revue.is_not(None))
    )
    nombre = 0
    for document in documents:
        jours_restants = (document.date_revue - aujourdhui).days
        if jours_restants > DELAI_DOCUMENT_ALERTE_JOURS:
            continue
        for destinataire in _utilisateurs_par_role(db, RoleUtilisateur.REFERENT_SHEQ):
            resultat = _creer(
                db,
                destinataire=destinataire,
                type_=TypeNotification.DOCUMENT_REVUE,
                message=f"Document {document.reference} v{document.version} à revoir avant le {document.date_revue}",
                canal=CanalNotification.APPLICATION,
                objet_type="document",
                objet_id=document.id,
                declencheur="j-30",
            )
            if resultat is not None:
                nombre += 1
    return nombre


def executer_taches_planifiees(db: Session) -> dict:
    """Point d'entrée unique appelé par le planificateur (app/core/scheduler.py)
    et par la route de déclenchement manuel — un seul chemin de code pour les
    deux, jamais deux implémentations parallèles à maintenir."""
    return {
        "actions_notifiees": _notifier_actions_echeance(db),
        "epi_notifies": _notifier_epi_verification(db),
        "inspections_notifiees": _notifier_inspections_planifiees(db),
        "documents_notifies": _notifier_documents_a_reviser(db),
    }


# ---------------------------------------------------------------------------
# Consultation
# ---------------------------------------------------------------------------


def lister_notifications(db: Session, utilisateur_id: int, limite: int = 50) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.destinataire_id == utilisateur_id)
            .order_by(Notification.cree_le.desc())
            .limit(limite)
        )
    )


def compteur_non_lues(db: Session, utilisateur_id: int) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.destinataire_id == utilisateur_id, Notification.lue.is_(False))
    )


def obtenir_notification(db: Session, notification_id: int, utilisateur_id: int) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.destinataire_id != utilisateur_id:
        # 404 même si la notification existe mais appartient à quelqu'un
        # d'autre : ne pas révéler son existence (même principe que les
        # documents non accessibles, prompt 4.3).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification introuvable")
    return notification


def marquer_lue(db: Session, notification: Notification) -> Notification:
    if not notification.lue:
        notification.lue = True
        notification.lue_le = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification


def marquer_toutes_lues(db: Session, utilisateur_id: int) -> int:
    maintenant = datetime.now(timezone.utc)
    notifications = db.scalars(
        select(Notification).where(Notification.destinataire_id == utilisateur_id, Notification.lue.is_(False))
    )
    nombre = 0
    for notification in notifications:
        notification.lue = True
        notification.lue_le = maintenant
        nombre += 1
    db.commit()
    return nombre
