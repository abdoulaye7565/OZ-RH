"""Tests du module Formations (prompt 4.2, section 5.3.3 du CDC)."""
from datetime import date, timedelta

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_creation_competence_et_habilitation_calcule_expiration(client, referent_sheq, technicien):
    competence = client.post(
        "/api/v1/formations/competences",
        headers=_entete(referent_sheq),
        json={"libelle": "Travail en hauteur", "periodicite_mois": 12},
    ).json()

    habilitation = client.post(
        "/api/v1/formations/habilitations",
        headers=_entete(referent_sheq),
        json={"utilisateur_id": technicien.id, "competence_id": competence["id"], "date_obtention": "2026-01-15"},
    ).json()

    assert habilitation["date_expiration"] == "2027-01-15"
    assert habilitation["expiree"] is False


def test_habilitation_expiree_signalee(client, referent_sheq, technicien):
    competence = client.post(
        "/api/v1/formations/competences",
        headers=_entete(referent_sheq),
        json={"libelle": "Secourisme", "periodicite_mois": 12},
    ).json()
    habilitation = client.post(
        "/api/v1/formations/habilitations",
        headers=_entete(referent_sheq),
        json={"utilisateur_id": technicien.id, "competence_id": competence["id"], "date_obtention": "2020-01-01"},
    ).json()
    assert habilitation["expiree"] is True


def test_technicien_ne_peut_pas_creer_de_competence(client, technicien):
    reponse = client.post(
        "/api/v1/formations/competences", headers=_entete(technicien), json={"libelle": "X", "periodicite_mois": 6}
    )
    assert reponse.status_code == 403


def test_matrice_restreinte_mais_mes_habilitations_ouvertes(client, referent_sheq, technicien, responsable):
    competence = client.post(
        "/api/v1/formations/competences",
        headers=_entete(referent_sheq),
        json={"libelle": "SLAM", "periodicite_mois": 12},
    ).json()
    client.post(
        "/api/v1/formations/habilitations",
        headers=_entete(referent_sheq),
        json={"utilisateur_id": technicien.id, "competence_id": competence["id"], "date_obtention": "2026-01-01"},
    )

    # Le technicien ne peut pas voir la matrice complète...
    reponse_matrice = client.get("/api/v1/formations/matrice", headers=_entete(technicien))
    assert reponse_matrice.status_code == 403

    # ...mais peut voir ses propres habilitations.
    reponse_mes_habs = client.get("/api/v1/formations/mes-habilitations", headers=_entete(technicien))
    assert reponse_mes_habs.status_code == 200
    assert len(reponse_mes_habs.json()) == 1

    # Le responsable ("direction") voit la matrice complète.
    reponse_responsable = client.get("/api/v1/formations/matrice", headers=_entete(responsable))
    assert reponse_responsable.status_code == 200
    corps = reponse_responsable.json()
    assert len(corps) == 1
    # Libellé résolu côté serveur (2026-09-19) : la route renvoyait jusqu'ici
    # des habilitations brutes, sans libellé de compétence exploitable par
    # l'écran (colonne "Compétence" vide en conditions réelles).
    assert corps[0]["libelle_competence"] == "SLAM"


def test_alerte_recyclage_detecte_une_habilitation_bientot_expiree(client, referent_sheq, technicien):
    competence = client.post(
        "/api/v1/formations/competences",
        headers=_entete(referent_sheq),
        json={"libelle": "SLAM", "periodicite_mois": 1},
    ).json()
    date_obtention = date.today() - timedelta(days=25)  # expire dans ~5 jours
    client.post(
        "/api/v1/formations/habilitations",
        headers=_entete(referent_sheq),
        json={"utilisateur_id": technicien.id, "competence_id": competence["id"], "date_obtention": str(date_obtention)},
    )

    reponse = client.get("/api/v1/formations/alertes-recyclage?horizon_jours=30", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    assert len(reponse.json()) == 1


def test_cloture_seance_avec_competence_renouvelle_habilitation_des_presents(client, referent_sheq, technicien):
    competence = client.post(
        "/api/v1/formations/competences",
        headers=_entete(referent_sheq),
        json={"libelle": "Sensibilisation SHEQ", "periodicite_mois": 12},
    ).json()
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={
            "theme": "Sensibilisation annuelle",
            "date": str(date.today()),
            "lieu": "Siège",
            "animateur_id": referent_sheq.id,
            "competence_id": competence["id"],
        },
    ).json()

    client.post(
        f"/api/v1/formations/seances/{seance['id']}/emargement",
        headers=_entete(referent_sheq),
        json={"participant_id": technicien.id, "present": True},
    )

    reponse = client.post(f"/api/v1/formations/seances/{seance['id']}/cloturer", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "realisee"

    matrice = client.get("/api/v1/formations/matrice", headers=_entete(referent_sheq)).json()
    assert len(matrice) == 1
    assert matrice[0]["utilisateur_id"] == technicien.id
    assert matrice[0]["date_obtention"] == str(date.today())


def test_emargement_est_idempotent_par_participant(client, referent_sheq, technicien):
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "X", "date": str(date.today()), "lieu": "Y", "animateur_id": referent_sheq.id},
    ).json()

    e1 = client.post(
        f"/api/v1/formations/seances/{seance['id']}/emargement",
        headers=_entete(referent_sheq),
        json={"participant_id": technicien.id, "present": False},
    ).json()
    e2 = client.post(
        f"/api/v1/formations/seances/{seance['id']}/emargement",
        headers=_entete(referent_sheq),
        json={"participant_id": technicien.id, "present": True},
    ).json()
    assert e1["id"] == e2["id"]
    assert e2["present"] is True


def test_liste_emargements_relit_les_presences_deja_enregistrees(client, referent_sheq, technicien, responsable):
    """2026-09-19 : sans cette route, un écran d'émargement rouvert ne peut
    pas savoir qui a déjà signé — seule l'écriture existait jusqu'ici."""
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "X", "date": str(date.today()), "lieu": "Y", "animateur_id": referent_sheq.id},
    ).json()

    vide = client.get(f"/api/v1/formations/seances/{seance['id']}/emargements", headers=_entete(referent_sheq))
    assert vide.status_code == 200
    assert vide.json() == []

    client.post(
        f"/api/v1/formations/seances/{seance['id']}/emargement",
        headers=_entete(referent_sheq),
        json={"participant_id": technicien.id, "present": True},
    )
    client.post(
        f"/api/v1/formations/seances/{seance['id']}/emargement",
        headers=_entete(referent_sheq),
        json={"participant_id": responsable.id, "present": False},
    )

    reponse = client.get(f"/api/v1/formations/seances/{seance['id']}/emargements", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 2
    presences = {e["participant_id"]: e["present"] for e in corps}
    assert presences[technicien.id] is True
    assert presences[responsable.id] is False


def test_liste_questions_ne_revele_jamais_la_reponse(client, technicien):
    reponse = client.get("/api/v1/formations/questions-quiz", headers=_entete(technicien))
    assert reponse.status_code == 200
    questions = reponse.json()
    assert len(questions) == 10
    for q in questions:
        assert "reponse_correcte" not in q


def test_quiz_calcule_le_score_et_le_seuil_de_reussite(client, referent_sheq, technicien):
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "Sensibilisation", "date": str(date.today()), "lieu": "Y", "animateur_id": referent_sheq.id},
    ).json()
    questions = client.get("/api/v1/formations/questions-quiz", headers=_entete(technicien)).json()

    # Réponses volontairement fausses pour toutes les questions.
    reponses = [{"question_id": q["id"], "reponse": "z"} for q in questions]
    resultat = client.post(
        f"/api/v1/formations/seances/{seance['id']}/quiz", headers=_entete(technicien), json={"seance_id": seance["id"], "reponses": reponses}
    ).json()
    assert resultat["score"] == 0
    assert resultat["total_questions"] == 10
    assert resultat["reussi"] is False


def test_quiz_refuse_une_reponse_manquante(client, referent_sheq, technicien):
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "Sensibilisation", "date": str(date.today()), "lieu": "Y", "animateur_id": referent_sheq.id},
    ).json()
    reponse = client.post(
        f"/api/v1/formations/seances/{seance['id']}/quiz",
        headers=_entete(technicien),
        json={"seance_id": seance["id"], "reponses": [{"question_id": 1, "reponse": "a"}]},
    )
    assert reponse.status_code == 400


def test_modification_seance_planifiee(client, referent_sheq, technicien):
    """Revue d'ensemble 2026-09-10 : PATCH /formations/seances/{id} corrige
    une séance encore planifiée (aucune route ne le permettait)."""
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "Sensibilisation", "date": str(date.today()), "lieu": "Siège", "animateur_id": referent_sheq.id},
    ).json()

    reponse = client.patch(
        f"/api/v1/formations/seances/{seance['id']}",
        headers=_entete(referent_sheq),
        json={"theme": "Sensibilisation annuelle SHEQ", "lieu": "Antenne Kayes"},
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["theme"] == "Sensibilisation annuelle SHEQ"
    assert corps["lieu"] == "Antenne Kayes"
    assert corps["animateur_id"] == referent_sheq.id  # non fourni => inchangé


def test_modification_refusee_apres_cloture(client, referent_sheq, technicien):
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "Sensibilisation", "date": str(date.today()), "lieu": "Siège", "animateur_id": referent_sheq.id},
    ).json()
    client.post(f"/api/v1/formations/seances/{seance['id']}/cloturer", headers=_entete(referent_sheq))

    reponse = client.patch(
        f"/api/v1/formations/seances/{seance['id']}", headers=_entete(referent_sheq), json={"theme": "trop tard"}
    )
    assert reponse.status_code == 409


def test_modification_seance_refusee_a_un_technicien(client, referent_sheq, technicien):
    seance = client.post(
        "/api/v1/formations/seances",
        headers=_entete(referent_sheq),
        json={"theme": "Sensibilisation", "date": str(date.today()), "lieu": "Siège", "animateur_id": referent_sheq.id},
    ).json()
    reponse = client.patch(
        f"/api/v1/formations/seances/{seance['id']}", headers=_entete(technicien), json={"theme": "x"}
    )
    assert reponse.status_code == 403
