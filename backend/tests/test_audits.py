"""Tests du module Audits (prompt 4.2, section 5.3.4 du CDC)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_referentiel_expose_les_22_exigences_reelles(client, technicien):
    reponse = client.get("/api/v1/audits/exigences", headers=_entete(technicien))
    assert reponse.status_code == 200
    exigences = reponse.json()
    assert len(exigences) == 22
    chapitres = {e["chapitre"] for e in exigences}
    assert chapitres == {
        "Contexte et leadership",
        "Planification",
        "Support",
        "Réalisation des activités",
        "Évaluation des performances",
        "Amélioration",
    }


def test_technicien_ne_peut_pas_creer_de_campagne(client, technicien):
    reponse = client.post("/api/v1/audits/campagnes", headers=_entete(technicien), json={})
    assert reponse.status_code == 403


def _coter_toutes_les_exigences(client, referent_sheq, campagne_id, valeur: int):
    exigences = client.get("/api/v1/audits/exigences", headers=_entete(referent_sheq)).json()
    cotations = [{"exigence_id": e["id"], "cotation": valeur} for e in exigences]
    return client.patch(f"/api/v1/audits/campagnes/{campagne_id}/cotations", headers=_entete(referent_sheq), json=cotations)


def test_score_maximal_est_le_double_du_nombre_d_exigences_cotees(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    exigences = client.get("/api/v1/audits/exigences", headers=_entete(referent_sheq)).json()

    # Une seule exigence cotée (2 = conforme) : score max = 2, pas 44.
    reponse = client.patch(
        f"/api/v1/audits/campagnes/{campagne['id']}/cotations",
        headers=_entete(referent_sheq),
        json=[{"exigence_id": exigences[0]["id"], "cotation": 2}],
    )
    assert reponse.status_code == 200

    detail = client.get(f"/api/v1/audits/campagnes/{campagne['id']}", headers=_entete(referent_sheq)).json()
    assert detail["score_total"] == 2
    assert detail["score_maximal"] == 2
    assert detail["taux_conformite_pourcent"] == 100.0


def test_cotation_toutes_conformes_donne_systeme_mature(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    _coter_toutes_les_exigences(client, referent_sheq, campagne["id"], 2)

    detail = client.get(f"/api/v1/audits/campagnes/{campagne['id']}", headers=_entete(referent_sheq)).json()
    assert detail["score_total"] == 44
    assert detail["score_maximal"] == 44
    assert detail["taux_conformite_pourcent"] == 100.0
    assert detail["interpretation"] == "Système mature"
    assert len(detail["score_par_chapitre"]) == 6


def test_cotation_hors_bornes_rejetee(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    exigences = client.get("/api/v1/audits/exigences", headers=_entete(referent_sheq)).json()
    reponse = client.patch(
        f"/api/v1/audits/campagnes/{campagne['id']}/cotations",
        headers=_entete(referent_sheq),
        json=[{"exigence_id": exigences[0]["id"], "cotation": 3}],
    )
    assert reponse.status_code == 422


def test_cotation_impossible_apres_cloture(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    client.post(f"/api/v1/audits/campagnes/{campagne['id']}/cloturer", headers=_entete(referent_sheq))

    exigences = client.get("/api/v1/audits/exigences", headers=_entete(referent_sheq)).json()
    reponse = client.patch(
        f"/api/v1/audits/campagnes/{campagne['id']}/cotations",
        headers=_entete(referent_sheq),
        json=[{"exigence_id": exigences[0]["id"], "cotation": 2}],
    )
    assert reponse.status_code == 409


def test_comparaison_entre_deux_campagnes_montre_l_evolution(client, referent_sheq):
    campagne_1 = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    _coter_toutes_les_exigences(client, referent_sheq, campagne_1["id"], 0)

    campagne_2 = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    _coter_toutes_les_exigences(client, referent_sheq, campagne_2["id"], 2)

    reponse = client.get(
        f"/api/v1/audits/comparaison?reference_id={campagne_1['id']}&comparee_id={campagne_2['id']}",
        headers=_entete(referent_sheq),
    )
    assert reponse.status_code == 200
    comparaison = reponse.json()
    assert comparaison["taux_reference_pourcent"] == 0.0
    assert comparaison["taux_compare_pourcent"] == 100.0
    assert comparaison["evolution_points"] == 100.0
    assert len(comparaison["par_chapitre"]) == 6
    for chapitre in comparaison["par_chapitre"]:
        assert chapitre["evolution_points"] == 100.0


def test_action_corrective_creee_a_partir_d_un_ecart(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    exigences = client.get("/api/v1/audits/exigences", headers=_entete(referent_sheq)).json()
    cotation = client.patch(
        f"/api/v1/audits/campagnes/{campagne['id']}/cotations",
        headers=_entete(referent_sheq),
        json=[{"exigence_id": exigences[0]["id"], "cotation": 0, "ecart": "Politique non affichée"}],
    ).json()[0]

    reponse = client.post(
        "/api/v1/actions",
        headers=_entete(referent_sheq),
        json={
            "libelle": "Afficher la politique SHEQ",
            "cotation_audit_id": cotation["id"],
            "type_mesure": "corrective",
            "responsable_id": referent_sheq.id,
            "echeance": "2027-01-01",
        },
    )
    assert reponse.status_code == 201
    assert reponse.json()["cotation_audit_id"] == cotation["id"]
