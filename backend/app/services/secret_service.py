"""Logique métier du module Coffre-fort (CDC section 5.2.4).

Trois règles de gestion structurent tout ce fichier :
1. Un secret n'est jamais renvoyé en clair par autre chose que
   `consulter_secret` — jamais par la création, la modification ou la liste.
2. Toute consultation, création ou modification est journalisée
   (`JournalAcces`, écriture seule — voir app/models/journal_acces.py).
3. La visibilité d'un secret dépend de son `role_requis` comparé au rôle de
   l'appelant, pas d'une permission globale — un technicien peut consulter
   un secret dont `role_requis` est "technicien", mais jamais un secret
   réservé au responsable ; le référent SHEQ et le collaborateur n'ont
   jamais accès, quel que soit `role_requis` (règle 5.2.4 : "l'accès au
   coffre-fort n'est pas accordé par défaut au référent SHEQ, dont la
   fonction ne le justifie pas" — le collaborateur n'est même pas mentionné).
"""
import secrets
import string
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.chiffrement import InvalidToken, chiffrer, dechiffrer
from app.models.enums import ActionJournal, RoleUtilisateur
from app.models.journal_acces import JournalAcces
from app.models.secret import Secret
from app.models.utilisateur import Utilisateur
from app.schemas.secret import SecretCreation, SecretModification

# Hiérarchie propre à ce module — ne réutilise pas RoleUtilisateur.__members__
# tel quel : le référent SHEQ et le collaborateur doivent rester exclus même
# si leur ordre de déclaration dans l'énuméré changeait un jour.
NIVEAU_ROLE_SECRET: dict[RoleUtilisateur, int] = {
    RoleUtilisateur.TECHNICIEN: 1,
    RoleUtilisateur.RESPONSABLE: 2,
    RoleUtilisateur.ADMINISTRATEUR: 3,
}

DELAI_MASQUAGE_SECONDES = 15  # cohérent avec la maquette (#s-vault) — 5.2.4 : "délai paramétrable"
ALPHABET_MOT_DE_PASSE = string.ascii_letters + string.digits
ALPHABET_SYMBOLES = "!@#$%^&*()-_=+[]{}"


def peut_consulter(utilisateur: Utilisateur, secret: Secret) -> bool:
    niveau_utilisateur = NIVEAU_ROLE_SECRET.get(utilisateur.role)
    niveau_requis = NIVEAU_ROLE_SECRET.get(secret.role_requis)
    if niveau_utilisateur is None or niveau_requis is None:
        return False
    return niveau_utilisateur >= niveau_requis


def _journaliser(db: Session, secret_id: int, utilisateur_id: int, action: ActionJournal) -> None:
    db.add(
        JournalAcces(
            secret_id=secret_id,
            utilisateur_id=utilisateur_id,
            horodatage=datetime.now(timezone.utc),
            action=action,
            cree_par_id=utilisateur_id,
        )
    )


def creer_secret(db: Session, donnees: SecretCreation, cree_par_id: int) -> Secret:
    secret = Secret(
        libelle=donnees.libelle,
        equipement_id=donnees.equipement_id,
        type_acces=donnees.type_acces,
        identifiant=donnees.identifiant,
        valeur_chiffree=chiffrer(donnees.valeur),
        role_requis=donnees.role_requis,
        cree_par_id=cree_par_id,
    )
    db.add(secret)
    db.flush()
    _journaliser(db, secret.id, cree_par_id, ActionJournal.CREATION)
    db.commit()
    db.refresh(secret)
    return secret


def lister_secrets(db: Session, utilisateur: Utilisateur) -> list[Secret]:
    """Un secret dont `role_requis` dépasse le rôle de l'appelant n'apparaît
    même pas dans la liste — "restreindre la visibilité d'un secret à un
    rôle minimal" (5.2.4) porte sur l'existence même du secret, pas
    seulement sur sa valeur."""
    tous = list(db.scalars(select(Secret).where(Secret.archive.is_(False)).order_by(Secret.libelle)))
    return [s for s in tous if peut_consulter(utilisateur, s)]


def obtenir_secret_visible(db: Session, secret_id: int, utilisateur: Utilisateur) -> Secret:
    secret = db.get(Secret, secret_id)
    # 404 générique que le secret n'existe pas ou soit hors de portée du
    # rôle de l'appelant — même principe que les documents en brouillon
    # (document_service.py) : ne jamais révéler l'existence d'une ressource
    # à qui n'y a pas droit.
    if secret is None or secret.archive or not peut_consulter(utilisateur, secret):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret introuvable")
    return secret


def obtenir_secret_pour_journal(db: Session, secret_id: int, utilisateur: Utilisateur) -> Secret:
    """Même contrôle de visibilité par rôle que obtenir_secret_visible(),
    sans exclure les secrets archivés — le journal doit rester consultable
    après archivage (règle 5.2.4 / point 4 de CLAUDE.md : "le journal est en
    écriture seule... aucune route ne permet de le modifier ou de le
    supprimer, même pour un administrateur" ; l'archivage du secret ne doit
    pas non plus le rendre indirectement illisible). Revue de sécurité du
    2026-09-08 : avant cette fonction, la route journal ne vérifiait que le
    rôle global (responsable/administrateur), jamais `role_requis` du
    secret visé — un responsable pouvait lire le journal d'un secret
    réservé à l'administrateur en devinant son id, alors que sa fiche et la
    liste le lui masquaient déjà correctement."""
    secret = db.get(Secret, secret_id)
    if secret is None or not peut_consulter(utilisateur, secret):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret introuvable")
    return secret


def modifier_secret(db: Session, secret: Secret, donnees: SecretModification, modifie_par_id: int) -> Secret:
    champs = donnees.model_dump(exclude_unset=True, exclude={"valeur"})
    for champ, valeur in champs.items():
        setattr(secret, champ, valeur)
    if donnees.valeur is not None:
        secret.valeur_chiffree = chiffrer(donnees.valeur)
    secret.modifie_par_id = modifie_par_id
    db.flush()
    _journaliser(db, secret.id, modifie_par_id, ActionJournal.MODIFICATION)
    db.commit()
    db.refresh(secret)
    return secret


def archiver_secret(db: Session, secret: Secret, modifie_par_id: int) -> Secret:
    """Jamais de suppression physique (point 2, CLAUDE.md) — un secret
    archivé disparaît des écrans de consultation (`lister_secrets` filtre
    `archive.is_(False)`) mais son journal des accès reste consultable."""
    secret.archive = True
    secret.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(secret)
    return secret


def consulter_secret(db: Session, secret: Secret, utilisateur: Utilisateur) -> str:
    """Déchiffre et journalise dans le même mouvement — jamais l'un sans
    l'autre, pour qu'aucun chemin de code ne puisse renvoyer une valeur en
    clair sans laisser de trace (règle 5.2.4 : "toute consultation est
    enregistrée")."""
    try:
        valeur = dechiffrer(secret.valeur_chiffree)
    except InvalidToken as exc:
        # Valeur corrompue ou chiffrée avec une autre clé (ex. FERNET_MASTER_KEY
        # changée) : signalé clairement, jamais masqué par une valeur vide.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ce secret ne peut pas être déchiffré — contactez l'administrateur",
        ) from exc
    _journaliser(db, secret.id, utilisateur.id, ActionJournal.CONSULTATION)
    db.commit()
    return valeur


def journal_du_secret(db: Session, secret_id: int) -> list[JournalAcces]:
    requete = select(JournalAcces).where(JournalAcces.secret_id == secret_id).order_by(JournalAcces.horodatage.desc())
    return list(db.scalars(requete))


def generer_mot_de_passe(longueur: int, inclure_symboles: bool) -> str:
    """Politique paramétrable (5.2.4) : longueur et jeu de symboles réglables
    par l'appelant ; toujours au moins une lettre, un chiffre, et un symbole
    si demandé, pour éviter un mot de passe techniquement conforme mais
    dégénéré (ex. uniquement des chiffres)."""
    alphabet = ALPHABET_MOT_DE_PASSE + (ALPHABET_SYMBOLES if inclure_symboles else "")
    while True:
        candidat = "".join(secrets.choice(alphabet) for _ in range(longueur))
        a_lettre = any(c.isalpha() for c in candidat)
        a_chiffre = any(c.isdigit() for c in candidat)
        a_symbole = (not inclure_symboles) or any(c in ALPHABET_SYMBOLES for c in candidat)
        if a_lettre and a_chiffre and a_symbole:
            return candidat
