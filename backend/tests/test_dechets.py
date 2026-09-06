"""Tests du module Déchets (prompt 4.3, section 5.3.6 du CDC)."""
import io

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_technicien_ne_peut_pas_creer_de_dechet(client, technicien, site):
    reponse = client.post(
        "/api/v1/dechets",
        headers=_entete(technicien),
        json={"date": "2026-04-15", "type": "DEEE", "description": "Routeur HS", "quantite": "2 unités", "site_id": site.id, "filiere": "Repreneur agréé DEEE"},
    )
    assert reponse.status_code == 403


def test_creation_et_enlevement_avec_justificatif(client, referent_sheq, site):
    dechet = client.post(
        "/api/v1/dechets",
        headers=_entete(referent_sheq),
        json={
            "date": "2026-04-15",
            "type": "DEEE",
            "description": "Routeur HS + câbles",
            "quantite": "2 unités",
            "site_id": site.id,
            "filiere": "Repreneur agréé DEEE",
        },
    ).json()
    assert dechet["date_enlevement"] is None

    fichier = io.BytesIO(b"contenu factice")
    reponse = client.post(
        f"/api/v1/dechets/{dechet['id']}/enlevement",
        headers=_entete(referent_sheq),
        data={"date_enlevement": "2026-05-01"},
        files={"justificatif": ("bon_enlevement.jpg", fichier, "image/jpeg")},
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["date_enlevement"] == "2026-05-01"
    assert corps["justificatif"] is not None


def test_liste_ouverte_a_tout_utilisateur_authentifie(client, technicien, referent_sheq, site):
    client.post(
        "/api/v1/dechets",
        headers=_entete(referent_sheq),
        json={"date": "2026-04-15", "type": "Papier", "description": "Cartons", "quantite": "5 kg", "site_id": site.id, "filiere": "Recyclage local"},
    )
    reponse = client.get("/api/v1/dechets", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert len(reponse.json()) == 1
