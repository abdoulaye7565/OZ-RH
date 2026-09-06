"""Tests du module Inspections (prompt 2.4)."""
from sqlalchemy import select

from app.core.security import creer_access_token
from app.models.point_checklist import PointChecklist


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _points_pour(db_session, type_inspection, nombre):
    requete = (
        select(PointChecklist)
        .where(PointChecklist.type_inspection == type_inspection, PointChecklist.archive.is_(False))
        .order_by(PointChecklist.ordre)
        .limit(nombre)
    )
    return list(db_session.scalars(requete))


def test_referentiel_locaux_contient_15_points_reels(client, technicien):
    reponse = client.get("/api/v1/points-checklist?type_inspection=locaux", headers=_entete(technicien))
    assert reponse.status_code == 200
    points = reponse.json()
    assert len(points) == 15
    assert points[0]["libelle"] == "Les circulations et issues sont dégagées et non encombrées"


def test_referentiel_installations_a_des_categories(client, technicien):
    reponse = client.get("/api/v1/points-checklist?type_inspection=installations", headers=_entete(technicien))
    points = reponse.json()
    assert len(points) == 25
    assert points[0]["categorie"] == "A. Structure porteuse et fixations"


def test_creation_inspection_avec_cotations(client, db_session, technicien, site):
    points_ref = _points_pour(db_session, "locaux", 3)
    reponse = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "locaux",
            "site_id": site.id,
            "points": [
                {"point_checklist_id": points_ref[0].id, "cotation": "C"},
                {"point_checklist_id": points_ref[1].id, "cotation": "NC", "observation": "Sol glissant"},
                {"point_checklist_id": points_ref[2].id, "cotation": "SO"},
            ],
        },
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["statut"] == "en_cours"
    assert len(corps["points"]) == 3
    assert corps["points"][0]["libelle"] == points_ref[0].libelle


def test_taux_conformite_exclut_les_sans_objet(client, db_session, technicien, site):
    """Cas de test explicitement demandé par le prompt 2.4."""
    points_ref = _points_pour(db_session, "incendie", 4)
    reponse = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "incendie",
            "site_id": site.id,
            "points": [
                {"point_checklist_id": points_ref[0].id, "cotation": "C"},
                {"point_checklist_id": points_ref[1].id, "cotation": "C"},
                {"point_checklist_id": points_ref[2].id, "cotation": "NC"},
                {"point_checklist_id": points_ref[3].id, "cotation": "SO"},
            ],
        },
    )
    corps = reponse.json()
    # 2 conformes, 1 non conforme, 1 sans objet exclu -> 2 / (2 + 1) = 0.666...
    assert abs(corps["taux_conformite"] - (2 / 3)) < 0.001


def test_taux_conformite_uniquement_sans_objet_est_nul(client, db_session, technicien, site):
    points_ref = _points_pour(db_session, "incendie", 2)
    reponse = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "incendie",
            "site_id": site.id,
            "points": [
                {"point_checklist_id": points_ref[0].id, "cotation": "SO"},
                {"point_checklist_id": points_ref[1].id, "cotation": "SO"},
            ],
        },
    )
    assert reponse.json()["taux_conformite"] is None


def test_point_hors_modele_refuse(client, db_session, technicien, site):
    point_incendie = _points_pour(db_session, "incendie", 1)[0]
    reponse = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "locaux",
            "site_id": site.id,
            "points": [{"point_checklist_id": point_incendie.id, "cotation": "C"}],
        },
    )
    assert reponse.status_code == 400


def test_cloture_genere_une_action_par_point_non_conforme(client, db_session, technicien, site):
    """Cas de test explicitement demandé par le prompt 2.4."""
    points_ref = _points_pour(db_session, "electricite", 4)
    creation = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "electricite",
            "site_id": site.id,
            "points": [
                {"point_checklist_id": points_ref[0].id, "cotation": "C"},
                {"point_checklist_id": points_ref[1].id, "cotation": "NC", "observation": "Câble dénudé"},
                {"point_checklist_id": points_ref[2].id, "cotation": "NC", "observation": "Multiprise surchargée"},
                {"point_checklist_id": points_ref[3].id, "cotation": "SO"},
            ],
        },
    ).json()

    reponse = client.post(f"/api/v1/inspections/{creation['id']}/cloturer", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "cloturee"

    actions = client.get(f"/api/v1/inspections/{creation['id']}/actions-generees", headers=_entete(technicien)).json()
    assert len(actions) == 2
    libelles = {a["libelle"] for a in actions}
    # Le libellé de l'action vient du POINT de checklist, pas de l'observation
    # saisie par l'inspecteur (l'observation reste sur le point de l'inspection).
    assert all("Câble dénudé" not in l and "Multiprise surchargée" not in l for l in libelles)
    assert all(a["inspection_id"] == creation["id"] for a in actions)
    assert all(a["statut"] == "ouverte" for a in actions)


def test_aucune_action_generee_si_tout_conforme(client, db_session, technicien, site):
    points_ref = _points_pour(db_session, "electricite", 2)
    creation = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "electricite",
            "site_id": site.id,
            "points": [
                {"point_checklist_id": points_ref[0].id, "cotation": "C"},
                {"point_checklist_id": points_ref[1].id, "cotation": "C"},
            ],
        },
    ).json()

    client.post(f"/api/v1/inspections/{creation['id']}/cloturer", headers=_entete(technicien))
    actions = client.get(f"/api/v1/inspections/{creation['id']}/actions-generees", headers=_entete(technicien)).json()
    assert len(actions) == 0


def test_inspection_cloturee_n_est_plus_modifiable(client, db_session, technicien, site):
    points_ref = _points_pour(db_session, "locaux", 1)
    creation = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "locaux",
            "site_id": site.id,
            "points": [{"point_checklist_id": points_ref[0].id, "cotation": "C"}],
        },
    ).json()
    client.post(f"/api/v1/inspections/{creation['id']}/cloturer", headers=_entete(technicien))

    reponse = client.patch(
        f"/api/v1/inspections/{creation['id']}/points",
        headers=_entete(technicien),
        json={"points": [{"point_checklist_id": points_ref[0].id, "cotation": "NC"}]},
    )
    assert reponse.status_code == 409


def test_cloturer_deux_fois_refuse(client, db_session, technicien, site):
    points_ref = _points_pour(db_session, "locaux", 1)
    creation = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "locaux",
            "site_id": site.id,
            "points": [{"point_checklist_id": points_ref[0].id, "cotation": "C"}],
        },
    ).json()
    client.post(f"/api/v1/inspections/{creation['id']}/cloturer", headers=_entete(technicien))

    reponse = client.post(f"/api/v1/inspections/{creation['id']}/cloturer", headers=_entete(technicien))
    assert reponse.status_code == 409


def test_mise_a_jour_points_avant_cloture_autorisee(client, db_session, technicien, site):
    points_ref = _points_pour(db_session, "locaux", 1)
    creation = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "locaux",
            "site_id": site.id,
            "points": [{"point_checklist_id": points_ref[0].id, "cotation": "C"}],
        },
    ).json()

    reponse = client.patch(
        f"/api/v1/inspections/{creation['id']}/points",
        headers=_entete(technicien),
        json={"points": [{"point_checklist_id": points_ref[0].id, "cotation": "NC", "observation": "Corrigé"}]},
    )
    assert reponse.status_code == 200
    assert reponse.json()["points"][0]["cotation"] == "NC"


def test_point_archive_ne_peut_plus_etre_utilise(client, db_session, referent_sheq, technicien, site):
    point = PointChecklist(type_inspection="locaux", ordre=999, libelle="Point de test à archiver")
    db_session.add(point)
    db_session.commit()

    client.post(f"/api/v1/points-checklist/{point.id}/archiver", headers=_entete(referent_sheq))

    reponse = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={"modele": "locaux", "site_id": site.id, "points": [{"point_checklist_id": point.id, "cotation": "C"}]},
    )
    assert reponse.status_code == 400


def test_technicien_ne_peut_pas_gerer_le_referentiel(client, technicien):
    reponse = client.post(
        "/api/v1/points-checklist",
        headers=_entete(technicien),
        json={"type_inspection": "locaux", "ordre": 100, "libelle": "Nouveau point"},
    )
    assert reponse.status_code == 403


def test_aucune_route_de_suppression(client):
    reponse = client.delete("/api/v1/inspections/1")
    assert reponse.status_code == 405
