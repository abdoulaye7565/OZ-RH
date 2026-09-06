"""Tests du module Risques (prompt 4.1, section 5.2.5 du CDC)."""
import io
from datetime import date, timedelta

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _donnees_risque(**overrides):
    donnees = {
        "danger": "Chute de hauteur lors d'une intervention sur pylône",
        "categorie": "Chute / Circulation",
        "unite_travail": "Terrain",
        "personnes_exposees": "Techniciens",
        "cotation": {
            "probabilite": 3,
            "gravite": 5,
            "mesures_existantes": "Aucune",
            "mesures_proposees": "Port du harnais obligatoire, permis de travail en hauteur",
        },
    }
    donnees.update(overrides)
    return donnees


def test_creation_calcule_criticite_et_niveau(client, referent_sheq):
    reponse = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=_donnees_risque())
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["derniere_cotation"]["criticite"] == 15
    assert corps["derniere_cotation"]["niveau"] == "critique"
    assert corps["numero"] == 1


def test_numeros_sequentiels(client, referent_sheq):
    r1 = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=_donnees_risque()).json()
    r2 = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=_donnees_risque()).json()
    assert r2["numero"] == r1["numero"] + 1


def test_seuils_de_niveau(client, referent_sheq):
    cas = [
        (1, 1, "faible"),   # criticite 1
        (2, 2, "modéré"),   # criticite 4
        (2, 4, "élevé"),    # criticite 8
        (5, 3, "critique"), # criticite 15
    ]
    for probabilite, gravite, niveau_attendu in cas:
        donnees = _donnees_risque(cotation={"probabilite": probabilite, "gravite": gravite, "mesures_proposees": "Mesure X"})
        reponse = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=donnees)
        assert reponse.json()["derniere_cotation"]["niveau"] == niveau_attendu, (probabilite, gravite)


def test_mesure_de_maitrise_obligatoire_meme_a_faible_gravite(client, referent_sheq):
    """Règle 5.2.5 : "tout risque de gravité 4 ou 5 doit comporter au moins une
    mesure de maîtrise, quelle que soit sa criticité" — déjà couverte en rendant
    le champ obligatoire pour toute gravité, pas seulement 4/5 (voir schémas)."""
    donnees = _donnees_risque(cotation={"probabilite": 1, "gravite": 1, "mesures_proposees": "   "})
    reponse = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=donnees)
    assert reponse.status_code == 422


def test_technicien_ne_peut_pas_creer_un_risque(client, technicien):
    reponse = client.post("/api/v1/risques", headers=_entete(technicien), json=_donnees_risque())
    assert reponse.status_code == 403


def test_reevaluation_ajoute_a_lhistorique_sans_remplacer(client, referent_sheq):
    creation = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=_donnees_risque()).json()
    risque_id = creation["id"]

    reponse = client.post(
        f"/api/v1/risques/{risque_id}/reevaluer",
        headers=_entete(referent_sheq),
        json={"probabilite": 1, "gravite": 2, "mesures_proposees": "Mesures renforcées, risque réduit"},
    )
    assert reponse.status_code == 201
    assert reponse.json()["niveau"] == "faible"

    detail = client.get(f"/api/v1/risques/{risque_id}", headers=_entete(referent_sheq)).json()
    assert len(detail["cotations"]) == 2
    # La plus récente en tête, avec la nouvelle cotation — l'ancienne (criticité
    # 15) reste consultable telle quelle, pas écrasée.
    assert detail["derniere_cotation"]["niveau"] == "faible"
    criticites = {c["criticite"] for c in detail["cotations"]}
    assert criticites == {15, 2}


def test_liste_filtre_par_niveau_categorie_et_unite(client, referent_sheq):
    client.post(
        "/api/v1/risques",
        headers=_entete(referent_sheq),
        json=_donnees_risque(categorie="Électrique", unite_travail="Bureaux", cotation={"probabilite": 1, "gravite": 1, "mesures_proposees": "M"}),
    )
    client.post(
        "/api/v1/risques",
        headers=_entete(referent_sheq),
        json=_donnees_risque(categorie="Chute / Circulation", unite_travail="Terrain", cotation={"probabilite": 5, "gravite": 5, "mesures_proposees": "M"}),
    )

    par_niveau = client.get("/api/v1/risques?niveau=critique", headers=_entete(referent_sheq)).json()
    assert len(par_niveau) == 1
    assert par_niveau[0]["categorie"] == "Chute / Circulation"

    par_categorie = client.get("/api/v1/risques?categorie=Électrique", headers=_entete(referent_sheq)).json()
    assert len(par_categorie) == 1

    par_unite = client.get("/api/v1/risques?unite_travail=bureaux", headers=_entete(referent_sheq)).json()
    assert len(par_unite) == 1


def test_matrice_positionne_les_risques_par_case(client, referent_sheq):
    client.post("/api/v1/risques", headers=_entete(referent_sheq), json=_donnees_risque())  # P=3, G=5

    matrice = client.get("/api/v1/risques/matrice", headers=_entete(referent_sheq)).json()
    assert len(matrice) == 25  # grille 5x5 complète
    case = next(c for c in matrice if c["probabilite"] == 3 and c["gravite"] == 5)
    assert case["criticite"] == 15
    assert case["niveau"] == "critique"
    assert len(case["risques"]) == 1
    case_vide = next(c for c in matrice if c["probabilite"] == 1 and c["gravite"] == 1)
    assert case_vide["risques"] == []


def test_revue_due_apres_douze_mois(client, referent_sheq):
    ancienne_date = str(date.today() - timedelta(days=370))
    donnees = _donnees_risque(cotation={"probabilite": 2, "gravite": 2, "mesures_proposees": "M", "date_evaluation": ancienne_date})
    client.post("/api/v1/risques", headers=_entete(referent_sheq), json=donnees)

    reponse = client.get("/api/v1/risques/revues-dues", headers=_entete(referent_sheq))
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["due"] is True
    assert corps[0]["jours_restants"] < 0


def test_import_csv_recalcule_criticite_et_ignore_colonnes_non_modelisees(client, referent_sheq):
    contenu_csv = (
        "N°,Catégorie de risque,Zone / Activité,Danger identifié,Risque / Dommage potentiel,"
        "Personnes exposées,Mesures de prévention existantes,P,G,C,Niveau de risque,"
        "Mesures de maîtrise proposées,Responsable,Échéance,Statut\n"
        "1,Ergonomique,Bureaux,Travail prolongé sur écran,Fatigue visuelle,Tout le personnel,"
        "Chaises réglables,4,2,999,FAUX_NIVEAU,Aménagement ergonomique des postes,Référent SHEQ,Juin 2026,En cours\n"
        "2,CategorieInexistante,Bureaux,Danger X,,Personnel,,3,3,9,ÉLEVÉ,Mesure Y,Direction,Juillet 2026,À lancer\n"
    )
    fichier = io.BytesIO(contenu_csv.encode("utf-8"))

    reponse = client.post(
        "/api/v1/risques/import",
        headers=_entete(referent_sheq),
        files={"fichier": ("import.csv", fichier, "text/csv")},
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["total_lignes"] == 2
    assert corps["importes"] == 1
    assert corps["en_erreur"] == 1
    # C=999 et Niveau=FAUX_NIVEAU dans le fichier sont ignorés : recalculés
    # depuis P=4, G=2 -> criticité 8, "élevé" (pas les valeurs du fichier).
    risque_importe = corps["risques"][0]
    assert risque_importe["derniere_cotation"]["criticite"] == 8
    assert risque_importe["derniere_cotation"]["niveau"] == "élevé"
    assert "inconnue" in corps["erreurs"][0]["erreurs"][0]


def test_technicien_ne_peut_pas_importer(client, technicien):
    fichier = io.BytesIO("N°,Catégorie de risque\n".encode("utf-8"))
    reponse = client.post(
        "/api/v1/risques/import",
        headers=_entete(technicien),
        files={"fichier": ("import.csv", fichier, "text/csv")},
    )
    assert reponse.status_code == 403


def test_aucune_route_de_suppression_de_risque(client, referent_sheq):
    creation = client.post("/api/v1/risques", headers=_entete(referent_sheq), json=_donnees_risque()).json()
    reponse = client.delete(f"/api/v1/risques/{creation['id']}", headers=_entete(referent_sheq))
    assert reponse.status_code == 405
