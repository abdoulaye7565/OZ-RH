import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — enregistre les 14 entités (+1, voir point_checklist.py)
from app.core.security import hacher_mot_de_passe
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.checklist_referentiel import lignes_a_semer
from app.models.enums import RoleUtilisateur, TypeSite
from app.models.point_checklist import PointChecklist
from app.models.site import Site
from app.models.utilisateur import Utilisateur


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    # Les tests utilisent create_all(), pas Alembic : la migration de données
    # qui sème les 93 points de checklist réels (dafa396b65c4) ne s'exécute
    # donc jamais ici. Semé directement depuis le même module partagé
    # (app/models/checklist_referentiel.py) pour ne jamais diverger de ce que
    # la migration insère réellement en développement/production.
    session.add_all(PointChecklist(**ligne) for ligne in lignes_a_semer())
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def site(db_session):
    s = Site(nom="Siège Bamako", type=TypeSite.SIEGE)
    db_session.add(s)
    db_session.commit()
    return s


@pytest.fixture()
def mot_de_passe_clair():
    return "UnMotDePasseSuffisammentSolide!42"


@pytest.fixture()
def administrateur(db_session, site, mot_de_passe_clair):
    admin = Utilisateur(
        nom="Traoré",
        prenom="Alassane",
        identifiant="a.traore",
        mot_de_passe=hacher_mot_de_passe(mot_de_passe_clair),
        role=RoleUtilisateur.ADMINISTRATEUR,
        site_id=site.id,
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture()
def technicien(db_session, site, mot_de_passe_clair):
    tech = Utilisateur(
        nom="Koné",
        prenom="Abdoulaye",
        identifiant="a.kone",
        mot_de_passe=hacher_mot_de_passe(mot_de_passe_clair),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(tech)
    db_session.commit()
    return tech


@pytest.fixture()
def referent_sheq(db_session, site, mot_de_passe_clair):
    referent = Utilisateur(
        nom="Diarra",
        prenom="Oumou",
        identifiant="o.diarra",
        mot_de_passe=hacher_mot_de_passe(mot_de_passe_clair),
        role=RoleUtilisateur.REFERENT_SHEQ,
        site_id=site.id,
    )
    db_session.add(referent)
    db_session.commit()
    return referent


@pytest.fixture()
def responsable(db_session, site, mot_de_passe_clair):
    resp = Utilisateur(
        nom="Traoré",
        prenom="Fatoumata",
        identifiant="f.traore",
        mot_de_passe=hacher_mot_de_passe(mot_de_passe_clair),
        role=RoleUtilisateur.RESPONSABLE,
        site_id=site.id,
    )
    db_session.add(resp)
    db_session.commit()
    return resp
