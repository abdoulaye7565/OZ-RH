"""Tests du module Revues de direction (prompt 4.2, section 5.3.4 du CDC,
FOR-SHEQ-016)."""
from datetime import date, timedelta

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _donnees_revue(**overrides):
    donnees = {
        "date": str(date.today()),
        "lieu": "Siège Bamako",
        "periode_debut": str(date.today() - timedelta(days=90)),
        "periode_fin": str(date.today()),
        "participants": "Direction, référent SHEQ",
    }
    donnees.update(overrides)
    return donnees


def test_technicien_ne_peut_pas_creer_de_revue(client, technicien):
    reponse = client.post("/api/v1/revues", headers=_entete(technicien), json=_donnees_revue())
    assert reponse.status_code == 403


def test_creation_assemble_les_indicateurs_de_la_periode(client, responsable):
    reponse = client.post("/api/v1/revues", headers=_entete(responsable), json=_donnees_revue())
    assert reponse.status_code == 201
    corps = reponse.json()
    indicateurs = corps["donnees_entree"]["indicateurs"]
    assert "signalements_total" in indicateurs
    assert "accidents_incidents" in indicateurs
    assert "inspections_realisees" in indicateurs
    assert "risques_nouveaux" in indicateurs
    assert "seances_realisees" in indicateurs
    assert "avancement_plan_action" in indicateurs
    assert corps["donnees_entree"]["decisions_reportees"] == []


def test_decisions_non_soldees_reportees_dans_la_revue_suivante(client, responsable):
    revue_1 = client.post("/api/v1/revues", headers=_entete(responsable), json=_donnees_revue()).json()
    client.post(
        f"/api/v1/revues/{revue_1['id']}/decisions",
        headers=_entete(responsable),
        json={"libelle": "Renouveler les extincteurs", "responsable_id": responsable.id, "echeance": str(date.today() + timedelta(days=30))},
    )
    decision_soldee = client.post(
        f"/api/v1/revues/{revue_1['id']}/decisions",
        headers=_entete(responsable),
        json={"libelle": "Former les secouristes", "responsable_id": responsable.id, "echeance": str(date.today() + timedelta(days=10))},
    ).json()
    client.post(f"/api/v1/revues/decisions/{decision_soldee['id']}/solder", headers=_entete(responsable))

    revue_2 = client.post("/api/v1/revues", headers=_entete(responsable), json=_donnees_revue()).json()
    reportees = revue_2["donnees_entree"]["decisions_reportees"]
    assert len(reportees) == 1
    assert reportees[0]["libelle"] == "Renouveler les extincteurs"
    assert reportees[0]["revue_origine_id"] == revue_1["id"]


def test_solder_une_decision_deja_soldee_est_refuse(client, responsable):
    revue = client.post("/api/v1/revues", headers=_entete(responsable), json=_donnees_revue()).json()
    decision = client.post(
        f"/api/v1/revues/{revue['id']}/decisions",
        headers=_entete(responsable),
        json={"libelle": "X", "responsable_id": responsable.id, "echeance": str(date.today())},
    ).json()
    client.post(f"/api/v1/revues/decisions/{decision['id']}/solder", headers=_entete(responsable))
    reponse = client.post(f"/api/v1/revues/decisions/{decision['id']}/solder", headers=_entete(responsable))
    assert reponse.status_code == 409


def test_detail_revue_liste_ses_decisions(client, responsable):
    revue = client.post("/api/v1/revues", headers=_entete(responsable), json=_donnees_revue()).json()
    client.post(
        f"/api/v1/revues/{revue['id']}/decisions",
        headers=_entete(responsable),
        json={"libelle": "X", "responsable_id": responsable.id, "echeance": str(date.today())},
    )
    detail = client.get(f"/api/v1/revues/{revue['id']}", headers=_entete(responsable)).json()
    assert len(detail["decisions"]) == 1


def test_liste_les_revues_deja_creees(client, responsable, technicien):
    """2026-09-19 : sans cette route, aucun moyen de retrouver une revue une
    fois l'écran de création quitté — seules la création et la lecture par
    id existaient."""
    vide = client.get("/api/v1/revues", headers=_entete(responsable))
    assert vide.status_code == 200
    assert vide.json() == []

    revue = client.post("/api/v1/revues", headers=_entete(responsable), json=_donnees_revue()).json()

    reponse = client.get("/api/v1/revues", headers=_entete(responsable))
    assert reponse.status_code == 200
    references = [r["id"] for r in reponse.json()]
    assert revue["id"] in references

    refuse = client.get("/api/v1/revues", headers=_entete(technicien))
    assert refuse.status_code == 403


def test_referent_sheq_peut_gerer_les_revues(client, referent_sheq):
    """Rapprochement documenté (permissions.py) : le référent SHEQ n'est pas cité
    dans les Acteurs du CDC pour ce module, mais FOR-SHEQ-016 le désigne comme
    rédacteur/cosignataire du compte rendu."""
    reponse = client.post("/api/v1/revues", headers=_entete(referent_sheq), json=_donnees_revue())
    assert reponse.status_code == 201
