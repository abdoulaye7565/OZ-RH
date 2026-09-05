"""Logique métier de l'authentification, indépendante de FastAPI (testable sans
client HTTP)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hacher_mot_de_passe, verifier_mot_de_passe
from app.models.utilisateur import Utilisateur
from app.schemas.auth import UtilisateurCreation


def authentifier(db: Session, identifiant: str, mot_de_passe: str) -> Utilisateur | None:
    """Renvoie l'utilisateur si l'identifiant et le mot de passe correspondent à un
    compte actif et non archivé, sinon None. Ne distingue jamais "identifiant
    inconnu" de "mot de passe incorrect" dans sa valeur de retour, pour ne pas
    permettre l'énumération des identifiants existants."""
    utilisateur = db.scalar(select(Utilisateur).where(Utilisateur.identifiant == identifiant))
    if utilisateur is None or utilisateur.archive or not utilisateur.actif:
        return None
    if not verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe):
        return None
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
