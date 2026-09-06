"""Tests du module Visiteurs (prompt 4.3, section 5.3.6 du CDC)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_enregistrement_refuse_sans_lecture_des_consignes(client, technicien):
    reponse = client.post(
        "/api/v1/visiteurs",
        headers=_entete(technicien),
        json={"nom": "Jean Dupont", "societe": "ACME", "motif": "Livraison", "consignes_lues": False},
    )
    assert reponse.status_code == 422


def test_enregistrement_avec_consignes_lues_reussit(client, technicien):
    reponse = client.post(
        "/api/v1/visiteurs",
        headers=_entete(technicien),
        json={"nom": "Jean Dupont", "societe": "ACME", "motif": "Livraison", "consignes_lues": True},
    )
    assert reponse.status_code == 201
    assert reponse.json()["present"] is True


def test_liste_des_presents_utilisable_pour_evacuation(client, technicien):
    v1 = client.post(
        "/api/v1/visiteurs",
        headers=_entete(technicien),
        json={"nom": "Présent", "motif": "X", "consignes_lues": True},
    ).json()
    v2 = client.post(
        "/api/v1/visiteurs",
        headers=_entete(technicien),
        json={"nom": "Parti", "motif": "Y", "consignes_lues": True},
    ).json()
    client.post(f"/api/v1/visiteurs/{v2['id']}/depart", headers=_entete(technicien))

    presents = client.get("/api/v1/visiteurs/presents", headers=_entete(technicien)).json()
    ids_presents = [v["id"] for v in presents]
    assert v1["id"] in ids_presents
    assert v2["id"] not in ids_presents


def test_depart_deja_enregistre_est_refuse(client, technicien):
    visiteur = client.post(
        "/api/v1/visiteurs",
        headers=_entete(technicien),
        json={"nom": "X", "motif": "Y", "consignes_lues": True},
    ).json()
    client.post(f"/api/v1/visiteurs/{visiteur['id']}/depart", headers=_entete(technicien))
    reponse = client.post(f"/api/v1/visiteurs/{visiteur['id']}/depart", headers=_entete(technicien))
    assert reponse.status_code == 409
