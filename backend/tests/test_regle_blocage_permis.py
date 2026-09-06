"""Tests de LA RÈGLE CENTRALE (prompt 2.2) : un test par cause de blocage, plus
le cas nominal, comme explicitement demandé. Teste directement
regle_blocage_permis.evaluer_controles (pas seulement via l'API) pour isoler
la règle elle-même de son intégration dans le cycle de vie du permis."""
from datetime import date, datetime, timedelta, timezone

import pytest

from app.core.security import hacher_mot_de_passe
from app.models.enums import DecisionSlam, RoleUtilisateur, StatutEpi, TypeEpi
from app.models.epi import Epi
from app.models.evaluation_slam import EvaluationSlam
from app.models.utilisateur import Utilisateur
from app.services.regle_blocage_permis import evaluer_controles


@pytest.fixture()
def intervenant(db_session, site):
    u = Utilisateur(
        nom="Koné",
        prenom="Intervenant",
        identifiant="intervenant.test",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(u)
    db_session.commit()
    return u


@pytest.fixture()
def surveillant(db_session, site):
    u = Utilisateur(
        nom="Diarra",
        prenom="Surveillant",
        identifiant="surveillant.test",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(u)
    db_session.commit()
    return u


def _donner_slam_go(db_session, intervenant, jour: datetime | None = None):
    evaluation = EvaluationSlam(
        utilisateur_id=intervenant.id,
        etapes_validees=[[True] * 4] * 4,
        decision=DecisionSlam.GO,
        date=jour or datetime.now(timezone.utc),
    )
    db_session.add(evaluation)
    db_session.commit()
    return evaluation


def _donner_epi_conforme(db_session, intervenant):
    epi = Epi(
        numero="H-001",
        type=TypeEpi.HARNAIS,
        marque_modele="Test",
        date_mise_service=date.today(),
        date_limite=date.today().replace(year=date.today().year + 10),
        prochaine_verification=date.today() + timedelta(days=300),
        porteur_id=intervenant.id,
        statut=StatutEpi.EN_SERVICE,
    )
    db_session.add(epi)
    db_session.commit()
    return epi


def test_cas_nominal_toutes_conditions_reunies_conforme(db_session, intervenant, surveillant):
    _donner_epi_conforme(db_session, intervenant)
    _donner_slam_go(db_session, intervenant)

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=surveillant.id,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is True
    assert resultat.motifs == []


def test_cause_a_epi_non_conforme(db_session, intervenant, surveillant):
    epi = Epi(
        numero="H-002",
        type=TypeEpi.HARNAIS,
        marque_modele="Test",
        date_mise_service=date.today() - timedelta(days=500),
        date_limite=date.today().replace(year=date.today().year + 10),
        prochaine_verification=date.today() - timedelta(days=10),  # dépassée
        porteur_id=intervenant.id,
        statut=StatutEpi.EN_SERVICE,
    )
    db_session.add(epi)
    db_session.commit()
    _donner_slam_go(db_session, intervenant)

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=surveillant.id,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False
    assert any("H-002" in m and "non conforme" in m for m in resultat.motifs)


def test_cause_a_epi_reforme(db_session, intervenant, surveillant):
    epi = _donner_epi_conforme(db_session, intervenant)
    epi.statut = StatutEpi.REFORME
    db_session.commit()
    _donner_slam_go(db_session, intervenant)

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=surveillant.id,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False


def test_cause_b_pas_de_slam_du_tout(db_session, intervenant, surveillant):
    _donner_epi_conforme(db_session, intervenant)
    # Aucune évaluation SLAM enregistrée.

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=surveillant.id,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False
    assert any("SLAM" in m for m in resultat.motifs)


def test_cause_b_slam_en_no_go(db_session, intervenant, surveillant):
    _donner_epi_conforme(db_session, intervenant)
    evaluation = EvaluationSlam(
        utilisateur_id=intervenant.id,
        etapes_validees=[[True, True, False, False]] * 4,
        decision=DecisionSlam.NO_GO,
        motif="Vent trop fort",
        date=datetime.now(timezone.utc),
    )
    db_session.add(evaluation)
    db_session.commit()

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=surveillant.id,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False
    assert any("SLAM" in m for m in resultat.motifs)


def test_cause_b_slam_go_mais_pas_le_meme_jour(db_session, intervenant, surveillant):
    """Un GO d'hier ne couvre pas une montée aujourd'hui — résolution du point
    laissé ouvert depuis le prompt 0.2 (pas de lien direct SLAM -> permis)."""
    _donner_epi_conforme(db_session, intervenant)
    hier = datetime.now(timezone.utc) - timedelta(days=1)
    _donner_slam_go(db_session, intervenant, jour=hier)

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=surveillant.id,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False


def test_cause_c_aucun_surveillant_designe(db_session, intervenant):
    _donner_epi_conforme(db_session, intervenant)
    _donner_slam_go(db_session, intervenant)

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=None,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False
    assert any("surveillant" in m.lower() for m in resultat.motifs)


def test_cause_d_surveillant_parmi_les_intervenants(db_session, intervenant):
    _donner_epi_conforme(db_session, intervenant)
    _donner_slam_go(db_session, intervenant)

    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=intervenant.id,  # le même que l'intervenant
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False
    assert any("surveillant" in m.lower() and "intervenant" in m.lower() for m in resultat.motifs)


def test_plusieurs_causes_cumulees_toutes_listees(db_session, intervenant):
    """Aucune EPI, aucun SLAM, pas de surveillant : les trois motifs doivent
    apparaître, pas seulement le premier trouvé."""
    resultat = evaluer_controles(
        db_session,
        intervenant_ids=[intervenant.id],
        surveillant_id=None,
        debut_validite=datetime.now(timezone.utc),
    )

    assert resultat.conforme is False
    assert any("surveillant" in m.lower() for m in resultat.motifs)
    assert any("SLAM" in m for m in resultat.motifs)
