"""Tests du modèle de données (prompt 0.2). Vérifient que les 14 entités sont
correctement déclarées et que les relations clés — notamment le cycle
SITE <-> UTILISATEUR résolu par use_alter — fonctionnent réellement, pas seulement
à la lecture du code."""
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 — enregistre les 14 entités
from app.db.base import Base
from app.models.cotation_risque import CotationRisque
from app.models.enums import (
    CategorieRisque,
    NiveauRisque,
    RoleUtilisateur,
    TypeSite,
)
from app.models.risque import Risque
from app.models.site import Site
from app.models.utilisateur import Utilisateur

ENTITES_ATTENDUES = {
    "action",
    "configuration",
    "document",
    "epi",
    "equipement",
    "evaluation_slam",
    "inspection",
    "journal_acces",
    "permis",
    "risque",
    "secret",
    "signalement",
    "site",
    "utilisateur",
}


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_les_14_entites_sont_enregistrees():
    tables = set(Base.metadata.tables.keys())
    manquantes = ENTITES_ATTENDUES - tables
    assert not manquantes, f"Entités manquantes : {manquantes}"


def test_toutes_les_tables_metier_ont_la_base_commune():
    colonnes_attendues = {"id", "cree_le", "cree_par_id", "modifie_le", "modifie_par_id", "archive", "organisation_id"}
    for nom_table in ENTITES_ATTENDUES - {"journal_acces"}:
        table = Base.metadata.tables[nom_table]
        colonnes = {c.name for c in table.columns}
        assert colonnes_attendues <= colonnes, f"{nom_table} : colonnes de base manquantes {colonnes_attendues - colonnes}"


def test_journal_acces_est_ecriture_seule_par_construction():
    """Ne porte ni modifie_le ni archive : rien dans le schéma ne suggère qu'une
    entrée puisse être modifiée ou archivée (règle 4, CLAUDE.md)."""
    colonnes = {c.name for c in Base.metadata.tables["journal_acces"].columns}
    assert "modifie_le" not in colonnes
    assert "modifie_par_id" not in colonnes
    assert "archive" not in colonnes


def test_cycle_site_utilisateur_fonctionne_en_pratique(session):
    """Le MCD relie SITE et UTILISATEUR dans les deux sens (site_id sur
    UTILISATEUR, cree_par_id vers UTILISATEUR sur SITE). C'est ce cycle que
    use_alter=True doit rendre possible à la création du schéma."""
    site = Site(nom="Siège Bamako", type=TypeSite.SIEGE, adresse="Hamdallaye ACI 2000")
    session.add(site)
    session.flush()

    admin = Utilisateur(
        nom="Traoré",
        prenom="Alassane",
        identifiant="a.traore",
        mot_de_passe="hash-factice",
        role=RoleUtilisateur.ADMINISTRATEUR,
        site_id=site.id,
    )
    session.add(admin)
    session.flush()

    site.cree_par_id = admin.id
    session.commit()

    assert site.id is not None
    assert admin.site_id == site.id
    assert site.cree_par_id == admin.id


def test_risque_ne_porte_plus_la_cotation_elle_meme(session):
    """Mis à jour au prompt 4.1 : RISQUE ne porte plus que l'identité stable du
    risque, la cotation (probabilite/gravite/criticite/niveau, calculés par le
    service métier) vit désormais sur CotationRisque — voir app/models/risque.py
    pour la justification (une réévaluation ne remplace jamais la précédente)."""
    site = Site(nom="Site technique", type=TypeSite.CLIENT)
    session.add(site)
    session.flush()

    utilisateur = Utilisateur(
        nom="Diarra",
        prenom="Oumou",
        identifiant="o.diarra",
        mot_de_passe="hash-factice",
        role=RoleUtilisateur.REFERENT_SHEQ,
        site_id=site.id,
    )
    session.add(utilisateur)
    session.flush()

    risque = Risque(
        numero=1,
        danger="Chute de hauteur lors d'une intervention sur pylône",
        categorie=CategorieRisque.CHUTE_CIRCULATION,
        unite_travail="Terrain",
    )
    session.add(risque)
    session.flush()

    cotation = CotationRisque(
        risque_id=risque.id,
        probabilite=3,
        gravite=5,
        criticite=15,
        niveau=NiveauRisque.CRITIQUE,
        mesures_proposees="Port du harnais obligatoire, permis de travail en hauteur",
        date_evaluation=date.today(),
        auteur_id=utilisateur.id,
    )
    session.add(cotation)
    session.commit()

    assert risque.id is not None
    assert cotation.id is not None
    assert cotation.criticite == cotation.probabilite * cotation.gravite


def test_probabilite_hors_bornes_est_rejetee(session):
    site = Site(nom="Site", type=TypeSite.SIEGE)
    session.add(site)
    session.flush()
    utilisateur = Utilisateur(
        nom="Test",
        prenom="Test",
        identifiant="t.test",
        mot_de_passe="hash-factice",
        role=RoleUtilisateur.REFERENT_SHEQ,
        site_id=site.id,
    )
    session.add(utilisateur)
    session.flush()

    risque = Risque(
        numero=2,
        danger="Danger factice",
        categorie=CategorieRisque.ELECTRIQUE,
        unite_travail="Bureaux",
    )
    session.add(risque)
    session.flush()

    cotation = CotationRisque(
        risque_id=risque.id,
        probabilite=6,  # hors bornes 1-5
        gravite=3,
        criticite=18,
        niveau=NiveauRisque.CRITIQUE,
        mesures_proposees="—",
        date_evaluation=date.today(),
        auteur_id=utilisateur.id,
    )
    session.add(cotation)
    with pytest.raises(Exception):
        session.commit()
