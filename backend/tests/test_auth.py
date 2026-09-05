"""Tests de l'authentification (prompt 0.3)."""
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.security import creer_access_token, creer_refresh_token, verifier_mot_de_passe


def test_mot_de_passe_stocke_est_hache_avec_argon2(administrateur):
    assert administrateur.mot_de_passe.startswith("$argon2")
    assert administrateur.mot_de_passe != "UnMotDePasseSuffisammentSolide!42"


def test_connexion_reussie_renvoie_deux_jetons(client, administrateur, mot_de_passe_clair):
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": administrateur.identifiant, "mot_de_passe": mot_de_passe_clair},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert "access_token" in corps
    assert "refresh_token" in corps
    assert corps["token_type"] == "bearer"
    assert corps["access_token"] != corps["refresh_token"]


def test_connexion_met_a_jour_derniere_connexion(client, db_session, administrateur, mot_de_passe_clair):
    assert administrateur.derniere_connexion is None

    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": administrateur.identifiant, "mot_de_passe": mot_de_passe_clair},
    )

    db_session.refresh(administrateur)
    assert administrateur.derniere_connexion is not None


def test_connexion_mot_de_passe_incorrect_refusee(client, administrateur):
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": administrateur.identifiant, "mot_de_passe": "mauvais-mot-de-passe"},
    )
    assert reponse.status_code == 401


def test_connexion_identifiant_inconnu_refusee(client):
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "inconnu", "mot_de_passe": "peu-importe"},
    )
    assert reponse.status_code == 401


def test_moi_sans_jeton_refuse(client):
    reponse = client.get("/api/v1/auth/moi")
    assert reponse.status_code == 401


def test_moi_avec_jeton_valide(client, administrateur):
    jeton = creer_access_token(administrateur.id, administrateur.role.value)
    reponse = client.get("/api/v1/auth/moi", headers={"Authorization": f"Bearer {jeton}"})
    assert reponse.status_code == 200
    assert reponse.json()["identifiant"] == administrateur.identifiant


def test_moi_avec_jeton_invalide_refuse(client):
    reponse = client.get("/api/v1/auth/moi", headers={"Authorization": "Bearer ceci-nest-pas-un-jwt"})
    assert reponse.status_code == 401


def test_moi_avec_jeton_expire_refuse(client, administrateur):
    jeton_expire = jwt.encode(
        {
            "sub": str(administrateur.id),
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(minutes=30),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    reponse = client.get("/api/v1/auth/moi", headers={"Authorization": f"Bearer {jeton_expire}"})
    assert reponse.status_code == 401


def test_moi_avec_refresh_token_refuse(client, administrateur):
    """Un refresh token ne doit pas servir à s'authentifier directement — sinon
    autant n'avoir qu'un seul jeton, longue durée, qui voyage à chaque requête."""
    refresh = creer_refresh_token(administrateur.id)
    reponse = client.get("/api/v1/auth/moi", headers={"Authorization": f"Bearer {refresh}"})
    assert reponse.status_code == 401


def test_rafraichissement_avec_refresh_token_valide(client, administrateur):
    refresh = creer_refresh_token(administrateur.id)
    reponse = client.post("/api/v1/auth/rafraichissement", json={"refresh_token": refresh})
    assert reponse.status_code == 200
    assert "access_token" in reponse.json()


def test_rafraichissement_avec_access_token_refuse(client, administrateur):
    """Symétrique du test précédent : un access token ne doit pas non plus servir
    de refresh token."""
    access = creer_access_token(administrateur.id, administrateur.role.value)
    reponse = client.post("/api/v1/auth/rafraichissement", json={"refresh_token": access})
    assert reponse.status_code == 401


def test_administrateur_peut_creer_un_utilisateur(client, administrateur, mot_de_passe_clair, site):
    connexion = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": administrateur.identifiant, "mot_de_passe": mot_de_passe_clair},
    )
    jeton = connexion.json()["access_token"]

    reponse = client.post(
        "/api/v1/auth/utilisateurs",
        headers={"Authorization": f"Bearer {jeton}"},
        json={
            "nom": "Diarra",
            "prenom": "Oumou",
            "identifiant": "o.diarra",
            "mot_de_passe": "AutreMotDePasseSolide!17",
            "role": "referent_sheq",
            "site_id": site.id,
        },
    )

    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["identifiant"] == "o.diarra"
    assert "mot_de_passe" not in corps


def test_technicien_ne_peut_pas_creer_un_utilisateur(client, technicien, mot_de_passe_clair):
    """Cas de refus explicitement demandé par le prompt 0.3 : un technicien qui
    tente d'accéder à une route réservée à l'administrateur reçoit un 403."""
    connexion = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": technicien.identifiant, "mot_de_passe": mot_de_passe_clair},
    )
    jeton = connexion.json()["access_token"]

    reponse = client.post(
        "/api/v1/auth/utilisateurs",
        headers={"Authorization": f"Bearer {jeton}"},
        json={
            "nom": "Test",
            "prenom": "Test",
            "identifiant": "t.test",
            "mot_de_passe": "PeuImportePourCeTest!1",
            "role": "collaborateur",
        },
    )

    assert reponse.status_code == 403


def test_creer_utilisateur_sans_jeton_refuse(client):
    reponse = client.post(
        "/api/v1/auth/utilisateurs",
        json={
            "nom": "Test",
            "prenom": "Test",
            "identifiant": "t.test2",
            "mot_de_passe": "PeuImportePourCeTest!1",
            "role": "collaborateur",
        },
    )
    assert reponse.status_code == 401


def test_identifiant_deja_utilise_refuse(client, administrateur, mot_de_passe_clair):
    connexion = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": administrateur.identifiant, "mot_de_passe": mot_de_passe_clair},
    )
    jeton = connexion.json()["access_token"]

    reponse = client.post(
        "/api/v1/auth/utilisateurs",
        headers={"Authorization": f"Bearer {jeton}"},
        json={
            "nom": "Doublon",
            "prenom": "Doublon",
            "identifiant": administrateur.identifiant,
            "mot_de_passe": "PeuImportePourCeTest!1",
            "role": "collaborateur",
        },
    )
    assert reponse.status_code == 409


def test_compte_desactive_ne_peut_pas_se_connecter(client, db_session, administrateur, mot_de_passe_clair):
    administrateur.actif = False
    db_session.commit()

    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": administrateur.identifiant, "mot_de_passe": mot_de_passe_clair},
    )
    assert reponse.status_code == 401
