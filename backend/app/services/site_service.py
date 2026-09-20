"""Logique métier de l'entité SITE (hors dictionnaire, section 5.2.3 du CDC).

Ajout d'une gestion complète le 2026-09-10 (retour direct de l'utilisateur :
« on a un seul site alors que nous intervenons sur plusieurs sites ») : la
création/modification se faisait jusqu'ici directement en base. La consultation
(`GET /sites`) reste ouverte à tout le personnel ; création, modification et
archivage sont réservés à l'administrateur (Permissions.GERER_SITES).
"""
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.equipement import Equipement
from app.models.permis import Permis
from app.models.enums import StatutPermis
from app.models.site import Site
from app.schemas.site import SiteCreation, SiteMiseAJour


def lister_sites(db: Session) -> list[Site]:
    return list(db.scalars(select(Site).where(Site.archive.is_(False)).order_by(Site.nom)))


def obtenir_site(db: Session, site_id: int) -> Site:
    site = db.get(Site, site_id)
    if site is None or site.archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


def creer_site(db: Session, donnees: SiteCreation, cree_par_id: int) -> Site:
    site = Site(nom=donnees.nom, type=donnees.type, adresse=donnees.adresse, cree_par_id=cree_par_id)
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def modifier_site(db: Session, site: Site, donnees: SiteMiseAJour, modifie_par_id: int) -> Site:
    valeurs = donnees.model_dump(exclude_unset=True)
    for champ, valeur in valeurs.items():
        setattr(site, champ, valeur)
    site.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(site)
    return site


def archiver_site(db: Session, site: Site, modifie_par_id: int) -> Site:
    """Archivage logique (jamais de suppression, CLAUDE.md §2). Refusé tant que
    le site porte encore des rattachements actifs — on ne fait pas disparaître
    un lieu où des équipements sont déployés ou des permis en cours :
    l'utilisateur doit d'abord traiter ces rattachements."""
    equipements_actifs = db.scalar(
        select(func.count()).select_from(Equipement).where(
            Equipement.site_id == site.id, Equipement.archive.is_(False)
        )
    )
    if equipements_actifs:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Impossible d'archiver ce site : {equipements_actifs} équipement(s) y sont "
                "encore rattachés. Transférez ou archivez-les d'abord."
            ),
        )
    permis_en_cours = db.scalar(
        select(func.count()).select_from(Permis).where(
            Permis.site_id == site.id,
            Permis.archive.is_(False),
            Permis.statut.in_([StatutPermis.DEMANDE, StatutPermis.DELIVRE]),
        )
    )
    if permis_en_cours:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Impossible d'archiver ce site : {permis_en_cours} permis y sont en cours.",
        )
    site.archive = True
    site.modifie_par_id = modifie_par_id
    db.commit()
    db.refresh(site)
    return site
