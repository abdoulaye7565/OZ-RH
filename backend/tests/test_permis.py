"""Tests du cycle de vie des permis (prompt 2.2) — la règle de blocage
elle-même est testée en détail dans test_regle_blocage_permis.py ; ici on
vérifie son intégration dans les routes (création, validation, refus, clôture)."""
from datetime import date, datetime, timedelta, timezone

import pytest

from app.core.security import creer_access_token, hacher_mot_de_passe
from app.models.enums import DecisionSlam, RoleUtilisateur, StatutEpi, TypeEpi
from app.models.epi import Epi
from app.models.evaluation_slam import EvaluationSlam
from app.models.utilisateur import Utilisateur


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


@pytest.fixture()
def intervenant_conforme(db_session, site):
    u = Utilisateur(
        nom="Koné",
        prenom="Conforme",
        identifiant="conforme.test",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(u)
    db_session.commit()

    db_session.add(
        Epi(
            numero="H-010",
            type=TypeEpi.HARNAIS,
            marque_modele="Test",
            date_mise_service=date.today(),
            date_limite=date.today().replace(year=date.today().year + 10),
            prochaine_verification=date.today() + timedelta(days=300),
            porteur_id=u.id,
            statut=StatutEpi.EN_SERVICE,
        )
    )
    db_session.add(
        EvaluationSlam(
            utilisateur_id=u.id,
            etapes_validees=[[True] * 4] * 4,
            decision=DecisionSlam.GO,
            date=datetime.now(timezone.utc),
        )
    )
    db_session.commit()
    return u


def _donnees_permis(site, intervenant, surveillant, **overrides):
    debut = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    donnees = {
        "site_id": site.id,
        "nature_travaux": "Alignement liaison",
        "support": "pylone",
        "intervenant_ids": [intervenant.id],
        "surveillant_id": surveillant.id,
        "debut_validite": debut.isoformat(),
        "fin_validite": (debut + timedelta(hours=4)).isoformat(),
    }
    donnees.update(overrides)
    return donnees


def test_creation_conforme_statut_demande(client, technicien, referent_sheq, site, intervenant_conforme):
    reponse = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["statut"] == "demande"
    assert corps["controles"]["conforme"] is True
    assert corps["reference"] is not None


def test_creation_non_conforme_statut_bloque_avec_motif(client, technicien, referent_sheq, site):
    intervenant_sans_rien = referent_sheq  # aucun EPI, aucun SLAM pour ce test
    reponse = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_sans_rien, technicien),
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["statut"] == "bloque"
    assert corps["controles"]["conforme"] is False
    assert len(corps["controles"]["motifs"]) > 0


def test_validation_delivre_le_permis(client, technicien, referent_sheq, responsable, site, intervenant_conforme):
    creation = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    ).json()

    reponse = client.post(f"/api/v1/permis/{creation['id']}/valider", headers=_entete(responsable))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["statut"] == "delivre"
    assert corps["validateur_id"] == responsable.id


def test_validation_dun_permis_bloque_refusee_avec_motifs(client, technicien, referent_sheq, responsable, site):
    creation = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, referent_sheq, technicien),
    ).json()
    assert creation["statut"] == "bloque"

    reponse = client.post(f"/api/v1/permis/{creation['id']}/valider", headers=_entete(responsable))
    assert reponse.status_code == 409
    assert "motifs" in reponse.json()["detail"]


def test_impossible_de_contourner_en_validant_apres_coup(
    client, db_session, technicien, referent_sheq, responsable, site, intervenant_conforme
):
    """La règle est réévaluée à la validation, pas seulement à la création :
    un EPI qui devient non conforme APRÈS la demande doit encore bloquer la
    délivrance — c'est le cœur de "impossible à contourner par l'API"."""
    creation = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    ).json()
    assert creation["statut"] == "demande"

    # L'EPI de l'intervenant se dégrade entre la demande et la validation.
    epi = db_session.query(Epi).filter_by(porteur_id=intervenant_conforme.id).first()
    epi.statut = StatutEpi.REFORME
    db_session.commit()

    reponse = client.post(f"/api/v1/permis/{creation['id']}/valider", headers=_entete(responsable))
    assert reponse.status_code == 409

    lecture = client.get(f"/api/v1/permis/{creation['id']}", headers=_entete(responsable))
    assert lecture.json()["statut"] == "bloque"


def test_technicien_ne_peut_pas_valider(client, technicien, referent_sheq, site, intervenant_conforme):
    creation = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    ).json()

    reponse = client.post(f"/api/v1/permis/{creation['id']}/valider", headers=_entete(technicien))
    assert reponse.status_code == 403


def test_refus_humain_malgre_controles_conformes(
    client, technicien, referent_sheq, responsable, site, intervenant_conforme
):
    """Le responsable garde le dernier mot même si les contrôles automatiques
    passent (météo, jugement...) — 5.2.2 liste "refuser" comme une action
    distincte de la règle automatique."""
    creation = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    ).json()

    reponse = client.post(
        f"/api/v1/permis/{creation['id']}/refuser",
        headers=_entete(responsable),
        json={"motif": "Alerte météo locale non captée par le système"},
    )
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "refuse"


def test_cloture_seulement_apres_delivrance(
    client, technicien, referent_sheq, responsable, site, intervenant_conforme
):
    creation = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    ).json()

    # Pas encore délivré : la clôture doit être refusée.
    premiere_tentative = client.post(f"/api/v1/permis/{creation['id']}/cloturer", headers=_entete(responsable))
    assert premiere_tentative.status_code == 409

    client.post(f"/api/v1/permis/{creation['id']}/valider", headers=_entete(responsable))
    deuxieme_tentative = client.post(f"/api/v1/permis/{creation['id']}/cloturer", headers=_entete(responsable))
    assert deuxieme_tentative.status_code == 200
    assert deuxieme_tentative.json()["statut"] == "cloture"


def test_surveillant_parmi_les_intervenants_refuse_a_la_creation(
    client, technicien, referent_sheq, site, intervenant_conforme
):
    reponse = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, intervenant_conforme),
    )
    corps = reponse.json()
    assert corps["statut"] == "bloque"
    assert any("surveillant" in m.lower() for m in corps["controles"]["motifs"])


def test_permis_multi_jours_refuse(client, technicien, referent_sheq, site, intervenant_conforme):
    debut = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    donnees = _donnees_permis(
        site,
        intervenant_conforme,
        referent_sheq,
        fin_validite=(debut + timedelta(days=1)).isoformat(),
    )
    reponse = client.post("/api/v1/permis", headers=_entete(technicien), json=donnees)
    assert reponse.status_code == 422


def test_intervenant_ids_vide_refuse(client, technicien, referent_sheq, site, intervenant_conforme):
    donnees = _donnees_permis(site, intervenant_conforme, referent_sheq, intervenant_ids=[])
    reponse = client.post("/api/v1/permis", headers=_entete(technicien), json=donnees)
    assert reponse.status_code == 422


def test_aucune_route_de_suppression(client):
    reponse = client.delete("/api/v1/permis/1")
    assert reponse.status_code == 405


def test_creation_lie_l_evaluation_slam_du_jour_au_permis(client, technicien, referent_sheq, site, intervenant_conforme, db_session):
    """Revue d'ensemble 2026-09-10 ("ils ne sont pas liés") : à la création,
    l'évaluation SLAM GO du jour de chaque intervenant est rattachée au permis
    (colonne evaluation_slam.permis_id + sortie API)."""
    reponse = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    )
    assert reponse.status_code == 201
    corps = reponse.json()

    # Sortie API
    assert len(corps["evaluations_slam"]) == 1
    ev = corps["evaluations_slam"][0]
    assert ev["utilisateur_id"] == intervenant_conforme.id
    assert ev["decision"] == "GO"
    assert ev["utilisateur_nom"] == f"{intervenant_conforme.prenom} {intervenant_conforme.nom}"

    # Colonne en base
    ligne = db_session.scalars(
        __import__("sqlalchemy").select(EvaluationSlam).where(EvaluationSlam.utilisateur_id == intervenant_conforme.id)
    ).one()
    assert ligne.permis_id == corps["id"]


def test_revalidation_rattache_une_slam_plus_recente(client, technicien, referent_sheq, responsable, site, intervenant_conforme, db_session):
    """Si une SLAM plus récente (même jour) est saisie entre la demande et la
    validation, le permis délivré doit pointer vers celle-ci."""
    from sqlalchemy import select

    reponse = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json=_donnees_permis(site, intervenant_conforme, referent_sheq),
    )
    permis_id = reponse.json()["id"]
    ev_initiale = reponse.json()["evaluations_slam"][0]["id"]

    # Nouvelle SLAM GO, plus récente, le même jour.
    db_session.add(
        EvaluationSlam(
            utilisateur_id=intervenant_conforme.id,
            etapes_validees=[[True] * 4] * 4,
            decision=DecisionSlam.GO,
            date=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
    )
    db_session.commit()

    valide = client.post(f"/api/v1/permis/{permis_id}/valider", headers=_entete(responsable))
    assert valide.status_code == 200
    liees = valide.json()["evaluations_slam"]
    assert len(liees) == 1
    assert liees[0]["id"] != ev_initiale  # la plus récente

    # L'ancienne évaluation n'est plus rattachée à ce permis.
    ancienne = db_session.get(EvaluationSlam, ev_initiale)
    assert ancienne.permis_id is None
