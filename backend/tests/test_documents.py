"""Tests du module Documents (prompt 4.3, section 5.3.5 du CDC)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _creer(client, referent_sheq, **overrides):
    donnees = {"reference": "PRO-SHEQ-004", "intitule": "Maîtrise documentaire", "niveau": "3"}
    donnees.update(overrides)
    return client.post("/api/v1/documents", headers=_entete(referent_sheq), data=donnees)


def test_technicien_ne_peut_pas_creer_de_document(client, technicien):
    reponse = _creer(client, technicien)
    assert reponse.status_code == 403


def test_document_en_approbation_est_invisible_aux_autres(client, referent_sheq, technicien):
    doc = _creer(client, referent_sheq).json()
    client.post(f"/api/v1/documents/{doc['id']}/soumettre-approbation", headers=_entete(referent_sheq))

    liste_technicien = client.get("/api/v1/documents", headers=_entete(technicien)).json()
    assert doc["id"] not in [d["id"] for d in liste_technicien]

    reponse_detail = client.get(f"/api/v1/documents/{doc['id']}", headers=_entete(technicien))
    assert reponse_detail.status_code == 404

    # Mais le référent SHEQ (rédacteur) le voit toujours.
    liste_referent = client.get("/api/v1/documents", headers=_entete(referent_sheq)).json()
    assert doc["id"] in [d["id"] for d in liste_referent]


def test_approbation_rend_le_document_visible_de_tous(client, referent_sheq, technicien, responsable):
    doc = _creer(client, referent_sheq).json()
    client.post(f"/api/v1/documents/{doc['id']}/soumettre-approbation", headers=_entete(referent_sheq))
    reponse = client.post(f"/api/v1/documents/{doc['id']}/approuver", headers=_entete(responsable))
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "en_vigueur"

    liste_technicien = client.get("/api/v1/documents", headers=_entete(technicien)).json()
    assert doc["id"] in [d["id"] for d in liste_technicien]


def test_referent_sheq_ne_peut_pas_approuver_lui_meme(client, referent_sheq):
    doc = _creer(client, referent_sheq).json()
    client.post(f"/api/v1/documents/{doc['id']}/soumettre-approbation", headers=_entete(referent_sheq))
    reponse = client.post(f"/api/v1/documents/{doc['id']}/approuver", headers=_entete(referent_sheq))
    assert reponse.status_code == 403


def test_nouvelle_version_archive_automatiquement_la_precedente(client, referent_sheq, responsable):
    doc_v1 = _creer(client, referent_sheq).json()
    client.post(f"/api/v1/documents/{doc_v1['id']}/soumettre-approbation", headers=_entete(referent_sheq))
    client.post(f"/api/v1/documents/{doc_v1['id']}/approuver", headers=_entete(responsable))

    doc_v2 = client.post(f"/api/v1/documents/{doc_v1['id']}/nouvelle-version", headers=_entete(referent_sheq)).json()
    assert doc_v2["version"] == "02"
    assert doc_v2["statut"] == "brouillon"

    client.post(f"/api/v1/documents/{doc_v2['id']}/soumettre-approbation", headers=_entete(referent_sheq))
    client.post(f"/api/v1/documents/{doc_v2['id']}/approuver", headers=_entete(responsable))

    v1_relu = client.get(f"/api/v1/documents/{doc_v1['id']}", headers=_entete(referent_sheq)).json()
    v2_relu = client.get(f"/api/v1/documents/{doc_v2['id']}", headers=_entete(referent_sheq)).json()
    assert v1_relu["statut"] == "archive"
    assert v2_relu["statut"] == "en_vigueur"


def test_accuse_lecture_idempotent(client, referent_sheq, technicien, responsable):
    doc = _creer(client, referent_sheq).json()
    client.post(f"/api/v1/documents/{doc['id']}/soumettre-approbation", headers=_entete(referent_sheq))
    client.post(f"/api/v1/documents/{doc['id']}/approuver", headers=_entete(responsable))

    r1 = client.post(f"/api/v1/documents/{doc['id']}/accuser-lecture", headers=_entete(technicien)).json()
    r2 = client.post(f"/api/v1/documents/{doc['id']}/accuser-lecture", headers=_entete(technicien)).json()
    assert len(r1["accuses_lecture"]) == 1
    assert len(r2["accuses_lecture"]) == 1


def test_alerte_revue_detecte_une_echeance_proche(client, referent_sheq, responsable):
    from datetime import date, timedelta

    doc = _creer(client, referent_sheq, date_revue=str(date.today() + timedelta(days=10))).json()
    client.post(f"/api/v1/documents/{doc['id']}/soumettre-approbation", headers=_entete(referent_sheq))
    client.post(f"/api/v1/documents/{doc['id']}/approuver", headers=_entete(responsable))

    reponse = client.get("/api/v1/documents/alertes-revue", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    assert len(reponse.json()) == 1
