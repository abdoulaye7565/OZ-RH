"""Tests du module Actions (prompt 1.2)."""
from datetime import date, timedelta

import pytest

from app.core.security import creer_access_token, hacher_mot_de_passe
from app.models.cotation_risque import CotationRisque
from app.models.enums import RoleUtilisateur
from app.models.risque import Risque
from app.models.utilisateur import Utilisateur
from app.models.enums import CategorieRisque, NiveauRisque


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


@pytest.fixture()
def risque(db_session, referent_sheq):
    # RISQUE ne porte plus la cotation elle-même depuis le prompt 4.1 (voir
    # app/models/risque.py) — une CotationRisque est requise séparément, même
    # si ce fichier n'a besoin ici que de risque.id comme clé étrangère.
    r = Risque(
        numero=1,
        danger="Chute de hauteur",
        categorie=CategorieRisque.CHUTE_CIRCULATION,
        unite_travail="Terrain",
        cree_par_id=referent_sheq.id,
    )
    db_session.add(r)
    db_session.flush()
    db_session.add(
        CotationRisque(
            risque_id=r.id,
            probabilite=3,
            gravite=5,
            criticite=15,
            niveau=NiveauRisque.CRITIQUE,
            mesures_proposees="Port du harnais",
            date_evaluation=date.today(),
            auteur_id=referent_sheq.id,
            cree_par_id=referent_sheq.id,
        )
    )
    db_session.commit()
    # Attribut transitoire (non mappé), pour la seule commodité des tests de ce
    # fichier : `auteur_id` n'existe plus sur le modèle Risque depuis le prompt
    # 4.1 (déplacé sur CotationRisque) mais `_donnees_action` ci-dessous reste
    # inchangée pour ne pas devoir modifier ses ~15 points d'appel.
    r.auteur_id = referent_sheq.id
    return r


def _donnees_action(risque, **overrides):
    donnees = {
        "libelle": "Installer une ligne de vie",
        "risque_id": risque.id,
        "type_mesure": "corrective",
        "responsable_id": risque.auteur_id,
        "echeance": str(date.today() + timedelta(days=30)),
    }
    donnees.update(overrides)
    return donnees


def test_referent_peut_creer_une_action_rattachee_a_un_risque(client, referent_sheq, risque):
    reponse = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["statut"] == "ouverte"
    assert corps["avancement"] == 0
    assert corps["en_retard"] is False


def test_technicien_ne_peut_pas_creer_une_action(client, technicien, risque):
    reponse = client.post("/api/v1/actions", headers=_entete(technicien), json=_donnees_action(risque))
    assert reponse.status_code == 403


def test_action_sans_origine_refusee(client, referent_sheq, risque):
    donnees = _donnees_action(risque)
    donnees["risque_id"] = None
    reponse = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=donnees)
    assert reponse.status_code == 422


def test_action_avec_deux_origines_refusee(client, referent_sheq, risque, site, db_session):
    from app.models.signalement import Signalement
    from app.models.enums import TypeSignalement, StatutSignalement
    from datetime import datetime, timezone

    sig = Signalement(
        reference="SIG-2026-999",
        type=TypeSignalement.INCIDENT,
        site_id=site.id,
        lieu="Test",
        description="Test",
        anonyme=False,
        auteur_id=referent_sheq.id,
        date_constat=datetime.now(timezone.utc),
        date_saisie=datetime.now(timezone.utc),
        statut=StatutSignalement.NOUVEAU,
    )
    db_session.add(sig)
    db_session.commit()

    donnees = _donnees_action(risque, signalement_id=sig.id)
    reponse = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=donnees)
    assert reponse.status_code == 422


def test_cloture_sans_indicateur_refusee(client, referent_sheq, risque):
    """Cas de refus explicitement demandé par le prompt 1.2."""
    creation = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))
    action_id = creation.json()["id"]

    reponse = client.patch(
        f"/api/v1/actions/{action_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "cloturee"},
    )
    assert reponse.status_code == 409


def test_cloture_avec_indicateur_acceptee(client, referent_sheq, risque):
    creation = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))
    action_id = creation.json()["id"]

    client.patch(
        f"/api/v1/actions/{action_id}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Ligne de vie installée et contrôlée"},
    )

    reponse = client.patch(
        f"/api/v1/actions/{action_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "cloturee"},
    )
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "cloturee"


def test_transition_apres_cloture_refusee(client, referent_sheq, risque):
    creation = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))
    action_id = creation.json()["id"]
    client.patch(
        f"/api/v1/actions/{action_id}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Fait"},
    )
    client.patch(f"/api/v1/actions/{action_id}/statut", headers=_entete(referent_sheq), json={"statut": "cloturee"})

    reponse = client.patch(
        f"/api/v1/actions/{action_id}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_cours"},
    )
    assert reponse.status_code == 409


def test_action_en_retard_calculee_automatiquement(client, referent_sheq, risque):
    donnees = _donnees_action(risque, echeance=str(date.today() - timedelta(days=5)))
    reponse = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=donnees)
    assert reponse.json()["en_retard"] is True


def test_action_cloturee_n_est_jamais_en_retard_meme_echeance_passee(client, referent_sheq, risque):
    donnees = _donnees_action(risque, echeance=str(date.today() - timedelta(days=5)))
    creation = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=donnees)
    action_id = creation.json()["id"]

    client.patch(
        f"/api/v1/actions/{action_id}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Fait"},
    )
    reponse = client.patch(
        f"/api/v1/actions/{action_id}/statut", headers=_entete(referent_sheq), json={"statut": "cloturee"}
    )
    assert reponse.json()["en_retard"] is False


def test_responsable_peut_mettre_a_jour_sa_propre_action(client, db_session, referent_sheq, risque, site):
    responsable = Utilisateur(
        nom="Koné",
        prenom="Test",
        identifiant="responsable.test",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(responsable)
    db_session.commit()

    creation = client.post(
        "/api/v1/actions",
        headers=_entete(referent_sheq),
        json=_donnees_action(risque, responsable_id=responsable.id),
    )
    action_id = creation.json()["id"]

    reponse = client.patch(
        f"/api/v1/actions/{action_id}/avancement",
        headers=_entete(responsable),
        json={"avancement": 50},
    )
    assert reponse.status_code == 200
    assert reponse.json()["avancement"] == 50


def test_autre_utilisateur_ne_peut_pas_mettre_a_jour_une_action_qui_ne_lui_est_pas_confiee(
    client, db_session, referent_sheq, risque, technicien, site
):
    responsable = Utilisateur(
        nom="Koné",
        prenom="Test2",
        identifiant="responsable.test2",
        mot_de_passe=hacher_mot_de_passe("PeuImporte!123"),
        role=RoleUtilisateur.TECHNICIEN,
        site_id=site.id,
    )
    db_session.add(responsable)
    db_session.commit()

    creation = client.post(
        "/api/v1/actions",
        headers=_entete(referent_sheq),
        json=_donnees_action(risque, responsable_id=responsable.id),
    )
    action_id = creation.json()["id"]

    reponse = client.patch(
        f"/api/v1/actions/{action_id}/avancement",
        headers=_entete(technicien),
        json={"avancement": 50},
    )
    assert reponse.status_code == 403


def test_synthese_par_statut_et_taux_avancement_global(client, referent_sheq, risque):
    a1 = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque)).json()
    client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))

    client.patch(
        f"/api/v1/actions/{a1['id']}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Fait"},
    )
    client.patch(f"/api/v1/actions/{a1['id']}/statut", headers=_entete(referent_sheq), json={"statut": "cloturee"})

    reponse = client.get("/api/v1/actions/synthese", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["par_statut"]["cloturee"] == 1
    assert corps["par_statut"]["ouverte"] == 1
    assert corps["taux_avancement_global"] == 0.5


def test_filtre_liste_par_statut(client, referent_sheq, risque):
    a1 = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque)).json()
    client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))
    client.patch(
        f"/api/v1/actions/{a1['id']}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Fait"},
    )
    client.patch(f"/api/v1/actions/{a1['id']}/statut", headers=_entete(referent_sheq), json={"statut": "cloturee"})

    reponse = client.get("/api/v1/actions?statut=cloturee", headers=_entete(referent_sheq))
    resultats = reponse.json()
    assert len(resultats) == 1
    assert resultats[0]["id"] == a1["id"]


def test_toute_personne_authentifiee_peut_consulter_la_liste(client, technicien, referent_sheq, risque):
    client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque))
    reponse = client.get("/api/v1/actions", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert len(reponse.json()) == 1


def test_aucune_route_de_suppression(client):
    reponse = client.delete("/api/v1/actions/1")
    assert reponse.status_code == 405


def test_modification_action_corrige_libelle_et_echeance(client, referent_sheq, risque):
    """Revue d'ensemble 2026-09-10 : PATCH /actions/{id} corrige les champs de
    suivi (aucune route ne le permettait, seul avancement/statut)."""
    cree = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque)).json()
    nouvelle_echeance = str(date.today() + timedelta(days=60))

    reponse = client.patch(
        f"/api/v1/actions/{cree['id']}",
        headers=_entete(referent_sheq),
        json={"libelle": "Installer une ligne de vie — priorité revue", "echeance": nouvelle_echeance},
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["libelle"] == "Installer une ligne de vie — priorité revue"
    assert corps["echeance"] == nouvelle_echeance
    assert corps["type_mesure"] == cree["type_mesure"]  # non fourni => inchangé


def test_modification_refusee_sur_action_cloturee(client, referent_sheq, risque):
    cree = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque)).json()
    client.patch(
        f"/api/v1/actions/{cree['id']}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Ligne de vie posée et contrôlée"},
    )
    client.patch(f"/api/v1/actions/{cree['id']}/statut", headers=_entete(referent_sheq), json={"statut": "cloturee"})

    reponse = client.patch(
        f"/api/v1/actions/{cree['id']}", headers=_entete(referent_sheq), json={"libelle": "trop tard"}
    )
    assert reponse.status_code == 409


def test_modification_libelle_vide_refuse(client, referent_sheq, risque):
    cree = client.post("/api/v1/actions", headers=_entete(referent_sheq), json=_donnees_action(risque)).json()
    reponse = client.patch(f"/api/v1/actions/{cree['id']}", headers=_entete(referent_sheq), json={"libelle": "  "})
    assert reponse.status_code == 422
