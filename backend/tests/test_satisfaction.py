"""Tests du module Satisfaction client (prompt 4.3, section 5.3.6 du CDC,
FOR-SHEQ-018)."""
from app.core.security import creer_access_token
from app.services.satisfaction_service import CRITERES


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _notes(note_defaut: int, **overrides_par_critere) -> list[dict]:
    return [{"critere": c, "note": overrides_par_critere.get(c, note_defaut)} for c in CRITERES]


def test_technicien_peut_envoyer_une_enquete(client, technicien):
    reponse = client.post(
        "/api/v1/satisfaction/enquetes",
        headers=_entete(technicien),
        json={"client": "Client Démo", "intervention": "Installation antenne", "technicien_id": technicien.id},
    )
    assert reponse.status_code == 201
    assert reponse.json()["jeton"]
    assert reponse.json()["repondu"] is False


def test_collaborateur_ne_peut_pas_envoyer_d_enquete(client, db_session, site):
    from app.core.security import hacher_mot_de_passe
    from app.models.enums import RoleUtilisateur
    from app.models.utilisateur import Utilisateur

    collaborateur = Utilisateur(
        nom="X", prenom="Y", identifiant="x.y", mot_de_passe=hacher_mot_de_passe("Motdepasse!42"),
        role=RoleUtilisateur.COLLABORATEUR, site_id=site.id,
    )
    db_session.add(collaborateur)
    db_session.commit()

    reponse = client.post(
        "/api/v1/satisfaction/enquetes",
        headers=_entete(collaborateur),
        json={"client": "Client Démo", "intervention": "X"},
    )
    assert reponse.status_code == 403


def test_questionnaire_public_ne_necessite_aucune_authentification(client, technicien):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()

    # Aucun en-tête d'autorisation : c'est tout l'intérêt du lien public.
    reponse = client.get(f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps["criteres"]) == 6


def test_jeton_invalide_renvoie_404(client):
    reponse = client.get("/api/v1/satisfaction/questionnaire/jeton-inexistant")
    assert reponse.status_code == 404


def test_reponse_avec_toutes_notes_bonnes_ne_declenche_pas_d_analyse(client, technicien):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()
    reponse = client.post(
        f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}",
        json={"notes": _notes(5), "recommandation": "oui_certainement", "remarques": "Très bien"},
    )
    assert reponse.status_code == 201
    assert reponse.json()["necessite_analyse"] is False


def test_une_seule_note_basse_declenche_l_analyse(client, technicien):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()
    notes = _notes(5, **{CRITERES[2]: 1})  # une seule note à 1/5
    reponse = client.post(
        f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}",
        json={"notes": notes, "recommandation": "probablement"},
    )
    assert reponse.status_code == 201
    assert reponse.json()["necessite_analyse"] is True


def test_jeton_deja_repondu_est_refuse(client, technicien):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()
    client.post(
        f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}",
        json={"notes": _notes(5), "recommandation": "oui_certainement"},
    )
    reponse = client.get(f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}")
    assert reponse.status_code == 404


def test_reponse_incomplete_est_refusee(client, technicien):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()
    reponse = client.post(
        f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}",
        json={"notes": [{"critere": CRITERES[0], "note": 5}], "recommandation": "oui_certainement"},
    )
    assert reponse.status_code == 400


def test_reponse_a_analyser_visible_par_le_referent_sheq_et_action_creable(client, technicien, referent_sheq):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()
    notes = _notes(5, **{CRITERES[0]: 2})
    reponse_soumise = client.post(
        f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}",
        json={"notes": notes, "recommandation": "non", "remarques": "Installation en retard"},
    ).json()

    a_traiter = client.get("/api/v1/satisfaction/a-traiter", headers=_entete(referent_sheq)).json()
    assert len(a_traiter) == 1
    assert a_traiter[0]["id"] == reponse_soumise["id"]

    action = client.post(
        "/api/v1/actions",
        headers=_entete(referent_sheq),
        json={
            "libelle": "Analyser l'insatisfaction client",
            "reponse_satisfaction_id": reponse_soumise["id"],
            "type_mesure": "corrective",
            "responsable_id": referent_sheq.id,
            "echeance": "2027-01-01",
        },
    )
    assert action.status_code == 201
    assert action.json()["reponse_satisfaction_id"] == reponse_soumise["id"]


def test_technicien_ne_peut_pas_consulter_les_reponses_a_traiter(client, technicien):
    reponse = client.get("/api/v1/satisfaction/a-traiter", headers=_entete(technicien))
    assert reponse.status_code == 403


def test_lister_toutes_les_reponses_inclut_celles_sans_analyse(client, technicien, referent_sheq):
    enquete = client.post(
        "/api/v1/satisfaction/enquetes", headers=_entete(technicien), json={"client": "Client Démo", "intervention": "X"}
    ).json()
    client.post(
        f"/api/v1/satisfaction/questionnaire/{enquete['jeton']}",
        json={"notes": _notes(5), "recommandation": "oui_certainement"},
    )

    toutes = client.get("/api/v1/satisfaction/reponses", headers=_entete(referent_sheq)).json()
    assert len(toutes) == 1
    assert toutes[0]["necessite_analyse"] is False

    # Contrairement à /a-traiter, cette route n'exclut pas les bonnes notes.
    a_traiter = client.get("/api/v1/satisfaction/a-traiter", headers=_entete(referent_sheq)).json()
    assert len(a_traiter) == 0


def test_technicien_ne_peut_pas_consulter_toutes_les_reponses(client, technicien):
    reponse = client.get("/api/v1/satisfaction/reponses", headers=_entete(technicien))
    assert reponse.status_code == 403
