"""Tests du module Fiches de configuration (prompt 3.2, section 5.2.3 du CDC)."""
import io
import json
from datetime import date

from app.core.security import creer_access_token
from app.models.enums import MarqueEquipement, StatutEquipement
from app.models.equipement import Equipement


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _creer_equipement(db_session, site, marque, identity="BKO-AP-01", numero_serie="SN0001"):
    equipement = Equipement(
        identity=identity,
        marque=marque,
        modele="Modèle test",
        numero_serie=numero_serie,
        site_id=site.id,
        emplacement="Pylône 24 m",
        date_installation=date(2026, 1, 1),
        statut=StatutEquipement.EN_SERVICE,
    )
    db_session.add(equipement)
    db_session.commit()
    return equipement


def _champs_mikrotik(equipement_id, **overrides):
    champs = {
        "equipement_id": str(equipement_id),
        "type_intervention": "reconfiguration",
        "version_logicielle": "7.16.1",
        "parametres_reseau": json.dumps(
            {"adresse_ip_masque": "10.0.0.2/30", "passerelle": "10.0.0.1", "dns": "8.8.8.8"}
        ),
        "parametres_sansfil": json.dumps({"mode": "station bridge", "frequence": "5180 MHz / 20 MHz", "protocole": "nv2"}),
        "signal_dbm": "-58",
        "ccq_pourcent": "96",
    }
    champs.update(overrides)
    return champs


def test_creation_mikrotik_calcule_la_conformite(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK)
    reponse = client.post(
        "/api/v1/configurations", headers=_entete(technicien), data=_champs_mikrotik(equipement.id)
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["signal_conforme"] is True
    assert corps["ccq_conforme"] is True
    assert corps["reference"].startswith(f"ENR-SHEQ-{date.today().year}-")


def test_signal_hors_objectif_est_signale_non_conforme(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK)
    reponse = client.post(
        "/api/v1/configurations",
        headers=_entete(technicien),
        data=_champs_mikrotik(equipement.id, signal_dbm="-80", ccq_pourcent="40"),
    )
    corps = reponse.json()
    assert corps["signal_conforme"] is False
    assert corps["ccq_conforme"] is False


def test_reference_incrementee_a_chaque_creation(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK)
    r1 = client.post("/api/v1/configurations", headers=_entete(technicien), data=_champs_mikrotik(equipement.id)).json()
    r2 = client.post("/api/v1/configurations", headers=_entete(technicien), data=_champs_mikrotik(equipement.id)).json()
    n1 = int(r1["reference"].rsplit("-", 1)[-1])
    n2 = int(r2["reference"].rsplit("-", 1)[-1])
    assert n2 == n1 + 1


def test_rejette_un_champ_mot_de_passe_glisse_dans_les_parametres(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK)
    donnees = _champs_mikrotik(
        equipement.id,
        parametres_reseau=json.dumps({"adresse_ip_masque": "10.0.0.2/30", "mot_de_passe_admin": "secret123"}),
    )
    reponse = client.post("/api/v1/configurations", headers=_entete(technicien), data=donnees)
    assert reponse.status_code == 422


def test_grandstream_exige_serveur_sip_et_extension(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.GRANDSTREAM, identity="BKO-TEL-01", numero_serie="SN0002")
    donnees = {
        "equipement_id": str(equipement.id),
        "type_intervention": "installation",
        "parametres_reseau": json.dumps({"adresse_ip_masque": "10.0.1.5/24", "mode_ip": "statique"}),
    }
    reponse = client.post("/api/v1/configurations", headers=_entete(technicien), data=donnees)
    assert reponse.status_code == 422

    donnees["parametres_reseau"] = json.dumps(
        {"adresse_ip_masque": "10.0.1.5/24", "serveur_sip": "10.0.1.1", "extension": "1042"}
    )
    reponse_ok = client.post("/api/v1/configurations", headers=_entete(technicien), data=donnees)
    assert reponse_ok.status_code == 201
    # Grandstream n'a pas de volet sans fil : signal/CCQ restent "sans objet".
    corps = reponse_ok.json()
    assert corps["signal_conforme"] is None
    assert corps["ccq_conforme"] is None


def test_grandstream_rejette_un_volet_sans_fil(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.GRANDSTREAM, identity="BKO-TEL-02", numero_serie="SN0003")
    donnees = {
        "equipement_id": str(equipement.id),
        "type_intervention": "installation",
        "parametres_reseau": json.dumps({"serveur_sip": "10.0.1.1", "extension": "1042"}),
        "parametres_sansfil": json.dumps({"mode": "ap"}),
    }
    reponse = client.post("/api/v1/configurations", headers=_entete(technicien), data=donnees)
    assert reponse.status_code == 422


def test_ruijie_valide_vlan_ports_et_gestion_cloud(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.RUIJIE, identity="BKO-SW-01", numero_serie="SN0004")
    donnees = {
        "equipement_id": str(equipement.id),
        "type_intervention": "installation",
        "parametres_reseau": json.dumps({"vlan": "10 data / 20 voix", "ports": "1-24 access", "mode_gestion_cloud": "cloud"}),
    }
    reponse = client.post("/api/v1/configurations", headers=_entete(technicien), data=donnees)
    assert reponse.status_code == 201


def test_referent_sheq_ne_peut_pas_creer_une_configuration(client, referent_sheq, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK)
    reponse = client.post(
        "/api/v1/configurations", headers=_entete(referent_sheq), data=_champs_mikrotik(equipement.id)
    )
    assert reponse.status_code == 403


def test_immutabilite_une_correction_cree_une_nouvelle_fiche(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK)
    originale = client.post(
        "/api/v1/configurations", headers=_entete(technicien), data=_champs_mikrotik(equipement.id, signal_dbm="-60")
    ).json()

    correction = client.post(
        "/api/v1/configurations",
        headers=_entete(technicien),
        data=_champs_mikrotik(equipement.id, signal_dbm="-55"),
    ).json()

    assert correction["id"] != originale["id"]
    assert correction["reference"] != originale["reference"]

    relue_originale = client.get(f"/api/v1/configurations/{originale['id']}", headers=_entete(technicien)).json()
    assert relue_originale["signal_dbm"] == -60.0

    # Aucune route de modification n'existe pour cette entité.
    reponse_patch = client.patch(f"/api/v1/configurations/{originale['id']}", headers=_entete(technicien), json={})
    assert reponse_patch.status_code == 405
    reponse_delete = client.delete(f"/api/v1/configurations/{originale['id']}", headers=_entete(technicien))
    assert reponse_delete.status_code == 405


def test_nom_de_sauvegarde_conforme_est_accepte(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK, identity="BKO-AP-02", numero_serie="SN0005")
    date_intervention = "2026-09-06T10:00:00Z"
    nom_attendu = "BKO-AP-02-20260906.rsc"
    donnees = _champs_mikrotik(equipement.id, date_intervention=date_intervention)
    fichier = io.BytesIO(b"contenu rsc factice")

    reponse = client.post(
        "/api/v1/configurations",
        headers=_entete(technicien),
        data=donnees,
        files={"fichiers": (nom_attendu, fichier, "application/octet-stream")},
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert len(corps["fichiers_sauvegarde"]) == 1


def test_nom_de_sauvegarde_non_conforme_est_rejete(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK, identity="BKO-AP-03", numero_serie="SN0006")
    date_intervention = "2026-09-06T10:00:00Z"
    donnees = _champs_mikrotik(equipement.id, date_intervention=date_intervention)
    fichier = io.BytesIO(b"contenu rsc factice")

    reponse = client.post(
        "/api/v1/configurations",
        headers=_entete(technicien),
        data=donnees,
        files={"fichiers": ("sauvegarde_du_jour.rsc", fichier, "application/octet-stream")},
    )
    assert reponse.status_code == 400
    assert "BKO-AP-03-20260906" in reponse.json()["detail"]


def test_export_pdf_renvoie_un_document_pdf(client, technicien, site, db_session):
    equipement = _creer_equipement(db_session, site, MarqueEquipement.MIKROTIK, identity="BKO-AP-04", numero_serie="SN0007")
    creation = client.post(
        "/api/v1/configurations", headers=_entete(technicien), data=_champs_mikrotik(equipement.id)
    ).json()

    reponse = client.get(f"/api/v1/configurations/{creation['id']}/export-pdf", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert reponse.headers["content-type"] == "application/pdf"
    assert reponse.content[:4] == b"%PDF"
