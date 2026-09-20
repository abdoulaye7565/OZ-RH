"""Tests de la recherche globale d'en-tête (revue d'ensemble 2026-09-10)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _creer_risque(client, referent_sheq, danger):
    return client.post(
        "/api/v1/risques",
        headers=_entete(referent_sheq),
        json={
            "danger": danger,
            "categorie": "Chute / Circulation",
            "unite_travail": "Terrain",
            "cotation": {"probabilite": 3, "gravite": 4, "mesures_proposees": "Harnais"},
        },
    )


def test_recherche_trouve_un_risque_par_libelle(client, referent_sheq):
    _creer_risque(client, referent_sheq, "Chute depuis un pylône haubané")
    reponse = client.get("/api/v1/recherche", params={"q": "pylône haubané"}, headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    resultats = reponse.json()
    assert any(r["type"] == "risque" and "haubané" in r["libelle"] for r in resultats)


def test_recherche_refuse_un_terme_trop_court(client, referent_sheq):
    reponse = client.get("/api/v1/recherche", params={"q": "a"}, headers=_entete(referent_sheq))
    assert reponse.status_code == 422


def test_recherche_exige_une_authentification(client):
    assert client.get("/api/v1/recherche", params={"q": "test"}).status_code == 401


def test_recherche_ne_renvoie_a_un_technicien_que_ses_signalements(client, technicien, referent_sheq, site):
    """Les signalements suivent la restriction de visibilité de leur liste."""
    data = {
        "type": "situation_dangereuse",
        "site_id": str(site.id),
        "lieu": "Zone de recherche AAA",
        "description": "Terme unique zzztest",
        "anonyme": "false",
        "date_constat": "2026-04-15T08:00:00+00:00",
    }
    # Signalement du référent (le technicien ne doit pas le voir en recherche).
    client.post("/api/v1/signalements", headers=_entete(referent_sheq), data=data)

    res_tech = client.get("/api/v1/recherche", params={"q": "zzztest"}, headers=_entete(technicien)).json()
    assert all(r["type"] != "signalement" for r in res_tech)

    res_ref = client.get("/api/v1/recherche", params={"q": "zzztest"}, headers=_entete(referent_sheq)).json()
    assert any(r["type"] == "signalement" for r in res_ref)
