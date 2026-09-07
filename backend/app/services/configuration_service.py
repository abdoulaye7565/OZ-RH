"""Logique métier du module Fiches de configuration (prompt 3.2, section 5.2.3
du CDC)."""
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.fichiers import enregistrer_sauvegardes
from app.core.pdf import DocumentPDF
from app.models.configuration import Configuration
from app.models.enums import MarqueEquipement
from app.models.equipement import Equipement
from app.schemas.configuration import (
    ConfigurationCreation,
    ParametresReseauGrandstream,
    ParametresReseauMikroTik,
    ParametresReseauRuijie,
    ParametresReseauUbiquiti,
    ParametresSansFilMikroTik,
    ParametresSansFilUbiquiti,
)

_TENTATIVES_REFERENCE = 5

SCHEMAS_RESEAU: dict[MarqueEquipement, type[BaseModel]] = {
    MarqueEquipement.MIKROTIK: ParametresReseauMikroTik,
    MarqueEquipement.GRANDSTREAM: ParametresReseauGrandstream,
    MarqueEquipement.UBIQUITI: ParametresReseauUbiquiti,
    MarqueEquipement.RUIJIE: ParametresReseauRuijie,
}

SCHEMAS_SANSFIL: dict[MarqueEquipement, type[BaseModel] | None] = {
    MarqueEquipement.MIKROTIK: ParametresSansFilMikroTik,
    MarqueEquipement.GRANDSTREAM: None,
    MarqueEquipement.UBIQUITI: ParametresSansFilUbiquiti,
    MarqueEquipement.RUIJIE: None,
}

# Seuils repris littéralement des fiches papier réelles (FOR-SHEQ-006 section 4 :
# "Signal (dBm) : objectif : -50 à -65" ; FOR-SHEQ-008 section 4 : mêmes valeurs)
# — s'appliquent uniquement à MikroTik et Ubiquiti (liaisons radio), pas à
# Grandstream (téléphonie) ni Ruijie (filaire/Wi-Fi local), qui n'envoient pas
# ces mesures.
SEUIL_SIGNAL_DBM_MIN = -65.0
SEUIL_SIGNAL_DBM_MAX = -50.0
SEUIL_CCQ_POURCENT_MIN = 90


def _generer_reference(db: Session) -> str:
    """Forme ENR-SHEQ-AAAA-NNN (point 7, CLAUDE.md : nommage des
    « enregistrements »), confirmée par la maquette mobile (toast "Fiche
    enregistrée · ENR-SHEQ-2026-118", écran s-config)."""
    annee = datetime.now(timezone.utc).year
    prefixe = f"ENR-SHEQ-{annee}-"
    dernier = db.scalar(
        select(Configuration.reference)
        .where(Configuration.reference.like(f"{prefixe}%"))
        .order_by(Configuration.reference.desc())
        .limit(1)
    )
    prochain_numero = int(dernier.rsplit("-", 1)[-1]) + 1 if dernier else 1
    return f"{prefixe}{prochain_numero:03d}"


def _erreurs_lisibles(exc: ValidationError) -> list[str]:
    return [f"{'.'.join(str(p) for p in e['loc'])} : {e['msg']}" for e in exc.errors()]


def valider_parametres(
    marque: MarqueEquipement, parametres_reseau: dict, parametres_sansfil: dict | None
) -> tuple[dict, dict | None]:
    """Valide les paramètres reçus contre le schéma de la marque de l'équipement
    concerné (pas de la requête elle-même, qui ne connaît pas la marque tant que
    l'équipement n'est pas chargé) — un même corps de requête générique
    (`parametres_reseau`/`parametres_sansfil` en dict libre) est donc validé
    différemment selon l'équipement visé."""
    schema_reseau = SCHEMAS_RESEAU[marque]
    try:
        reseau_valide = schema_reseau(**parametres_reseau).model_dump()
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"parametres_reseau": _erreurs_lisibles(exc)},
        )

    schema_sansfil = SCHEMAS_SANSFIL[marque]
    if schema_sansfil is None:
        if parametres_sansfil:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"« {marque.value} » n'a pas de volet sans fil dans ce module : parametres_sansfil doit être absent",
            )
        return reseau_valide, None

    if parametres_sansfil is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"parametres_sansfil est requis pour la marque « {marque.value} »",
        )
    try:
        sansfil_valide = schema_sansfil(**parametres_sansfil).model_dump()
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"parametres_sansfil": _erreurs_lisibles(exc)},
        )
    return reseau_valide, sansfil_valide


def evaluer_conformite(signal_dbm: float | None, ccq_pourcent: int | None) -> tuple[bool | None, bool | None]:
    """None = sans objet (marque sans cette mesure), pas un défaut caché — cohérent
    avec le code couleur gris = sans objet (charte visuelle, CLAUDE.md point 8),
    même principe que Epi.est_conforme et Inspection.taux_conformite."""
    signal_conforme = (
        None if signal_dbm is None else (SEUIL_SIGNAL_DBM_MIN <= signal_dbm <= SEUIL_SIGNAL_DBM_MAX)
    )
    ccq_conforme = None if ccq_pourcent is None else (ccq_pourcent >= SEUIL_CCQ_POURCENT_MIN)
    return signal_conforme, ccq_conforme


def nom_sauvegarde_attendu(identity: str, date_intervention: date) -> str:
    """Forme SITE-IDENTITY-AAAAMMJJ (chapitre 5.2.3 du CDC, point 7 de
    CLAUDE.md) : `identity` suit déjà elle-même la forme SITE-FONCTION-NN
    (prompt 3.1), le "SITE" de la convention de nommage des sauvegardes est
    donc son propre premier segment — confirmé par la maquette mobile (drop-zone
    de l'écran s-config : "FAS-AP-01-20260904"), pas un second préfixe de site
    distinct concaténé en plus de l'identity complète."""
    return f"{identity}-{date_intervention:%Y%m%d}"


def _valider_noms_sauvegarde(fichiers: list[UploadFile], identity: str, date_intervention: date) -> None:
    attendu = nom_sauvegarde_attendu(identity, date_intervention)
    for fichier in fichiers:
        nom = fichier.filename or ""
        stem = Path(nom).stem
        if stem != attendu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nom de fichier de sauvegarde non conforme : « {nom} » — attendu « {attendu}{Path(nom).suffix or ''} »",
            )


async def creer_configuration(
    db: Session,
    donnees: ConfigurationCreation,
    fichiers_sauvegarde: list[UploadFile],
    technicien_id: int,
) -> Configuration:
    """Immuable dès la création (règle 5, CLAUDE.md) : aucune route de
    modification n'existe pour cette entité (voir app/api/v1/configurations.py)
    — une correction s'effectue en rappelant cette fonction, ce qui crée une
    nouvelle fiche avec une nouvelle référence, l'ancienne restant consultable
    telle quelle dans l'historique de la fiche équipement (prompt 3.1)."""
    equipement = db.get(Equipement, donnees.equipement_id)
    if equipement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Équipement introuvable")

    parametres_reseau, parametres_sansfil = valider_parametres(
        equipement.marque, donnees.parametres_reseau, donnees.parametres_sansfil
    )

    date_intervention = donnees.date_intervention or datetime.now(timezone.utc)

    # Contrôle du nommage AVANT toute écriture sur disque (tout ou rien, même
    # principe que app/core/fichiers.py::enregistrer_photos) : une seule
    # sauvegarde mal nommée rejette l'ensemble de la fiche, rien n'est déposé.
    if fichiers_sauvegarde:
        _valider_noms_sauvegarde(fichiers_sauvegarde, equipement.identity, date_intervention.date())

    chemins_sauvegarde = (
        await enregistrer_sauvegardes(fichiers_sauvegarde, sous_dossier="configurations", nombre_max=5)
        if fichiers_sauvegarde
        else None
    )

    for tentative in range(_TENTATIVES_REFERENCE):
        configuration = Configuration(
            reference=_generer_reference(db),
            equipement_id=donnees.equipement_id,
            type_intervention=donnees.type_intervention,
            version_logicielle=donnees.version_logicielle,
            parametres_reseau=parametres_reseau,
            parametres_sansfil=parametres_sansfil,
            signal_dbm=donnees.signal_dbm,
            ccq_pourcent=donnees.ccq_pourcent,
            fichiers_sauvegarde=chemins_sauvegarde,
            technicien_id=technicien_id,
            date_intervention=date_intervention,
            cree_par_id=technicien_id,
        )
        db.add(configuration)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if tentative == _TENTATIVES_REFERENCE - 1:
                raise
            continue
        db.refresh(configuration)
        return configuration
    raise AssertionError("inatteignable")


def generer_pdf(configuration: Configuration, equipement: Equipement, technicien, site) -> bytes:
    """Export PDF (section 5.2.3 du CDC : "Exporter une fiche de configuration au
    format PDF"). Reprend l'ordre des sections du formulaire papier réel
    (Intervention, Équipement, Réseau, Sans fil/spécifique, Sauvegarde,
    Validation) — la section « Identifiants d'accès (CONFIDENTIEL) » du papier
    est délibérément absente : ces identifiants n'existent nulle part dans
    CONFIGURATION (règle de conception, section 5.2.3), donc rien à exporter là.
    Mise en page simple (pas un fac-similé pixel du papier, aucun gabarit visuel
    exploitable n'étant disponible hors du fichier CONFIDENTIEL lui-même) mais
    fidèle à l'ordre et au contenu des sections."""
    pdf = DocumentPDF(f"FICHE DE CONFIGURATION {equipement.marque.value.upper()}", configuration.reference)

    pdf.section(
        "1. Intervention",
        [
            ("Date", configuration.date_intervention.strftime("%d/%m/%Y %H:%M")),
            ("Technicien", f"{technicien.prenom} {technicien.nom}"),
            ("Site / Client", site.nom),
            ("Type", configuration.type_intervention.value),
        ],
    )
    pdf.section(
        "2. Équipement",
        [
            ("Identity", equipement.identity),
            ("Marque", equipement.marque.value),
            ("Modèle", equipement.modele),
            ("N° de série", equipement.numero_serie),
            ("Adresse MAC", equipement.adresse_mac or "—"),
            ("Emplacement", equipement.emplacement),
            ("Version", configuration.version_logicielle or "—"),
        ],
    )
    pdf.section("3. Réseau", [(cle, valeur) for cle, valeur in (configuration.parametres_reseau or {}).items()])
    if configuration.parametres_sansfil:
        pdf.section("4. Sans fil / spécifique marque", list(configuration.parametres_sansfil.items()))

    signal_conforme, ccq_conforme = evaluer_conformite(configuration.signal_dbm, configuration.ccq_pourcent)
    if configuration.signal_dbm is not None or configuration.ccq_pourcent is not None:
        pdf.section(
            "5. Mesures de liaison",
            [
                (
                    "Signal (dBm)",
                    f"{configuration.signal_dbm} — {'conforme' if signal_conforme else 'hors objectif'}"
                    if configuration.signal_dbm is not None
                    else "—",
                ),
                (
                    "CCQ (%)",
                    f"{configuration.ccq_pourcent} — {'conforme' if ccq_conforme else 'hors objectif'}"
                    if configuration.ccq_pourcent is not None
                    else "—",
                ),
            ],
        )

    pdf.section(
        "6. Sauvegarde",
        [("Fichier(s)", ", ".join(Path(p).name for p in configuration.fichiers_sauvegarde) if configuration.fichiers_sauvegarde else "Aucune")],
    )

    pdf.pied_de_page(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), f"{technicien.prenom} {technicien.nom}")
    return pdf.construire()
