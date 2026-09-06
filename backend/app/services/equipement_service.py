"""Logique métier du module Parc d'équipements (prompt 3.1, section 5.2.3 du CDC)."""
import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.configuration import Configuration
from app.models.enums import MarqueEquipement, TypeSignalement
from app.models.equipement import Equipement
from app.models.inspection import Inspection
from app.models.signalement import Signalement
from app.schemas.equipement import EquipementCreation, EquipementMiseAJour

# Chapitre 7.3.1 du CDC ("Tableau 5 : Règles de nommage") : forme SITE-FONCTION-NN,
# "saisi par le technicien, unicité contrôlée" — aucun vocabulaire de FONCTION n'est
# énuméré ailleurs dans le CDC (à la différence du préfixe EPI, chapitre 7.3.1 aussi,
# qui donne des lettres précises). Traité comme une forme structurelle libre plutôt
# qu'une liste fermée : deux segments alphanumériques puis un numéro à 2 chiffres,
# normalisé en majuscules à la saisie. À confirmer avec le référent SHEQ si un
# vocabulaire de FONCTION doit finalement être imposé.
_FORMAT_IDENTITY = re.compile(r"^[A-Z0-9]{2,10}-[A-Z0-9]{2,10}-\d{2}$")

# Signalements considérés comme "incidents associés" à un équipement dans la fiche
# du prompt 3.1 : le dictionnaire ne modélise pas de lien SIGNALEMENT → EQUIPEMENT
# (seul un lien vers SITE existe) — voir la limite documentée dans docs/JOURNAL.md.
_TYPES_INCIDENT = (TypeSignalement.INCIDENT, TypeSignalement.ACCIDENT)

_TENTATIVES_UNICITE = 3


def valider_format_identity(identity: str) -> str:
    normalise = identity.strip().upper()
    if not _FORMAT_IDENTITY.match(normalise):
        raise ValueError(
            "L'identity doit suivre la forme SITE-FONCTION-NN "
            "(deux segments alphanumériques puis un numéro à 2 chiffres, ex. CLA-ST-01)"
        )
    return normalise


def _verifier_unicite(db: Session, identity: str, numero_serie: str, exclure_id: int | None = None) -> None:
    requete_identity = select(Equipement).where(Equipement.identity == identity)
    requete_serie = select(Equipement).where(Equipement.numero_serie == numero_serie)
    if exclure_id is not None:
        requete_identity = requete_identity.where(Equipement.id != exclure_id)
        requete_serie = requete_serie.where(Equipement.id != exclure_id)
    if db.scalar(requete_identity) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"L'identity « {identity} » existe déjà")
    if db.scalar(requete_serie) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Le numéro de série « {numero_serie} » existe déjà"
        )


def creer_equipement(db: Session, donnees: EquipementCreation, cree_par_id: int) -> Equipement:
    _verifier_unicite(db, donnees.identity, donnees.numero_serie)
    equipement = Equipement(
        identity=donnees.identity,
        marque=donnees.marque,
        modele=donnees.modele,
        numero_serie=donnees.numero_serie,
        adresse_mac=donnees.adresse_mac,
        site_id=donnees.site_id,
        emplacement=donnees.emplacement,
        date_installation=donnees.date_installation,
        fin_garantie=donnees.fin_garantie,
        cree_par_id=cree_par_id,
    )
    db.add(equipement)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Identity ou numéro de série déjà utilisé")
    db.refresh(equipement)
    return equipement


def mettre_a_jour_equipement(
    db: Session, equipement: Equipement, donnees: EquipementMiseAJour, modifie_par_id: int
) -> Equipement:
    champs = donnees.model_dump(exclude_unset=True)
    nouvelle_identity = champs.get("identity", equipement.identity)
    nouveau_numero_serie = champs.get("numero_serie", equipement.numero_serie)
    if "identity" in champs or "numero_serie" in champs:
        _verifier_unicite(db, nouvelle_identity, nouveau_numero_serie, exclure_id=equipement.id)
    for champ, valeur in champs.items():
        setattr(equipement, champ, valeur)
    equipement.modifie_par_id = modifie_par_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Identity ou numéro de série déjà utilisé")
    db.refresh(equipement)
    return equipement


def rechercher_equipements(
    db: Session,
    identity: str | None = None,
    site_id: int | None = None,
    numero_serie: str | None = None,
    marque: MarqueEquipement | None = None,
) -> list[Equipement]:
    """Recherche multicritère (section 5.2.3 du CDC : "Rechercher un équipement
    par identity, site, numéro de série ou marque"). Les critères textuels sont
    des correspondances partielles (l'identity/numéro de série complet n'est pas
    toujours connu sur le terrain) ; site et marque sont des égalités exactes."""
    requete = select(Equipement).where(Equipement.archive.is_(False))
    if identity:
        requete = requete.where(Equipement.identity.ilike(f"%{identity.strip()}%"))
    if numero_serie:
        requete = requete.where(Equipement.numero_serie.ilike(f"%{numero_serie.strip()}%"))
    if site_id is not None:
        requete = requete.where(Equipement.site_id == site_id)
    if marque is not None:
        requete = requete.where(Equipement.marque == marque)
    return list(db.scalars(requete.order_by(Equipement.identity)))


def obtenir_fiche(db: Session, equipement: Equipement) -> dict:
    """Fiche équipement (section 5.2.3 : "historique complet : configurations,
    inspections, incidents associés")."""
    configurations = list(
        db.scalars(
            select(Configuration)
            .where(Configuration.equipement_id == equipement.id)
            .order_by(Configuration.date_intervention.desc())
        )
    )
    inspections = list(
        db.scalars(
            select(Inspection)
            .where(Inspection.equipement_id == equipement.id, Inspection.archive.is_(False))
            .order_by(Inspection.date.desc())
        )
    )
    # Limite documentée (docs/JOURNAL.md, prompt 3.1) : faute de lien direct
    # SIGNALEMENT → EQUIPEMENT dans le dictionnaire, "incidents associés" est
    # interprété comme les incidents/accidents du même SITE, pas de l'équipement
    # précis — une corrélation par site, pas par équipement.
    incidents = list(
        db.scalars(
            select(Signalement)
            .where(
                Signalement.site_id == equipement.site_id,
                Signalement.type.in_(_TYPES_INCIDENT),
                Signalement.archive.is_(False),
            )
            .order_by(Signalement.date_constat.desc())
        )
    )
    return {
        "equipement": equipement,
        "configurations": configurations,
        "inspections": inspections,
        "incidents": incidents,
    }
