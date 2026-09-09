"""Tests du module Coffre-fort (CDC section 5.2.4)."""
from datetime import date

import pytest

from app.core.security import creer_access_token
from app.models.equipement import Equipement


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


@pytest.fixture()
def equipement(db_session, site, responsable):
    e = Equipement(
        identity="BKO-TEST-01",
        marque="MikroTik",
        modele="hAP ac2",
        numero_serie="SN-TEST-001",
        site_id=site.id,
        emplacement="Local technique",
        date_installation=date(2026, 1, 1),
        statut="en_service",
        cree_par_id=responsable.id,
    )
    db_session.add(e)
    db_session.commit()
    return e


def _creer_secret(client, responsable, **overrides):
    corps = {
        "libelle": "Accès admin routeur",
        "type_acces": "administration",
        "identifiant": "admin",
        "valeur": "MotDePasseInitial!42",
        "role_requis": "technicien",
    }
    corps.update(overrides)
    return client.post("/api/v1/secrets", headers=_entete(responsable), json=corps)


def test_responsable_peut_creer_un_secret(client, responsable):
    reponse = _creer_secret(client, responsable)
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["libelle"] == "Accès admin routeur"
    assert "valeur" not in corps
    assert "valeur_chiffree" not in corps


def test_technicien_ne_peut_pas_creer_de_secret(client, technicien):
    reponse = _creer_secret(client, technicien)
    assert reponse.status_code == 403


def test_referent_sheq_ne_peut_pas_creer_de_secret(client, referent_sheq):
    reponse = _creer_secret(client, referent_sheq)
    assert reponse.status_code == 403


def test_role_requis_invalide_refuse(client, responsable):
    reponse = _creer_secret(client, responsable, role_requis="referent_sheq")
    assert reponse.status_code == 422
    reponse = _creer_secret(client, responsable, role_requis="collaborateur")
    assert reponse.status_code == 422


def test_liste_ne_contient_jamais_la_valeur(client, responsable):
    _creer_secret(client, responsable, valeur="SecretJamaisExpose!99")
    reponse = client.get("/api/v1/secrets", headers=_entete(responsable))
    assert reponse.status_code == 200
    for s in reponse.json():
        assert "valeur" not in s
        assert "valeur_chiffree" not in s


def test_consultation_renvoie_la_vraie_valeur_et_journalise(client, db_session, responsable):
    secret = _creer_secret(client, responsable, valeur="ValeurAConsulter!7").json()

    reponse = client.post(f"/api/v1/secrets/{secret['id']}/consulter", headers=_entete(responsable))
    assert reponse.status_code == 200
    assert reponse.json()["valeur"] == "ValeurAConsulter!7"

    journal = client.get(f"/api/v1/secrets/{secret['id']}/journal", headers=_entete(responsable)).json()
    actions = [j["action"] for j in journal]
    assert "creation" in actions
    assert "consultation" in actions
    assert all(j["utilisateur_id"] == responsable.id for j in journal)


def test_technicien_ne_voit_pas_un_secret_reserve_au_responsable(client, technicien, responsable):
    secret = _creer_secret(client, responsable, role_requis="responsable").json()

    liste = client.get("/api/v1/secrets", headers=_entete(technicien)).json()
    assert secret["id"] not in [s["id"] for s in liste]

    fiche = client.get(f"/api/v1/secrets/{secret['id']}", headers=_entete(technicien))
    assert fiche.status_code == 404

    consultation = client.post(f"/api/v1/secrets/{secret['id']}/consulter", headers=_entete(technicien))
    assert consultation.status_code == 404


def test_technicien_voit_et_consulte_un_secret_qui_lui_est_ouvert(client, technicien, responsable):
    secret = _creer_secret(client, responsable, role_requis="technicien", valeur="OuvertAuTechnicien!1").json()

    liste = client.get("/api/v1/secrets", headers=_entete(technicien)).json()
    assert secret["id"] in [s["id"] for s in liste]

    consultation = client.post(f"/api/v1/secrets/{secret['id']}/consulter", headers=_entete(technicien))
    assert consultation.status_code == 200
    assert consultation.json()["valeur"] == "OuvertAuTechnicien!1"


def test_referent_sheq_n_a_jamais_acces_meme_a_un_secret_technicien(client, referent_sheq, responsable):
    """Règle 5.2.4 explicite : "l'accès au coffre-fort n'est pas accordé par
    défaut au référent SHEQ, dont la fonction ne le justifie pas" — vérifié
    même sur le secret le moins restrictif (role_requis=technicien)."""
    secret = _creer_secret(client, responsable, role_requis="technicien").json()

    liste = client.get("/api/v1/secrets", headers=_entete(referent_sheq)).json()
    assert liste == []

    consultation = client.post(f"/api/v1/secrets/{secret['id']}/consulter", headers=_entete(referent_sheq))
    assert consultation.status_code == 404


def test_collaborateur_n_a_jamais_acces(client, db_session, site, mot_de_passe_clair, responsable):
    from app.core.security import hacher_mot_de_passe
    from app.models.utilisateur import Utilisateur

    collaborateur = Utilisateur(
        nom="Collab",
        prenom="Test",
        identifiant="c.test",
        mot_de_passe=hacher_mot_de_passe(mot_de_passe_clair),
        role="collaborateur",
        site_id=site.id,
    )
    db_session.add(collaborateur)
    db_session.commit()

    secret = _creer_secret(client, responsable, role_requis="technicien").json()
    liste = client.get("/api/v1/secrets", headers=_entete(collaborateur)).json()
    assert liste == []


def test_administrateur_voit_tout(client, administrateur, responsable):
    _creer_secret(client, responsable, role_requis="technicien")
    _creer_secret(client, responsable, role_requis="responsable", libelle="Secret responsable")
    _creer_secret(client, responsable, role_requis="administrateur", libelle="Secret admin")

    liste = client.get("/api/v1/secrets", headers=_entete(administrateur)).json()
    assert len(liste) == 3


def test_modification_change_la_valeur_dechiffree(client, responsable):
    secret = _creer_secret(client, responsable, valeur="AncienneValeur!1").json()

    reponse = client.patch(
        f"/api/v1/secrets/{secret['id']}", headers=_entete(responsable), json={"valeur": "NouvelleValeur!2"}
    )
    assert reponse.status_code == 200

    consultation = client.post(f"/api/v1/secrets/{secret['id']}/consulter", headers=_entete(responsable))
    assert consultation.json()["valeur"] == "NouvelleValeur!2"


def test_archivage_retire_le_secret_de_la_liste_mais_garde_le_journal(client, responsable):
    secret = _creer_secret(client, responsable).json()
    client.post(f"/api/v1/secrets/{secret['id']}/consulter", headers=_entete(responsable))

    reponse = client.post(f"/api/v1/secrets/{secret['id']}/archiver", headers=_entete(responsable))
    assert reponse.status_code == 200
    assert reponse.json()["archive"] is True

    liste = client.get("/api/v1/secrets", headers=_entete(responsable)).json()
    assert secret["id"] not in [s["id"] for s in liste]

    journal = client.get(f"/api/v1/secrets/{secret['id']}/journal", headers=_entete(responsable)).json()
    assert len(journal) >= 2  # création + consultation, toujours là après archivage


def test_secret_rattache_a_un_equipement_reel(client, responsable, equipement):
    reponse = _creer_secret(client, responsable, equipement_id=equipement.id)
    assert reponse.status_code == 201
    assert reponse.json()["equipement_id"] == equipement.id


def test_secret_rattache_a_un_equipement_inexistant_refuse(client, responsable):
    reponse = _creer_secret(client, responsable, equipement_id=999999)
    assert reponse.status_code == 404


def test_generation_mot_de_passe_respecte_la_longueur(client, responsable):
    reponse = client.post(
        "/api/v1/secrets/generer-mot-de-passe", headers=_entete(responsable), json={"longueur": 24, "inclure_symboles": True}
    )
    assert reponse.status_code == 200
    mdp = reponse.json()["mot_de_passe"]
    assert len(mdp) == 24
    assert any(c.isalpha() for c in mdp)
    assert any(c.isdigit() for c in mdp)


def test_generation_mot_de_passe_sans_symboles(client, responsable):
    reponse = client.post(
        "/api/v1/secrets/generer-mot-de-passe", headers=_entete(responsable), json={"longueur": 16, "inclure_symboles": False}
    )
    mdp = reponse.json()["mot_de_passe"]
    assert all(c.isalnum() for c in mdp)


def test_technicien_ne_peut_pas_generer_de_mot_de_passe(client, technicien):
    reponse = client.post(
        "/api/v1/secrets/generer-mot-de-passe", headers=_entete(technicien), json={"longueur": 16}
    )
    assert reponse.status_code == 403


def test_technicien_ne_peut_pas_consulter_le_journal(client, technicien, responsable):
    secret = _creer_secret(client, responsable, role_requis="technicien").json()
    reponse = client.get(f"/api/v1/secrets/{secret['id']}/journal", headers=_entete(technicien))
    assert reponse.status_code == 403


def test_responsable_ne_peut_pas_consulter_le_journal_d_un_secret_reserve_a_l_administrateur(
    client, administrateur, responsable
):
    """Revue de sécurité du 2026-09-08 : la route journal appliquait bien le
    rôle global (responsable/administrateur gèrent le coffre-fort) mais pas
    la visibilité par secret (`role_requis`) — un responsable pouvait donc
    lire le journal d'un secret qu'il ne voit ni dans sa liste ni sur sa
    fiche, en devinant simplement son id. Même secret qu'aucune des deux
    autres routes ne lui montre : le journal doit se comporter pareil."""
    secret = _creer_secret(client, administrateur, role_requis="administrateur").json()

    fiche = client.get(f"/api/v1/secrets/{secret['id']}", headers=_entete(responsable))
    assert fiche.status_code == 404

    journal = client.get(f"/api/v1/secrets/{secret['id']}/journal", headers=_entete(responsable))
    assert journal.status_code == 404

    # L'administrateur, lui, voit toujours le journal du même secret.
    journal_admin = client.get(f"/api/v1/secrets/{secret['id']}/journal", headers=_entete(administrateur))
    assert journal_admin.status_code == 200


def test_secret_jamais_stocke_en_clair_en_base(client, db_session, responsable):
    reponse = _creer_secret(client, responsable, valeur="JamaisEnClairEnBase!5")
    secret_id = reponse.json()["id"]

    from app.models.secret import Secret

    ligne = db_session.get(Secret, secret_id)
    assert b"JamaisEnClairEnBase" not in ligne.valeur_chiffree


def test_aucune_route_de_suppression(client):
    reponse = client.delete("/api/v1/secrets/1")
    assert reponse.status_code == 405


def test_aucune_route_de_suppression_du_journal(client):
    reponse = client.delete("/api/v1/secrets/1/journal")
    assert reponse.status_code == 405
