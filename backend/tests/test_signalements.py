"""Tests du module Signalements (prompt 1.1)."""
import io
from datetime import datetime, timezone

from sqlalchemy import text

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _champs_formulaire(site, **overrides):
    donnees = {
        "type": "incident",
        "site_id": str(site.id),
        "lieu": "Pylône P12",
        "description": "Câble détendu constaté lors de la ronde.",
        "anonyme": "false",
        "date_constat": datetime.now(timezone.utc).isoformat(),
    }
    donnees.update(overrides)
    return donnees


def test_creation_attribue_une_reference_sig_annuelle(client, technicien, site):
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data=_champs_formulaire(site),
    )

    assert reponse.status_code == 201
    corps = reponse.json()
    annee = datetime.now(timezone.utc).year
    assert corps["reference"] == f"SIG-{annee}-001"
    assert corps["statut"] == "nouveau"


def test_deux_creations_incrementent_le_numero_de_sequence(client, technicien, site):
    r1 = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    r2 = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))

    annee = datetime.now(timezone.utc).year
    assert r1.json()["reference"] == f"SIG-{annee}-001"
    assert r2.json()["reference"] == f"SIG-{annee}-002"


def test_signalement_anonyme_ne_laisse_aucune_trace_de_son_auteur(client, db_session, technicien, site):
    """Test explicitement demandé par le prompt 1.1 : vérifie l'absence de trace en
    base BRUTE (pas seulement dans la réponse JSON), y compris cree_par_id qui
    vient de la classe de base commune et pourrait facilement être oublié."""
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data=_champs_formulaire(site, anonyme="true"),
    )
    assert reponse.status_code == 201
    assert reponse.json()["auteur_id"] is None

    signalement_id = reponse.json()["id"]

    ligne_brute = db_session.execute(
        text("SELECT auteur_id, cree_par_id, modifie_par_id FROM signalement WHERE id = :id"),
        {"id": signalement_id},
    ).one()
    assert ligne_brute.auteur_id is None
    assert ligne_brute.cree_par_id is None
    assert ligne_brute.modifie_par_id is None


def test_signalement_non_anonyme_reference_bien_son_auteur(client, db_session, technicien, site):
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data=_champs_formulaire(site, anonyme="false"),
    )
    corps = reponse.json()
    assert corps["auteur_id"] == technicien.id

    ligne_brute = db_session.execute(
        text("SELECT cree_par_id FROM signalement WHERE id = :id"), {"id": corps["id"]}
    ).one()
    assert ligne_brute.cree_par_id == technicien.id


def test_plus_de_cinq_photos_refuse(client, technicien, site):
    fichiers = [
        ("photos", (f"photo{i}.jpg", io.BytesIO(b"contenu-image"), "image/jpeg")) for i in range(6)
    ]
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data=_champs_formulaire(site),
        files=fichiers,
    )
    assert reponse.status_code == 400


def test_type_de_fichier_non_image_refuse(client, technicien, site):
    fichiers = [("photos", ("document.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf"))]
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data=_champs_formulaire(site),
        files=fichiers,
    )
    assert reponse.status_code == 400


def test_cinq_photos_valides_acceptees_et_stockees_hors_base(client, technicien, site, tmp_path, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))

    fichiers = [
        ("photos", (f"photo{i}.jpg", io.BytesIO(b"\xff\xd8\xff-contenu-jpeg-factice"), "image/jpeg"))
        for i in range(5)
    ]
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data=_champs_formulaire(site),
        files=fichiers,
    )
    assert reponse.status_code == 201
    photos = reponse.json()["photos"]
    assert len(photos) == 5
    for chemin_relatif in photos:
        assert (tmp_path / chemin_relatif).exists()


def test_transition_nouveau_vers_cloture_directe_refusee(client, technicien, referent_sheq, site):
    creation = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    signalement_id = creation.json()["id"]

    reponse = client.patch(
        f"/api/v1/signalements/{signalement_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "cloture"},
    )
    assert reponse.status_code == 409


def test_workflow_nominal_jusqu_a_cloture(client, technicien, referent_sheq, site):
    creation = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    signalement_id = creation.json()["id"]

    r1 = client.patch(
        f"/api/v1/signalements/{signalement_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_analyse"},
    )
    assert r1.status_code == 200

    r2 = client.patch(
        f"/api/v1/signalements/{signalement_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "actions_definies"},
    )
    assert r2.status_code == 200

    r3 = client.patch(
        f"/api/v1/signalements/{signalement_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "cloture"},
    )
    assert r3.status_code == 200
    assert r3.json()["statut"] == "cloture"


def test_transition_apres_cloture_refusee(client, technicien, referent_sheq, site):
    creation = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    signalement_id = creation.json()["id"]
    for statut in ("en_analyse", "cloture"):
        client.patch(
            f"/api/v1/signalements/{signalement_id}/statut",
            headers=_entete(referent_sheq),
            json={"statut": statut},
        )

    reponse = client.patch(
        f"/api/v1/signalements/{signalement_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_analyse"},
    )
    assert reponse.status_code == 409


def test_technicien_ne_peut_pas_changer_le_statut(client, technicien, site):
    creation = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    signalement_id = creation.json()["id"]

    reponse = client.patch(
        f"/api/v1/signalements/{signalement_id}/statut",
        headers=_entete(technicien),
        json={"statut": "en_analyse"},
    )
    assert reponse.status_code == 403


def test_technicien_ne_voit_que_ses_propres_signalements(client, db_session, technicien, referent_sheq, site):
    from app.models.enums import RoleUtilisateur
    from app.models.utilisateur import Utilisateur
    from app.core.security import hacher_mot_de_passe

    autre_technicien = Utilisateur(
        nom="Autre",
        prenom="Technicien",
        identifiant="autre.tech",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(autre_technicien)
    db_session.commit()

    client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    client.post("/api/v1/signalements", headers=_entete(autre_technicien), data=_champs_formulaire(site))

    reponse_technicien = client.get("/api/v1/signalements", headers=_entete(technicien))
    assert reponse_technicien.status_code == 200
    assert len(reponse_technicien.json()) == 1

    reponse_referent = client.get("/api/v1/signalements", headers=_entete(referent_sheq))
    assert reponse_referent.status_code == 200
    assert len(reponse_referent.json()) == 2


def test_lecture_d_un_signalement_qui_n_appartient_pas_a_l_appelant_renvoie_404(
    client, db_session, technicien, site
):
    from app.models.enums import RoleUtilisateur
    from app.models.utilisateur import Utilisateur
    from app.core.security import hacher_mot_de_passe

    autre_technicien = Utilisateur(
        nom="Autre",
        prenom="Technicien",
        identifiant="autre.tech2",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(autre_technicien)
    db_session.commit()

    creation = client.post("/api/v1/signalements", headers=_entete(autre_technicien), data=_champs_formulaire(site))
    signalement_id = creation.json()["id"]

    reponse = client.get(f"/api/v1/signalements/{signalement_id}", headers=_entete(technicien))
    assert reponse.status_code == 404


def test_filtre_par_statut(client, technicien, referent_sheq, site):
    creation = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    client.patch(
        f"/api/v1/signalements/{creation.json()['id']}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_analyse"},
    )

    reponse = client.get("/api/v1/signalements?statut=en_analyse", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    resultats = reponse.json()
    assert len(resultats) == 1
    assert resultats[0]["statut"] == "en_analyse"


def test_archivage_retire_le_signalement_de_la_liste(client, technicien, referent_sheq, site):
    creation = client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_formulaire(site))
    signalement_id = creation.json()["id"]

    reponse = client.post(f"/api/v1/signalements/{signalement_id}/archiver", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    assert reponse.json()["archive"] is True

    liste = client.get("/api/v1/signalements", headers=_entete(referent_sheq)).json()
    assert all(s["id"] != signalement_id for s in liste)


def test_aucune_route_de_suppression_n_existe(client):
    """CRUD sans suppression (règle transversale) : aucune méthode DELETE n'est
    exposée sur /signalements."""
    reponse = client.delete("/api/v1/signalements/1")
    assert reponse.status_code == 405


def test_creation_sans_authentification_refusee(client, site):
    reponse = client.post("/api/v1/signalements", data=_champs_formulaire(site))
    assert reponse.status_code == 401
