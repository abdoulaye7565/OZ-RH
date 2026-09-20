"""Logique métier de l'authentification, indépendante de FastAPI (testable sans
client HTTP)."""
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hacher_mot_de_passe, verifier_mot_de_passe
from app.models.enums import RoleUtilisateur
from app.models.utilisateur import Utilisateur
from app.schemas.auth import UtilisateurCreation, UtilisateurModification

logger = logging.getLogger("app.auth")

# Protection contre le brute-force sur /auth/connexion (revue de sécurité du
# 2026-09-08, CLAUDE.md point 10 : "le coffre-fort et l'authentification font
# l'objet d'une revue de sécurité dédiée avant mise en production" — jusqu'ici
# aucune limite n'existait, un mot de passe pouvait être essayé sans fin).
# Verrouillage par compte plutôt que par IP (pas de nouvelle dépendance, pas
# de nouvelle table — un champ sur UTILISATEUR suffit) : compromis assumé,
# à documenter — un tiers connaissant un identifiant réel peut délibérément
# verrouiller ce compte 15 minutes en enchaînant des mots de passe faux
# (déni de service ciblé), ce qu'un throttling par IP éviterait. Acceptable
# pour un nombre restreint de comptes nommés, internes à l'entreprise — pas
# un système à inscription publique.
LIMITE_TENTATIVES = 5
DUREE_VERROUILLAGE = timedelta(minutes=15)


def authentifier(db: Session, identifiant: str, mot_de_passe: str) -> Utilisateur | None:
    """Renvoie l'utilisateur si l'identifiant et le mot de passe correspondent à un
    compte actif, non archivé et non verrouillé, sinon None. Ne distingue jamais
    "identifiant inconnu" de "mot de passe incorrect" ou "compte verrouillé" dans
    sa valeur de retour, pour ne pas permettre l'énumération des identifiants
    existants ni confirmer l'état de verrouillage à qui ne le connaît pas déjà —
    même principe déjà appliqué au compte désactivé."""
    utilisateur = db.scalar(select(Utilisateur).where(Utilisateur.identifiant == identifiant))
    if utilisateur is None or utilisateur.archive or not utilisateur.actif:
        return None

    maintenant = datetime.now(timezone.utc)
    verrouille_jusqua = utilisateur.verrouille_jusqua
    if verrouille_jusqua is not None:
        # SQLite renvoie un datetime naïf même sur une colonne timezone=True
        # (contrairement à PostgreSQL) — déjà rencontré dans tableau_bord_service.py.
        if verrouille_jusqua.tzinfo is None:
            verrouille_jusqua = verrouille_jusqua.replace(tzinfo=timezone.utc)
        if verrouille_jusqua > maintenant:
            return None

    if not verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe):
        utilisateur.tentatives_echouees += 1
        if utilisateur.tentatives_echouees >= LIMITE_TENTATIVES:
            utilisateur.verrouille_jusqua = maintenant + DUREE_VERROUILLAGE
        db.commit()
        return None

    utilisateur.tentatives_echouees = 0
    utilisateur.verrouille_jusqua = None
    db.commit()
    return utilisateur


def creer_utilisateur(db: Session, donnees: UtilisateurCreation, cree_par: Utilisateur) -> Utilisateur:
    utilisateur = Utilisateur(
        nom=donnees.nom,
        prenom=donnees.prenom,
        identifiant=donnees.identifiant,
        mot_de_passe=hacher_mot_de_passe(donnees.mot_de_passe),
        role=donnees.role,
        site_id=donnees.site_id,
        courriel=donnees.courriel,
        cree_par_id=cree_par.id,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def modifier_utilisateur(
    db: Session, cible: Utilisateur, donnees: UtilisateurModification, modifie_par: Utilisateur
) -> Utilisateur:
    """Modifie nom/prénom/rôle/site/courriel d'un compte existant — jamais
    l'identifiant ni le mot de passe (voir UtilisateurModification). Même
    garde-fou que desactiver_utilisateur : un administrateur ne peut pas se
    retirer à lui-même son propre rôle d'administrateur, ce qui laisserait
    l'application sans personne habilité à gérer les comptes."""
    champs = donnees.model_dump(exclude_unset=True)
    if (
        "role" in champs
        and cible.id == modifie_par.id
        and cible.role == RoleUtilisateur.ADMINISTRATEUR
        and champs["role"] != RoleUtilisateur.ADMINISTRATEUR
    ):
        raise ValueError("Vous ne pouvez pas retirer votre propre rôle d'administrateur")
    for champ, valeur in champs.items():
        setattr(cible, champ, valeur)
    cible.modifie_par_id = modifie_par.id
    db.commit()
    db.refresh(cible)
    return cible


def desactiver_utilisateur(db: Session, cible: Utilisateur, modifie_par: Utilisateur) -> Utilisateur:
    """Désactive un compte (point 2, CLAUDE.md : jamais de suppression
    physique — `actif=False`, le compte et son historique restent en base).
    Un compte désactivé ne peut plus se connecter (voir `authentifier` et la
    route `/rafraichissement`) mais reste visible dans les écrans qui le
    référencent déjà (auteur d'un signalement archivé, etc.)."""
    if cible.id == modifie_par.id:
        raise ValueError("Vous ne pouvez pas désactiver votre propre compte")
    cible.actif = False
    cible.modifie_par_id = modifie_par.id
    db.commit()
    db.refresh(cible)
    return cible


def activer_utilisateur(db: Session, cible: Utilisateur, modifie_par: Utilisateur) -> Utilisateur:
    cible.actif = True
    cible.modifie_par_id = modifie_par.id
    db.commit()
    db.refresh(cible)
    return cible


def changer_photo(db: Session, utilisateur: Utilisateur, chemin: str) -> Utilisateur:
    """Remplace la photo de profil (2026-09-10, retour direct de
    l'utilisateur — "insérer sa photo"). Toujours en libre-service : chacun
    ne peut changer QUE sa propre photo (vérifié par la route, pas ici — ce
    service ne fait aucune hypothèse sur qui appelle). L'ancien fichier est
    supprimé du disque s'il existe : ce n'est pas une donnée métier tracée
    (contrairement à un signalement ou une action, règle 2 CLAUDE.md), juste
    un blob orphelin qu'il est inutile d'accumuler indéfiniment."""
    ancien = utilisateur.photo
    utilisateur.photo = chemin
    utilisateur.modifie_par_id = utilisateur.id
    db.commit()
    db.refresh(utilisateur)
    if ancien:
        _supprimer_fichier_le_cas_echeant(ancien)
    return utilisateur


def retirer_photo(db: Session, utilisateur: Utilisateur) -> Utilisateur:
    """Revient aux initiales (aucune photo) — voir changer_photo pour la
    justification de la suppression du fichier sur disque."""
    ancien = utilisateur.photo
    utilisateur.photo = None
    utilisateur.modifie_par_id = utilisateur.id
    db.commit()
    db.refresh(utilisateur)
    if ancien:
        _supprimer_fichier_le_cas_echeant(ancien)
    return utilisateur


def _supprimer_fichier_le_cas_echeant(chemin_relatif: str) -> None:
    chemin = Path(settings.storage_dir) / chemin_relatif
    try:
        chemin.unlink(missing_ok=True)
    except OSError:
        # Un fichier qu'on n'arrive pas à supprimer n'est jamais une raison de
        # faire échouer le changement de photo lui-même (règle 9, CLAUDE.md —
        # ne pas masquer une erreur, mais ne pas non plus la laisser bloquer
        # une opération sans rapport) ; il reste simplement orphelin sur disque.
        logger.warning("Impossible de supprimer l'ancienne photo de profil : %s", chemin, exc_info=True)
