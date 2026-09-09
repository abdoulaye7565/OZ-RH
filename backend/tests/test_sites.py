"""Tests de la route de consultation des sites (résolution de site_id en écran)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_lister_sites_ouvert_a_tout_authentifie(client, technicien, site):
    reponse = client.get("/api/v1/sites", headers=_entete(technicien))
    assert reponse.status_code == 200
    noms = [s["nom"] for s in reponse.json()]
    assert site.nom in noms


def test_lister_sites_sans_jeton_refuse(client):
    reponse = client.get("/api/v1/sites")
    assert reponse.status_code == 401
