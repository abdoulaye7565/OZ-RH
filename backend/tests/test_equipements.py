"""Tests du module Parc d'équipements (prompt 3.1, section 5.2.3 du CDC)."""
import io
from datetime import date, datetime, timezone

from app.core.security import creer_access_token
from app.models.configuration import Configuration
from app.models.enums import (
    CotationPoint,
    StatutSignalement,
    TypeInspection,
    TypeIntervention,
    TypeSignalement,
    TypeSite,
)
from app.models.inspection import Inspection
from app.models.signalement import Signalement
from app.models.site import Site


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _donnees_equipement(site, **overrides):
    donnees = {
        "identity": "CLA-ST-01",
        "marque": "MikroTik",
        "modele": "LHG 5",
        "numero_serie": "SN0001",
        "site_id": site.id,
        "emplacement": "Pylône 24 m",
        "date_installation": str(date(2026, 3, 1)),
    }
    donnees.update(overrides)
    return donnees


def test_creation_normalise_lidentity_en_majuscules(client, technicien, site):
    reponse = client.post(
        "/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site, identity="cla-st-01")
    )
    assert reponse.status_code == 201
    assert reponse.json()["identity"] == "CLA-ST-01"


def test_creation_rejette_un_format_didentity_invalide(client, technicien, site):
    reponse = client.post(
        "/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site, identity="PasBonFormat")
    )
    assert reponse.status_code == 422


def test_creation_rejette_une_identity_deja_utilisee(client, technicien, site):
    client.post("/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site))
    reponse = client.post(
        "/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site, numero_serie="SN9999")
    )
    assert reponse.status_code == 409


def test_creation_rejette_un_numero_de_serie_deja_utilise(client, technicien, site):
    client.post("/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site))
    reponse = client.post(
        "/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site, identity="CLA-ST-02")
    )
    assert reponse.status_code == 409


def test_referent_sheq_ne_peut_pas_creer_un_equipement(client, referent_sheq, site):
    reponse = client.post(
        "/api/v1/equipements", headers=_entete(referent_sheq), json=_donnees_equipement(site)
    )
    assert reponse.status_code == 403


def test_administrateur_peut_creer_un_equipement(client, administrateur, site):
    reponse = client.post(
        "/api/v1/equipements", headers=_entete(administrateur), json=_donnees_equipement(site)
    )
    assert reponse.status_code == 201


def test_recherche_multicritere(client, technicien, db_session):
    site_a = Site(nom="Client A", type=TypeSite.CLIENT)
    site_b = Site(nom="Client B", type=TypeSite.CLIENT)
    db_session.add_all([site_a, site_b])
    db_session.commit()

    client.post(
        "/api/v1/equipements",
        headers=_entete(technicien),
        json=_donnees_equipement(site_a, identity="CLA-ST-01", numero_serie="SN0001", marque="MikroTik"),
    )
    client.post(
        "/api/v1/equipements",
        headers=_entete(technicien),
        json=_donnees_equipement(site_b, identity="CLB-AP-01", numero_serie="SN0002", marque="Ubiquiti"),
    )

    par_identity = client.get("/api/v1/equipements?identity=cla-st", headers=_entete(technicien)).json()
    assert [e["identity"] for e in par_identity] == ["CLA-ST-01"]

    par_site = client.get(f"/api/v1/equipements?site_id={site_b.id}", headers=_entete(technicien)).json()
    assert [e["identity"] for e in par_site] == ["CLB-AP-01"]

    par_numero_serie = client.get("/api/v1/equipements?numero_serie=0002", headers=_entete(technicien)).json()
    assert [e["identity"] for e in par_numero_serie] == ["CLB-AP-01"]

    par_marque = client.get("/api/v1/equipements?marque=Ubiquiti", headers=_entete(technicien)).json()
    assert [e["identity"] for e in par_marque] == ["CLB-AP-01"]


def test_mise_a_jour_partielle_ne_touche_pas_les_autres_champs(client, technicien, site):
    creation = client.post(
        "/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site)
    ).json()

    reponse = client.patch(
        f"/api/v1/equipements/{creation['id']}",
        headers=_entete(technicien),
        json={"emplacement": "Toiture bâtiment B"},
    )
    corps = reponse.json()
    assert corps["emplacement"] == "Toiture bâtiment B"
    assert corps["identity"] == "CLA-ST-01"
    assert corps["modifie_par_id"] == technicien.id


def test_fiche_equipement_agrege_configurations_inspections_et_incidents(
    client, technicien, referent_sheq, site, db_session
):
    creation = client.post(
        "/api/v1/equipements", headers=_entete(technicien), json=_donnees_equipement(site)
    ).json()
    equipement_id = creation["id"]

    configuration = Configuration(
        reference="CFG-0001",
        equipement_id=equipement_id,
        type_intervention=TypeIntervention.INSTALLATION,
        technicien_id=technicien.id,
        date_intervention=datetime.now(timezone.utc),
        cree_par_id=technicien.id,
    )
    db_session.add(configuration)

    inspection = Inspection(
        modele=TypeInspection.EQUIPEMENTS,
        site_id=site.id,
        equipement_id=equipement_id,
        inspecteur_id=technicien.id,
        date=date.today(),
        points=[{"point_checklist_id": 1, "libelle": "Fixation", "cotation": CotationPoint.CONFORME.value, "observation": None, "photo": None}],
        cree_par_id=technicien.id,
    )
    db_session.add(inspection)

    incident_meme_site = Signalement(
        type=TypeSignalement.INCIDENT,
        site_id=site.id,
        lieu="Pylône 24 m",
        description="Coupure liaison suite orage",
        anonyme=False,
        auteur_id=technicien.id,
        date_constat=datetime.now(timezone.utc),
        date_saisie=datetime.now(timezone.utc),
        statut=StatutSignalement.NOUVEAU,
        cree_par_id=technicien.id,
    )
    anomalie_non_incident = Signalement(
        type=TypeSignalement.ANOMALIE,
        site_id=site.id,
        lieu="Pylône 24 m",
        description="Peinture écaillée",
        anonyme=False,
        auteur_id=technicien.id,
        date_constat=datetime.now(timezone.utc),
        date_saisie=datetime.now(timezone.utc),
        statut=StatutSignalement.NOUVEAU,
        cree_par_id=technicien.id,
    )
    db_session.add_all([incident_meme_site, anomalie_non_incident])
    db_session.commit()

    reponse = client.get(f"/api/v1/equipements/{equipement_id}/fiche", headers=_entete(referent_sheq))
    corps = reponse.json()

    assert corps["equipement"]["id"] == equipement_id
    assert len(corps["configurations"]) == 1
    assert corps["configurations"][0]["reference"] == "CFG-0001"
    assert len(corps["inspections"]) == 1
    assert corps["inspections"][0]["taux_conformite"] == 1.0
    # Seul l'incident (pas l'anomalie) apparaît : filtrage par type incident/accident.
    assert len(corps["incidents"]) == 1
    assert corps["incidents"][0]["description"] == "Coupure liaison suite orage"


def test_import_csv_rapporte_les_erreurs_ligne_par_ligne(client, responsable, site):
    contenu_csv = (
        "Site / Client,Emplacement,Type d'équipement,Marque,Modèle,N° de série,Adresse MAC,Identity / Nom,"
        "Adresse IP,Date d'installation,Fin de garantie,Fiche de configuration (réf.),Dernière inspection,Statut,Observations\n"
        f"{site.nom},Pylône 24 m,Antenne PtP,MikroTik,LHG 5,SN1001,AA:BB:CC:DD:EE:01,CLA-ST-01,10.0.0.2,03/2026,03/2028,,,En service,\n"
        "Site Inconnu,Pylône 30 m,Antenne PtP,MikroTik,LHG 5,SN1002,AA:BB:CC:DD:EE:02,CLA-ST-02,10.0.0.3,03/2026,,,,,\n"
        f"{site.nom},Baie technique,Switch,MarqueInexistante,CRS309,SN1003,,CLA-SW-01,,03/2026,,,,,\n"
    )
    fichier = io.BytesIO(contenu_csv.encode("utf-8"))

    reponse = client.post(
        "/api/v1/equipements/import",
        headers=_entete(responsable),
        files={"fichier": ("import.csv", fichier, "text/csv")},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["total_lignes"] == 3
    assert corps["importees"] == 1
    assert corps["en_erreur"] == 2
    assert corps["equipements"][0]["identity"] == "CLA-ST-01"

    erreurs_par_ligne = {e["ligne"]: e["erreurs"] for e in corps["erreurs"]}
    assert "introuvable" in erreurs_par_ligne[2][0]
    assert "inconnue" in erreurs_par_ligne[3][0]


def test_import_xlsx(client, responsable, site):
    from openpyxl import Workbook

    classeur = Workbook()
    feuille = classeur.active
    feuille.append(["Gabarit d'import du parc"])
    feuille.append(["Ne pas modifier les en-têtes ci-dessous"])
    feuille.append([])
    feuille.append(
        [
            "N°",
            "Site / Client",
            "Emplacement",
            "Type d'équipement",
            "Marque",
            "Modèle",
            "N° de série",
            "Adresse MAC",
            "Identity / Nom",
            "Adresse IP",
            "Date d'installation",
            "Fin de garantie",
            "Fiche de configuration (réf.)",
            "Dernière inspection",
            "Statut",
            "Observations",
        ]
    )
    feuille.append(
        [1, site.nom, "Pylône 24 m", "Antenne PtP", "MikroTik", "LHG 5", "SN2001", "AA:BB:CC:DD:EE:FF", "CLA-ST-01", "10.0.0.2", "03/2026", "03/2028", "FOR-SHEQ-006", "05/2026", "En service", "Exemple"]
    )
    tampon = io.BytesIO()
    classeur.save(tampon)
    tampon.seek(0)

    reponse = client.post(
        "/api/v1/equipements/import",
        headers=_entete(responsable),
        files={"fichier": ("INV-SHEQ-001_Inventaire_Parc.xlsx", tampon, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["importees"] == 1
    assert corps["equipements"][0]["identity"] == "CLA-ST-01"
    assert corps["equipements"][0]["site_id"] == site.id


def test_import_rejette_un_format_non_supporte(client, responsable):
    fichier = io.BytesIO(b"contenu quelconque")
    reponse = client.post(
        "/api/v1/equipements/import",
        headers=_entete(responsable),
        files={"fichier": ("inventaire.txt", fichier, "text/plain")},
    )
    assert reponse.status_code == 400


def test_technicien_ne_peut_pas_importer(client, technicien):
    fichier = io.BytesIO(b"Site / Client,Emplacement\n")
    reponse = client.post(
        "/api/v1/equipements/import",
        headers=_entete(technicien),
        files={"fichier": ("import.csv", fichier, "text/csv")},
    )
    assert reponse.status_code == 403
