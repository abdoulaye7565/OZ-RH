"""Logique métier du module EPI (prompt 2.1, section 5.3.2 du CDC et règle 6 du
point 7 de CLAUDE.md)."""
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import StatutEpi, TypeEpi
from app.models.epi import Epi
from app.schemas.epi import EpiCreation

PERIODICITE_VERIFICATION = relativedelta(months=12)
_TENTATIVES_NUMERO = 5

# Chapitre 7.3.1 du CDC ne donne les lettres que pour 3 des 6 types (H, L, C) ;
# les trois autres sont une interprétation, à confirmer avec le référent SHEQ.
PREFIXES_NUMERO: dict[TypeEpi, str] = {
    TypeEpi.HARNAIS: "H",
    TypeEpi.LONGE: "L",
    TypeEpi.CASQUE: "C",
    TypeEpi.ANTICHUTE_MOBILE: "A",
    TypeEpi.CONNECTEUR: "K",
    TypeEpi.LIGNE_DE_VIE: "V",
}


def _generer_numero(db: Session, type_epi: TypeEpi) -> str:
    """Séquence globale, pas une séquence par lettre : l'exemple du prompt 2.1
    ("H-001, L-002, C-003") attribue des numéros consécutifs à des EPI de types
    différents, pas 001 à chaque nouvelle lettre."""
    prefixe = PREFIXES_NUMERO[type_epi]
    dernier = db.scalar(select(Epi.numero).order_by(Epi.id.desc()).limit(1))
    prochain_numero = int(dernier.rsplit("-", 1)[-1]) + 1 if dernier else 1
    return f"{prefixe}-{prochain_numero:03d}"


def _verifier_non_reforme(epi: Epi) -> None:
    if epi.statut == StatutEpi.REFORME:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet EPI est réformé : aucune opération ne peut le remettre en service, même pour un administrateur",
        )


def creer_epi(db: Session, donnees: EpiCreation, cree_par_id: int) -> Epi:
    for tentative in range(_TENTATIVES_NUMERO):
        epi = Epi(
            numero=_generer_numero(db, donnees.type),
            type=donnees.type,
            marque_modele=donnees.marque_modele,
            date_fabrication=donnees.date_fabrication,
            date_mise_service=donnees.date_mise_service,
            date_limite=donnees.date_limite,
            porteur_id=donnees.porteur_id,
            # Amorce le cycle de vérification dès la mise en service, avant toute
            # vérification réelle : le dictionnaire (7.2.6) ne donne la formule
            # qu'après une vérification ("dernière vérification + 12 mois") ;
            # sans cette amorce, un EPI neuf jamais vérifié n'aurait pas
            # d'échéance et serait donc "conforme" indéfiniment par défaut.
            prochaine_verification=donnees.date_mise_service + PERIODICITE_VERIFICATION,
            statut=StatutEpi.EN_SERVICE,
            cree_par_id=cree_par_id,
        )
        db.add(epi)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if tentative == _TENTATIVES_NUMERO - 1:
                raise
            continue
        db.refresh(epi)
        return epi
    raise AssertionError("inatteignable")


def modifier_affectation(db: Session, epi: Epi, porteur_id: int | None, modifie_par_id: int) -> Epi:
    _verifier_non_reforme(epi)
    epi.porteur_id = porteur_id
    epi.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(epi)
    return epi


def enregistrer_verification_periodique(
    db: Session, epi: Epi, conforme: bool, modifie_par_id: int
) -> Epi:
    _verifier_non_reforme(epi)
    aujourdhui = date.today()
    epi.derniere_verification = aujourdhui
    epi.prochaine_verification = aujourdhui + PERIODICITE_VERIFICATION
    epi.statut = StatutEpi.EN_SERVICE if conforme else StatutEpi.A_VERIFIER
    epi.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(epi)
    return epi


def enregistrer_verification_avant_utilisation(
    db: Session, epi: Epi, conforme: bool, modifie_par_id: int
) -> Epi:
    """Contrôle léger avant usage : ne touche pas au cycle de vérification
    périodique (derniere_verification/prochaine_verification). Aucune trace
    persistante d'un contrôle CONFORME (aucune table d'historique parmi les 14
    entités, même limite que documentée au prompt 1.6 pour le cas de recette
    13) : seul un contrôle NON CONFORME a un effet, il retire l'EPI du service
    immédiat en le passant "à vérifier"."""
    _verifier_non_reforme(epi)
    if not conforme:
        epi.statut = StatutEpi.A_VERIFIER
        epi.modifie_par_id = modifie_par_id
        db.commit()
        db.refresh(epi)
    return epi


def retirer(db: Session, epi: Epi, modifie_par_id: int) -> Epi:
    _verifier_non_reforme(epi)
    epi.statut = StatutEpi.RETIRE
    epi.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(epi)
    return epi


def reformer(db: Session, epi: Epi, motif: str, modifie_par_id: int) -> Epi:
    """Irréversible par construction : _verifier_non_reforme lève 409 si déjà
    réformé, et aucune autre fonction de ce module ne peut faire sortir un EPI
    de ce statut (vérifié explicitement par les tests)."""
    _verifier_non_reforme(epi)
    epi.statut = StatutEpi.REFORME
    epi.motif_reforme = motif
    epi.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(epi)
    return epi


def verifications_dues(db: Session, horizon_jours: int = 30) -> list[Epi]:
    requete = (
        select(Epi)
        .where(
            Epi.archive.is_(False),
            Epi.statut.notin_((StatutEpi.RETIRE, StatutEpi.REFORME)),
            Epi.prochaine_verification.is_not(None),
            Epi.prochaine_verification <= date.today() + timedelta(days=horizon_jours),
        )
        .order_by(Epi.prochaine_verification.asc())
    )
    return list(db.scalars(requete))
