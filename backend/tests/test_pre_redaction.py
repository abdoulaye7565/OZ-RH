"""Tests de la pré-rédaction des rapports (prompt 6.4, chapitre 16.2.4 du CDC).

Aucun appel réel au fournisseur (voir tests/test_assistance.py) : le client
`assistance.client.appeler` est simulé, la logique de brouillon/validation et
l'assemblage du PDF sont, eux, entièrement réels — y compris la vérification
du contenu texte du PDF produit (pypdf), pas seulement de sa présence."""
import io
from datetime import date, timedelta

import pypdf
import pytest
from fastapi import HTTPException

from app.core.security import creer_access_token
from app.schemas.audit import CampagneCreation
from app.schemas.revue import RevueCreation
from app.services import audit_service, revue_service
from app.services.assistance import client as assistance_client
from app.services.assistance.client import ResultatAppel


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _texte_pdf(contenu: bytes) -> str:
    lecteur = pypdf.PdfReader(io.BytesIO(contenu))
    return "\n".join(page.extract_text() or "" for page in lecteur.pages)


def _nouvelle_revue(db_session, referent_sheq):
    return revue_service.creer_revue(
        db_session,
        RevueCreation(date=date.today(), periode_debut=date.today() - timedelta(days=90), periode_fin=date.today()),
        redacteur_id=referent_sheq.id,
    )


# --- Revue de direction ---


def test_generer_commentaire_revue_reste_brouillon(db_session, referent_sheq, responsable, monkeypatch):
    monkeypatch.setattr(
        assistance_client, "appeler",
        lambda db, *, fonction, prompt, utilisateur_id: ResultatAppel(disponible=True, contenu="Synthèse générée."),
    )
    revue = _nouvelle_revue(db_session, referent_sheq)

    revue = revue_service.generer_commentaire(db_session, revue, responsable.id)

    assert revue.commentaire_ia == "Synthèse générée."
    assert revue.commentaire_valide is False


def test_modifier_commentaire_revue_repasse_en_brouillon(db_session, referent_sheq, responsable):
    revue = _nouvelle_revue(db_session, referent_sheq)
    revue.commentaire_ia = "Ancien texte"
    revue.commentaire_valide = True
    db_session.commit()

    revue = revue_service.modifier_commentaire(db_session, revue, "Nouveau texte librement écrit", responsable.id)

    assert revue.commentaire_ia == "Nouveau texte librement écrit"
    assert revue.commentaire_valide is False


def test_modifier_commentaire_revue_texte_vide_repart_a_zero(db_session, referent_sheq, responsable):
    revue = _nouvelle_revue(db_session, referent_sheq)
    revue.commentaire_ia = "Texte existant"
    db_session.commit()

    revue = revue_service.modifier_commentaire(db_session, revue, "", responsable.id)

    assert revue.commentaire_ia is None


def test_valider_commentaire_revue_sans_contenu_refuse(db_session, referent_sheq, responsable):
    revue = _nouvelle_revue(db_session, referent_sheq)
    with pytest.raises(HTTPException) as exc:
        revue_service.valider_commentaire(db_session, revue, responsable.id)
    assert exc.value.status_code == 409


def test_pdf_revue_omet_le_commentaire_non_valide(db_session, referent_sheq, responsable):
    revue = _nouvelle_revue(db_session, referent_sheq)
    revue.commentaire_ia = "Un commentaire non encore validé, ne doit pas apparaître."
    db_session.commit()

    contenu = revue_service.generer_pdf(db_session, revue, referent_sheq)
    texte = _texte_pdf(contenu)

    assert "Analyse des événements marquants" not in texte
    assert "ne doit pas apparaître" not in texte


def test_pdf_revue_inclut_le_commentaire_valide(db_session, referent_sheq, responsable):
    revue = _nouvelle_revue(db_session, referent_sheq)
    revue.commentaire_ia = "Ce commentaire validé doit apparaître dans le PDF."
    revue.commentaire_valide = True
    db_session.commit()

    contenu = revue_service.generer_pdf(db_session, revue, referent_sheq)
    texte = _texte_pdf(contenu)

    assert "Analyse des événements marquants" in texte
    assert "doit apparaître dans le PDF" in texte


# --- Campagne d'audit ---


def test_generer_commentaire_audit_reste_brouillon(db_session, referent_sheq, monkeypatch):
    monkeypatch.setattr(
        assistance_client, "appeler",
        lambda db, *, fonction, prompt, utilisateur_id: ResultatAppel(disponible=True, contenu="Synthèse d'audit."),
    )
    campagne = audit_service.creer_campagne(db_session, CampagneCreation(), auditeur_id=referent_sheq.id)

    campagne = audit_service.generer_commentaire(db_session, campagne, referent_sheq.id)

    assert campagne.commentaire_ia == "Synthèse d'audit."
    assert campagne.commentaire_valide is False


def test_pdf_audit_inclut_le_commentaire_valide_seulement(db_session, referent_sheq):
    campagne = audit_service.creer_campagne(db_session, CampagneCreation(), auditeur_id=referent_sheq.id)
    campagne.commentaire_ia = "Commentaire de synthèse d'audit validé."
    campagne.commentaire_valide = True
    db_session.commit()

    contenu = audit_service.generer_pdf(db_session, campagne, referent_sheq)
    texte = _texte_pdf(contenu)

    assert "Commentaire de synthèse d'audit validé" in texte


# --- Routes ---


def test_route_generer_commentaire_revue_refusee_au_technicien(client, referent_sheq, technicien):
    revue = client.post(
        "/api/v1/revues", headers=_entete(referent_sheq),
        json={"date": "2026-09-07", "periode_debut": "2026-06-01", "periode_fin": "2026-09-07"},
    ).json()
    reponse = client.post(f"/api/v1/revues/{revue['id']}/commentaire/generer", headers=_entete(technicien))
    assert reponse.status_code == 403


def test_route_cycle_complet_commentaire_revue(client, referent_sheq, responsable, monkeypatch):
    monkeypatch.setattr(
        assistance_client, "appeler",
        lambda db, *, fonction, prompt, utilisateur_id: ResultatAppel(disponible=True, contenu="Texte pré-rédigé."),
    )
    revue = client.post(
        "/api/v1/revues", headers=_entete(referent_sheq),
        json={"date": "2026-09-07", "periode_debut": "2026-06-01", "periode_fin": "2026-09-07"},
    ).json()

    genere = client.post(f"/api/v1/revues/{revue['id']}/commentaire/generer", headers=_entete(responsable)).json()
    assert genere["commentaire_ia"] == "Texte pré-rédigé."
    assert genere["commentaire_valide"] is False

    valide = client.post(f"/api/v1/revues/{revue['id']}/commentaire/valider", headers=_entete(responsable)).json()
    assert valide["commentaire_valide"] is True

    modifie = client.patch(
        f"/api/v1/revues/{revue['id']}/commentaire", headers=_entete(responsable), json={"texte": "Réécrit à la main."}
    ).json()
    assert modifie["commentaire_ia"] == "Réécrit à la main."
    assert modifie["commentaire_valide"] is False
