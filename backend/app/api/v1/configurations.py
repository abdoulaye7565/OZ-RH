"""Routes du module Fiches de configuration (prompt 3.2, section 5.2.3 du CDC)."""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.permissions import Permissions
from app.db.session import get_db
from app.models.configuration import Configuration
from app.models.enums import TypeIntervention
from app.models.equipement import Equipement
from app.models.site import Site
from app.models.utilisateur import Utilisateur
from app.schemas.configuration import ConfigurationCreation, ConfigurationSortie
from app.services.configuration_service import creer_configuration, evaluer_conformite, generer_pdf

router = APIRouter(prefix="/configurations", tags=["configurations"])

NOMBRE_MAX_SAUVEGARDES = 5


def _vers_sortie(configuration: Configuration) -> ConfigurationSortie:
    signal_conforme, ccq_conforme = evaluer_conformite(configuration.signal_dbm, configuration.ccq_pourcent)
    sortie = ConfigurationSortie.model_validate(configuration)
    sortie.signal_conforme = signal_conforme
    sortie.ccq_conforme = ccq_conforme
    return sortie


def _recuperer(db: Session, configuration_id: int) -> Configuration:
    configuration = db.get(Configuration, configuration_id)
    if configuration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fiche de configuration introuvable")
    return configuration


def _parser_json(brut: str | None, champ: str) -> dict | None:
    if not brut:
        return None
    try:
        valeur = json.loads(brut)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{champ} : JSON invalide")
    if not isinstance(valeur, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{champ} : un objet JSON est attendu")
    return valeur


@router.post("", response_model=ConfigurationSortie, status_code=status.HTTP_201_CREATED)
async def creer(
    equipement_id: int = Form(...),
    type_intervention: TypeIntervention = Form(...),
    version_logicielle: str | None = Form(None),
    parametres_reseau: str = Form(...),
    parametres_sansfil: str | None = Form(None),
    signal_dbm: float | None = Form(None),
    ccq_pourcent: int | None = Form(None),
    date_intervention: datetime | None = Form(None),
    fichiers: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role(*Permissions.GERER_PARC)),
) -> ConfigurationSortie:
    donnees = ConfigurationCreation(
        equipement_id=equipement_id,
        type_intervention=type_intervention,
        version_logicielle=version_logicielle,
        parametres_reseau=_parser_json(parametres_reseau, "parametres_reseau") or {},
        parametres_sansfil=_parser_json(parametres_sansfil, "parametres_sansfil"),
        signal_dbm=signal_dbm,
        ccq_pourcent=ccq_pourcent,
        date_intervention=date_intervention,
    )
    configuration = await creer_configuration(db, donnees, fichiers, technicien_id=utilisateur.id)
    return _vers_sortie(configuration)


@router.get("/{configuration_id}", response_model=ConfigurationSortie)
def lire(
    configuration_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> ConfigurationSortie:
    return _vers_sortie(_recuperer(db, configuration_id))


@router.get("/{configuration_id}/export-pdf")
def exporter_pdf(
    configuration_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Response:
    configuration = _recuperer(db, configuration_id)
    equipement = db.get(Equipement, configuration.equipement_id)
    technicien = db.get(Utilisateur, configuration.technicien_id)
    site = db.get(Site, equipement.site_id)
    contenu = generer_pdf(configuration, equipement, technicien, site)
    return Response(
        content=contenu,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{configuration.reference}.pdf"'},
    )
