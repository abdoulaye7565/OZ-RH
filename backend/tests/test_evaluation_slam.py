"""Tests du module SLAM (prompt 2.2)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_referentiel_expose_4_etapes_de_4_points(client, technicien):
    reponse = client.get("/api/v1/slam/referentiel", headers=_entete(technicien))
    assert reponse.status_code == 200
    etapes = reponse.json()
    assert len(etapes) == 4
    assert all(len(e["points"]) == 4 for e in etapes)
    assert [e["lettre"] for e in etapes] == ["S", "L", "A", "M"]


def test_go_avec_tous_les_points_valides_accepte(client, technicien):
    reponse = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[True] * 4] * 4, "decision": "GO"},
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["decision"] == "GO"
    assert corps["utilisateur_id"] == technicien.id


def test_go_avec_un_point_non_valide_refuse(client, technicien):
    """Équivalent serveur de "passage à l'étape suivante impossible tant que
    tout n'est pas validé" : le client ne peut pas non plus déclarer GO en
    contournant le stepper mobile."""
    etapes = [[True] * 4] * 4
    etapes[2][1] = False  # un seul point non coché, étape 3
    reponse = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": etapes, "decision": "GO"},
    )
    assert reponse.status_code == 422


def test_no_go_sans_tout_valider_accepte_avec_motif(client, technicien):
    """Une décision NO GO peut intervenir à n'importe quelle étape, sans avoir
    coché tous les points des étapes suivantes (règle 5.2.2)."""
    etapes = [[True] * 4, [True, False, False, False], [False] * 4, [False] * 4]
    reponse = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": etapes, "decision": "NO_GO", "motif": "Vent trop fort"},
    )
    assert reponse.status_code == 201
    assert reponse.json()["decision"] == "NO_GO"


def test_no_go_sans_motif_refuse(client, technicien):
    reponse = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[False] * 4] * 4, "decision": "NO_GO"},
    )
    assert reponse.status_code == 422


def test_forme_incorrecte_refusee(client, technicien):
    reponse = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[True, True, True]] * 4, "decision": "GO"},  # 3 points au lieu de 4
    )
    assert reponse.status_code == 422


def test_mes_evaluations_ne_montre_que_les_siennes(client, db_session, technicien, referent_sheq):
    client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[True] * 4] * 4, "decision": "GO"},
    )
    client.post(
        "/api/v1/slam",
        headers=_entete(referent_sheq),
        json={"etapes_validees": [[True] * 4] * 4, "decision": "GO"},
    )

    reponse = client.get("/api/v1/slam/mes-evaluations", headers=_entete(technicien))
    resultats = reponse.json()
    assert len(resultats) == 1
    assert resultats[0]["utilisateur_id"] == technicien.id


def test_aucune_route_de_suppression(client):
    reponse = client.delete("/api/v1/slam/1")
    assert reponse.status_code == 405
