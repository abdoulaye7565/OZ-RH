"""Tests de la gestion des sites (section 5.2.3 du CDC).

Ajout du 2026-09-10 (retour direct de l'utilisateur : « on a un seul site
alors que nous intervenons sur plusieurs sites ») : création / modification /
archivage réservés à l'administrateur, consultation ouverte à tous.
"""
from datetime import date

from app.core.security import creer_access_token
from app.models.enums import MarqueEquipement, StatutEquipement
from app.models.equipement import Equipement


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_administrateur_cree_un_site(client, administrateur):
    reponse = client.post(
        "/api/v1/sites",
        headers=_entete(administrateur),
        json={"nom": "Antenne Kayes", "type": "client", "adresse": "Route de Médine"},
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["nom"] == "Antenne Kayes"
    assert corps["type"] == "client"

    liste = client.get("/api/v1/sites", headers=_entete(administrateur)).json()
    assert any(s["nom"] == "Antenne Kayes" for s in liste)


def test_nom_vide_refuse(client, administrateur):
    reponse = client.post(
        "/api/v1/sites",
        headers=_entete(administrateur),
        json={"nom": "   ", "type": "client"},
    )
    assert reponse.status_code == 422


def test_technicien_ne_peut_pas_creer_de_site(client, technicien):
    reponse = client.post(
        "/api/v1/sites",
        headers=_entete(technicien),
        json={"nom": "Antenne Ségou", "type": "client"},
    )
    assert reponse.status_code == 403


def test_technicien_peut_lister_les_sites(client, technicien, site):
    reponse = client.get("/api/v1/sites", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert any(s["id"] == site.id for s in reponse.json())


def test_modification_partielle_d_un_site(client, administrateur, site):
    reponse = client.patch(
        f"/api/v1/sites/{site.id}",
        headers=_entete(administrateur),
        json={"adresse": "Hamdallaye ACI 2000"},
    )
    assert reponse.status_code == 200
    assert reponse.json()["adresse"] == "Hamdallaye ACI 2000"
    assert reponse.json()["nom"] == site.nom  # inchangé


def test_archivage_retire_le_site_de_la_liste(client, administrateur):
    cree = client.post(
        "/api/v1/sites",
        headers=_entete(administrateur),
        json={"nom": "Site temporaire", "type": "client"},
    ).json()

    reponse = client.post(f"/api/v1/sites/{cree['id']}/archiver", headers=_entete(administrateur))
    assert reponse.status_code == 200

    liste = client.get("/api/v1/sites", headers=_entete(administrateur)).json()
    assert all(s["id"] != cree["id"] for s in liste)


def test_archivage_refuse_si_equipement_encore_rattache(client, db_session, administrateur):
    cree = client.post(
        "/api/v1/sites",
        headers=_entete(administrateur),
        json={"nom": "Site avec matériel", "type": "client"},
    ).json()
    db_session.add(
        Equipement(
            identity="KAY-AP-01",
            marque=MarqueEquipement.MIKROTIK,
            modele="hAP ac2",
            numero_serie="SN-KAY-001",
            site_id=cree["id"],
            emplacement="Local technique",
            date_installation=date(2026, 1, 1),
            statut=StatutEquipement.EN_SERVICE,
        )
    )
    db_session.commit()

    reponse = client.post(f"/api/v1/sites/{cree['id']}/archiver", headers=_entete(administrateur))
    assert reponse.status_code == 409
    assert "équipement" in reponse.json()["detail"].lower()


def test_aucune_route_de_suppression(client, administrateur, site):
    assert client.delete(f"/api/v1/sites/{site.id}", headers=_entete(administrateur)).status_code == 405
