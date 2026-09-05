"""Tests du module EPI (prompt 2.1, section 5.3.2 du CDC)."""
from datetime import date, timedelta

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _donnees_epi(**overrides):
    donnees = {
        "type": "harnais",
        "marque_modele": "Petzl Avao",
        "date_mise_service": str(date.today()),
        "date_limite": str(date.today().replace(year=date.today().year + 10)),
    }
    donnees.update(overrides)
    return donnees


def test_creation_attribue_un_numero_selon_le_type(client, referent_sheq):
    r1 = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi(type="harnais")).json()
    r2 = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi(type="longe")).json()
    r3 = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi(type="casque")).json()

    assert r1["numero"] == "H-001"
    assert r2["numero"] == "L-002"
    assert r3["numero"] == "C-003"


def test_creation_amorce_la_prochaine_verification_a_12_mois(client, referent_sheq):
    mise_en_service = date(2026, 3, 15)
    reponse = client.post(
        "/api/v1/epi",
        headers=_entete(referent_sheq),
        json=_donnees_epi(date_mise_service=str(mise_en_service)),
    )
    corps = reponse.json()
    assert corps["prochaine_verification"] == "2027-03-15"
    assert corps["derniere_verification"] is None
    assert corps["est_conforme"] is True


def test_technicien_ne_peut_pas_creer_un_epi(client, technicien):
    reponse = client.post("/api/v1/epi", headers=_entete(technicien), json=_donnees_epi())
    assert reponse.status_code == 403


def test_verification_periodique_conforme_reconduit_le_cycle(client, referent_sheq):
    creation = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()

    reponse = client.post(
        f"/api/v1/epi/{creation['id']}/verification-periodique",
        headers=_entete(referent_sheq),
        json={"conforme": True},
    )
    corps = reponse.json()
    assert corps["statut"] == "en_service"
    assert corps["derniere_verification"] == str(date.today())
    assert corps["prochaine_verification"] == str(date.today().replace(year=date.today().year + 1))
    assert corps["est_conforme"] is True


def test_verification_periodique_non_conforme_passe_a_verifier(client, referent_sheq):
    creation = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()

    reponse = client.post(
        f"/api/v1/epi/{creation['id']}/verification-periodique",
        headers=_entete(referent_sheq),
        json={"conforme": False},
    )
    corps = reponse.json()
    assert corps["statut"] == "a_verifier"
    assert corps["est_conforme"] is False


def test_verification_avant_utilisation_conforme_ne_change_rien(client, referent_sheq, technicien):
    creation = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()

    reponse = client.post(
        f"/api/v1/epi/{creation['id']}/verification-avant-utilisation",
        headers=_entete(technicien),
        json={"conforme": True},
    )
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "en_service"


def test_verification_avant_utilisation_non_conforme_retire_du_service(client, referent_sheq, technicien):
    creation = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()

    reponse = client.post(
        f"/api/v1/epi/{creation['id']}/verification-avant-utilisation",
        headers=_entete(technicien),
        json={"conforme": False},
    )
    corps = reponse.json()
    assert corps["statut"] == "a_verifier"
    assert corps["est_conforme"] is False
    # Le cycle des 12 mois n'est pas affecté par un simple contrôle avant usage.
    assert corps["derniere_verification"] is None


def test_epi_avec_verification_depassee_est_non_conforme(client, db_session, referent_sheq):
    from app.models.epi import Epi
    from app.models.enums import TypeEpi, StatutEpi

    epi = Epi(
        numero="H-099",
        type=TypeEpi.HARNAIS,
        marque_modele="Test",
        date_mise_service=date.today() - timedelta(days=800),
        date_limite=date.today().replace(year=date.today().year + 10),
        derniere_verification=date.today() - timedelta(days=400),
        prochaine_verification=date.today() - timedelta(days=35),
        statut=StatutEpi.EN_SERVICE,
    )
    db_session.add(epi)
    db_session.commit()

    reponse = client.get(f"/api/v1/epi/{epi.id}", headers=_entete(referent_sheq))
    assert reponse.json()["est_conforme"] is False


def test_epi_reforme_ne_peut_etre_remis_en_service_par_aucune_route(client, referent_sheq, technicien):
    """Cas de test explicitement demandé par le prompt 2.1."""
    creation = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()
    epi_id = creation["id"]

    reforme = client.post(
        f"/api/v1/epi/{epi_id}/reformer",
        headers=_entete(referent_sheq),
        json={"motif": "A arrêté une chute lors d'une intervention"},
    )
    assert reforme.status_code == 200
    assert reforme.json()["statut"] == "reforme"
    assert reforme.json()["motif_reforme"] == "A arrêté une chute lors d'une intervention"

    # Aucune route, même administrateur, ne doit pouvoir le sortir de cet état.
    tentatives = [
        lambda: client.post(
            f"/api/v1/epi/{epi_id}/verification-periodique",
            headers=_entete(referent_sheq),
            json={"conforme": True},
        ),
        lambda: client.post(
            f"/api/v1/epi/{epi_id}/verification-avant-utilisation",
            headers=_entete(technicien),
            json={"conforme": True},
        ),
        lambda: client.post(f"/api/v1/epi/{epi_id}/retirer", headers=_entete(referent_sheq)),
        lambda: client.patch(
            f"/api/v1/epi/{epi_id}/affectation",
            headers=_entete(referent_sheq),
            json={"porteur_id": technicien.id},
        ),
        lambda: client.post(
            f"/api/v1/epi/{epi_id}/reformer",
            headers=_entete(referent_sheq),
            json={"motif": "Nouvelle tentative"},
        ),
    ]
    for tentative in tentatives:
        reponse = tentative()
        assert reponse.status_code == 409, f"attendu 409, obtenu {reponse.status_code} : {reponse.json()}"

    lecture = client.get(f"/api/v1/epi/{epi_id}", headers=_entete(referent_sheq))
    assert lecture.json()["statut"] == "reforme"
    assert lecture.json()["est_conforme"] is False


def test_affectation_a_un_porteur(client, referent_sheq, technicien):
    creation = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()

    reponse = client.patch(
        f"/api/v1/epi/{creation['id']}/affectation",
        headers=_entete(referent_sheq),
        json={"porteur_id": technicien.id},
    )
    assert reponse.json()["porteur_id"] == technicien.id


def test_liste_verifications_dues_sous_30_jours(client, referent_sheq):
    proche = client.post(
        "/api/v1/epi",
        headers=_entete(referent_sheq),
        json=_donnees_epi(date_mise_service=str(date.today() - timedelta(days=350))),
    ).json()
    lointain = client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi()).json()

    reponse = client.get("/api/v1/epi/verifications-dues", headers=_entete(referent_sheq))
    ids = {e["id"] for e in reponse.json()}
    assert proche["id"] in ids
    assert lointain["id"] not in ids


def test_epi_reforme_exclu_de_la_liste_des_verifications_dues(client, referent_sheq):
    creation = client.post(
        "/api/v1/epi",
        headers=_entete(referent_sheq),
        json=_donnees_epi(date_mise_service=str(date.today() - timedelta(days=350))),
    ).json()
    client.post(
        f"/api/v1/epi/{creation['id']}/reformer",
        headers=_entete(referent_sheq),
        json={"motif": "Test"},
    )

    reponse = client.get("/api/v1/epi/verifications-dues", headers=_entete(referent_sheq))
    ids = {e["id"] for e in reponse.json()}
    assert creation["id"] not in ids


def test_aucune_route_de_suppression(client):
    reponse = client.delete("/api/v1/epi/1")
    assert reponse.status_code == 405


def test_liste_ouverte_a_tout_le_personnel_authentifie(client, technicien, referent_sheq):
    client.post("/api/v1/epi", headers=_entete(referent_sheq), json=_donnees_epi())
    reponse = client.get("/api/v1/epi", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert len(reponse.json()) == 1
