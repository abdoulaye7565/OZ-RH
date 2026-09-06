"""Recette du lot 1 (prompt 1.6, chapitre 14 du CDC, tableau 8).

Un test par cas de test numéroté dans le tableau 8, pour une traçabilité directe
entre ce fichier et le CDC. Les cas 1, 2 et 10 portent sur le mécanisme hors
connexion (prompt 1.4) : ce prompt a été présenté (stratégie) mais jamais
implémenté — en attente de validation, voir docs/JOURNAL.md. Les marquer
"réussis" en écrivant un test qui ne vérifie rien de réel serait mentir sur
l'état du projet ; ils sont donc explicitement `skip` avec le motif, pour que
la suite reste un reflet honnête de ce qui existe réellement.
"""
from datetime import date, datetime, timezone

import pytest

from app.core.security import creer_access_token
from app.models.cotation_risque import CotationRisque
from app.models.enums import CategorieRisque, NiveauRisque
from app.models.risque import Risque


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _champs_signalement(site, **overrides):
    donnees = {
        "type": "incident",
        "site_id": str(site.id),
        "lieu": "Pylône P12",
        "description": "Test de recette.",
        "anonyme": "false",
        "date_constat": datetime.now(timezone.utc).isoformat(),
    }
    donnees.update(overrides)
    return donnees


@pytest.fixture()
def risque_recette(db_session, referent_sheq):
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
    return r


# --- Cas 1, 2, 10 : bloqués par l'absence du prompt 1.4 --------------------


@pytest.mark.skip(
    reason="Cas 1 (CDC tableau 8) : nécessite la file d'attente hors connexion du "
    "prompt 1.4, jamais implémentée (stratégie proposée le 2026-09-05, en attente "
    "de validation)."
)
def test_cas_01_creation_hors_connexion_moins_de_deux_minutes_avec_photo():
    ...


@pytest.mark.skip(
    reason="Cas 2 (CDC tableau 8) : nécessite la synchronisation et l'attribution "
    "différée de référence du prompt 1.4, jamais implémentées."
)
def test_cas_02_synchronisation_attribue_le_numero_definitif():
    ...


@pytest.mark.skip(
    reason="Cas 10 (CDC tableau 8) : nécessite la détection de conflit du prompt "
    "1.4, jamais implémentée."
)
def test_cas_10_modification_concurrente_deux_versions_presentees():
    ...


# --- Cas 11 : mise à jour du tableau de bord sans ressaisie -----------------


def test_cas_11_tableau_de_bord_reflete_un_nouveau_signalement_sans_ressaisie(
    client, technicien, referent_sheq, site
):
    avant = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq)).json()
    total_avant = avant["signalements"]["total_periode"]

    client.post("/api/v1/signalements", headers=_entete(technicien), data=_champs_signalement(site))

    apres = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq)).json()
    assert apres["signalements"]["total_periode"] == total_avant + 1


def test_cas_11_tableau_de_bord_reflete_une_action_cloturee_sans_ressaisie(
    client, referent_sheq, risque_recette
):
    creation = client.post(
        "/api/v1/actions",
        headers=_entete(referent_sheq),
        json={
            "libelle": "Action de recette",
            "risque_id": risque_recette.id,
            "type_mesure": "corrective",
            "responsable_id": referent_sheq.id,
            "echeance": str(date.today()),
        },
    ).json()

    avant = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq)).json()
    assert avant["actions"]["par_statut"]["ouverte"] >= 1

    client.patch(
        f"/api/v1/actions/{creation['id']}/avancement",
        headers=_entete(referent_sheq),
        json={"avancement": 100, "indicateur": "Fait"},
    )
    client.patch(
        f"/api/v1/actions/{creation['id']}/statut", headers=_entete(referent_sheq), json={"statut": "cloturee"}
    )

    apres = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq)).json()
    assert apres["actions"]["par_statut"]["cloturee"] == avant["actions"]["par_statut"]["cloturee"] + 1


# --- Cas 13 : historique d'un enregistrement (auteur + horodatage) ---------


def test_cas_13_creation_horodatee_avec_auteur(client, technicien, site):
    reponse = client.post(
        "/api/v1/signalements", headers=_entete(technicien), data=_champs_signalement(site, anonyme="false")
    )
    corps = reponse.json()

    assert corps["cree_le"] is not None
    assert corps["cree_par_id"] == technicien.id
    # Pas encore modifié : date de modification technique égale (ou très proche)
    # de la création, aucun modificateur.
    assert corps["modifie_par_id"] is None


def test_cas_13_modification_horodatee_avec_auteur_du_modificateur(
    client, db_session, technicien, referent_sheq, site
):
    """`modifie_par_id` doit refléter QUI a agi, pas nécessairement l'auteur
    d'origine — corrigé à l'occasion de ce prompt : les services de signalements
    et d'actions ne renseignaient cette colonne dans aucun cas avant ce prompt,
    bien qu'elle existe depuis le modèle de données (prompt 0.2)."""
    creation = client.post(
        "/api/v1/signalements", headers=_entete(technicien), data=_champs_signalement(site)
    ).json()
    assert creation["modifie_par_id"] is None

    reponse = client.patch(
        f"/api/v1/signalements/{creation['id']}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_analyse"},
    )
    corps = reponse.json()

    assert corps["cree_par_id"] == technicien.id, "l'auteur d'origine ne doit pas changer"
    assert corps["modifie_par_id"] == referent_sheq.id, "le modificateur doit être celui qui a agi"
    assert corps["modifie_le"] >= corps["cree_le"]


def test_cas_13_anonymat_preserve_meme_apres_traitement_par_un_tiers(client, technicien, referent_sheq, site):
    """La traçabilité de qui TRAITE un signalement (référent SHEQ) ne doit
    jamais réintroduire l'identité de son auteur anonyme d'origine."""
    creation = client.post(
        "/api/v1/signalements", headers=_entete(technicien), data=_champs_signalement(site, anonyme="true")
    ).json()
    assert creation["cree_par_id"] is None
    assert creation["auteur_id"] is None

    reponse = client.patch(
        f"/api/v1/signalements/{creation['id']}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_analyse"},
    )
    corps = reponse.json()
    assert corps["cree_par_id"] is None, "l'anonymat porte sur la création, pas sur le traitement"
    assert corps["auteur_id"] is None
    assert corps["modifie_par_id"] == referent_sheq.id


def test_cas_13_limite_pas_d_historique_complet_des_transitions(client, technicien, referent_sheq, site):
    """Documente une limite réelle plutôt que de la passer sous silence :
    l'API ne restitue que l'état COURANT (dernière modification), pas la liste
    chronologique de toutes les transitions passées ("toutes les opérations"
    au sens du cas 13). Aucune table de journal de ce type n'existe pour les
    signalements ou les actions — seul JOURNAL_ACCES existe, et il est réservé
    au coffre-fort (chapitre 7.2.8 du CDC). Une restitution FIDÈLE et COMPLÈTE
    du cas 13 nécessiterait une table d'historique dédiée, à ajouter
    explicitement si ce niveau de traçabilité est requis en l'état."""
    creation = client.post(
        "/api/v1/signalements", headers=_entete(technicien), data=_champs_signalement(site)
    ).json()
    client.patch(
        f"/api/v1/signalements/{creation['id']}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "en_analyse"},
    )
    client.patch(
        f"/api/v1/signalements/{creation['id']}/statut",
        headers=_entete(referent_sheq),
        json={"statut": "cloture"},
    )

    lecture = client.get(f"/api/v1/signalements/{creation['id']}", headers=_entete(referent_sheq)).json()
    # Seul le statut final est visible ; rien ne restitue le passage par
    # "en_analyse" avant "cloture", ni qui a déclenché chaque transition.
    assert lecture["statut"] == "cloture"
    assert "historique" not in lecture
    assert "transitions" not in lecture


# --- Cas 14 : refus de toute suppression ------------------------------------


def test_cas_14_signalement_aucune_suppression_possible(client):
    reponse = client.delete("/api/v1/signalements/1")
    assert reponse.status_code == 405


def test_cas_14_action_aucune_suppression_possible(client):
    reponse = client.delete("/api/v1/actions/1")
    assert reponse.status_code == 405


def test_cas_14_utilisateur_aucune_suppression_possible(client):
    # 404, pas 405 : contrairement à signalements/actions, aucune route
    # /auth/utilisateurs/{id} n'existe DU TOUT (même pas en lecture) — la
    # suppression est donc impossible par construction, pas seulement bloquée
    # sur une route existante.
    reponse = client.delete("/api/v1/auth/utilisateurs/1")
    assert reponse.status_code == 404


def test_cas_14_seul_archivage_disponible_pour_signalement(client, technicien, referent_sheq, site):
    creation = client.post(
        "/api/v1/signalements", headers=_entete(technicien), data=_champs_signalement(site)
    ).json()

    reponse = client.post(f"/api/v1/signalements/{creation['id']}/archiver", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    assert reponse.json()["archive"] is True

    # Toujours présent en base, jamais supprimé physiquement.
    lecture = client.get(f"/api/v1/signalements/{creation['id']}", headers=_entete(referent_sheq))
    assert lecture.status_code == 200
