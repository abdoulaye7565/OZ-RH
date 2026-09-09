"""Tests du socle du service d'assistance IA (prompt 6.1, chapitre 16 du CDC).

Aucune fonction métier n'existe encore (assistant documentaire, etc. : prompts
suivants) — ces tests couvrent l'infrastructure elle-même, en particulier les
deux garanties explicitement demandées : le service indisponible ne fait
échouer aucune fonctionnalité de l'application, et aucun secret ne peut être
transmis même si le code appelant le demande."""
import httpx
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models.appel_assistance import AppelAssistance
from app.models.enums import RoleUtilisateur
from app.models.utilisateur import Utilisateur
from app.services.assistance import client as assistance_client
from app.services.assistance import configuration, garde_fous, journal


@pytest.fixture()
def assistance_configuree(monkeypatch):
    monkeypatch.setattr(settings, "assistance_activee", True)
    monkeypatch.setattr(settings, "assistance_api_cle", "cle-de-test-sans-valeur-reelle")


# --- Le service indisponible ne fait échouer aucune fonctionnalité ---


def test_appel_sans_cle_api_ne_leve_pas_et_journalise(db_session, technicien):
    resultat = assistance_client.appeler(
        db_session, fonction="test", prompt="une question", utilisateur_id=technicien.id
    )
    assert resultat.disponible is False
    entree = db_session.scalars(select(AppelAssistance)).one()
    assert entree.succes is False
    assert entree.fonction == "test"


def test_appel_en_timeout_ne_leve_pas_d_exception(db_session, technicien, assistance_configuree, monkeypatch):
    def _post_qui_expire(*args, **kwargs):
        raise httpx.TimeoutException("délai dépassé (simulé)")

    monkeypatch.setattr(httpx, "post", _post_qui_expire)

    resultat = assistance_client.appeler(
        db_session, fonction="test", prompt="une question", utilisateur_id=technicien.id
    )

    assert resultat.disponible is False
    assert resultat.erreur is not None


def test_appel_en_echec_est_journalise_comme_echec(db_session, technicien, assistance_configuree, monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: (_ for _ in ()).throw(httpx.NetworkError("simulé")))

    assistance_client.appeler(db_session, fonction="assistant_documentaire", prompt="x", utilisateur_id=technicien.id)

    entree = db_session.scalars(select(AppelAssistance)).one()
    assert entree.succes is False
    assert entree.cout_estime_usd is None
    assert entree.fonction == "assistant_documentaire"


def test_appel_reussi_est_journalise_avec_un_cout_estime(db_session, technicien, assistance_configuree, monkeypatch):
    class ReponseFactice:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"type": "text", "text": "réponse"}], "usage": {"input_tokens": 100, "output_tokens": 20}}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: ReponseFactice())

    resultat = assistance_client.appeler(
        db_session, fonction="test", prompt="une question", utilisateur_id=technicien.id
    )

    assert resultat.disponible is True
    assert resultat.contenu == "réponse"
    entree = db_session.scalars(select(AppelAssistance)).one()
    assert entree.succes is True
    assert entree.cout_estime_usd is not None and entree.cout_estime_usd > 0


def test_retry_limite_a_deux_tentatives_maximum(db_session, technicien, assistance_configuree, monkeypatch):
    compteur = {"appels": 0}

    def _toujours_en_timeout(*args, **kwargs):
        compteur["appels"] += 1
        raise httpx.TimeoutException("simulé")

    monkeypatch.setattr(httpx, "post", _toujours_en_timeout)

    assistance_client.appeler(db_session, fonction="test", prompt="x", utilisateur_id=technicien.id)

    assert compteur["appels"] == 2  # 1 essai + 1 réessai, pas plus


# --- Aucun secret ne peut être transmis même si le code appelant le demande ---


def test_contenu_bytes_refuse_par_le_garde_fou():
    with pytest.raises(garde_fous.ContenuRefuseError):
        garde_fous.verifier_pas_de_secret(b"valeur chiffree du coffre-fort")


def test_appel_avec_un_contenu_bytes_refuse_avant_tout_appel_reseau(db_session, technicien, assistance_configuree, monkeypatch):
    appele = {"valeur": False}
    monkeypatch.setattr(httpx, "post", lambda *a, **k: appele.__setitem__("valeur", True))

    with pytest.raises(garde_fous.ContenuRefuseError):
        assistance_client.appeler(db_session, fonction="test", prompt=b"secret", utilisateur_id=technicien.id)

    assert appele["valeur"] is False  # jamais transmis au réseau
    assert db_session.scalars(select(AppelAssistance)).first() is None  # ni journalisé comme un appel


def test_contenu_texte_normal_accepte():
    garde_fous.verifier_pas_de_secret("une question tout à fait normale")  # ne lève rien


# --- Masquage des noms de personnes ---


def test_masquer_noms_remplace_les_utilisateurs_connus(db_session, site):
    utilisateur = Utilisateur(
        nom="Koné", prenom="Abdoulaye", identifiant="test.masquage",
        mot_de_passe="peu importe", role=RoleUtilisateur.TECHNICIEN, site_id=site.id,
    )
    db_session.add(utilisateur)
    db_session.commit()

    resultat = garde_fous.masquer_noms("Intervention réalisée par Abdoulaye Koné sur le site.", db_session)

    assert "Abdoulaye" not in resultat
    assert "Koné" not in resultat
    assert "[personne]" in resultat


def test_masquer_noms_sans_utilisateur_connu_ne_modifie_rien(db_session):
    texte = "Un texte quelconque sans nom particulier."
    assert garde_fous.masquer_noms(texte, db_session) == texte


# --- Activation par fonction ---


def test_fonction_desactivee_par_defaut():
    assert configuration.fonction_activee("assistant_documentaire") is False


def test_fonction_desactivee_si_interrupteur_general_off(monkeypatch):
    # `Settings` (Pydantic) refuse qu'on lui ajoute un champ non déclaré :
    # aucune fonction du lot 6 n'existe encore, donc aucun champ
    # `assistance_<fonction>_active` réel n'existe non plus (voir le
    # docstring de `fonction_activee`) — on simule sa présence en
    # remplaçant l'objet `settings` utilisé par `configuration.py` par un
    # double léger, plutôt que de forcer un champ sur le vrai singleton.
    faux_settings = type("FauxSettings", (), {"assistance_activee": False, "assistance_x_active": True})()
    monkeypatch.setattr(configuration, "settings", faux_settings)
    assert configuration.fonction_activee("x") is False


def test_fonction_activee_si_interrupteur_general_et_fonction_actifs(monkeypatch):
    faux_settings = type("FauxSettings", (), {"assistance_activee": True, "assistance_x_active": True})()
    monkeypatch.setattr(configuration, "settings", faux_settings)
    assert configuration.fonction_activee("x") is True


def test_fonction_non_essentielle_desactivee_si_plafond_depasse(db_session, technicien, monkeypatch):
    faux_settings = type(
        "FauxSettings", (),
        {"assistance_activee": True, "assistance_x_active": True, "assistance_plafond_mensuel_usd": 1.0},
    )()
    monkeypatch.setattr(configuration, "settings", faux_settings)
    journal.enregistrer_appel(
        db_session, fonction="x", utilisateur_id=technicien.id,
        volume_caracteres=10, duree_ms=100, cout_estime_usd=5.0, succes=True,
    )
    assert configuration.fonction_activee("x", db_session) is False


def test_fonction_essentielle_reste_activee_malgre_le_plafond(db_session, technicien, monkeypatch):
    faux_settings = type(
        "FauxSettings", (),
        {"assistance_activee": True, "assistance_x_active": True, "assistance_plafond_mensuel_usd": 1.0},
    )()
    monkeypatch.setattr(configuration, "settings", faux_settings)
    journal.enregistrer_appel(
        db_session, fonction="x", utilisateur_id=technicien.id,
        volume_caracteres=10, duree_ms=100, cout_estime_usd=5.0, succes=True,
    )
    assert configuration.fonction_activee("x", db_session, essentielle=True) is True


# --- Plafond mensuel ---


def test_plafond_non_depasse_sans_configuration(db_session):
    assert configuration.plafond_depasse(db_session) is False


def test_plafond_depasse_une_fois_le_seuil_atteint(db_session, technicien, monkeypatch):
    monkeypatch.setattr(settings, "assistance_plafond_mensuel_usd", 1.0)
    journal.enregistrer_appel(
        db_session, fonction="test", utilisateur_id=technicien.id,
        volume_caracteres=10, duree_ms=100, cout_estime_usd=1.5, succes=True,
    )
    assert configuration.plafond_depasse(db_session) is True


def test_plafond_depasse_alerte_les_administrateurs(db_session, technicien, administrateur, monkeypatch):
    from sqlalchemy import select as sa_select

    from app.models.enums import TypeNotification
    from app.models.notification import Notification

    monkeypatch.setattr(settings, "assistance_plafond_mensuel_usd", 1.0)
    journal.enregistrer_appel(
        db_session, fonction="test", utilisateur_id=technicien.id,
        volume_caracteres=10, duree_ms=100, cout_estime_usd=1.5, succes=True,
    )

    configuration.plafond_depasse(db_session)

    notif = db_session.scalars(
        sa_select(Notification).where(Notification.type == TypeNotification.PLAFOND_ASSISTANCE)
    ).one()
    assert notif.destinataire_id == administrateur.id

    # Un second appel le même mois ne recrée pas de notification (déduplication).
    configuration.plafond_depasse(db_session)
    total = db_session.scalars(
        sa_select(Notification).where(Notification.type == TypeNotification.PLAFOND_ASSISTANCE)
    ).all()
    assert len(total) == 1


def test_plafond_ignore_les_appels_en_echec(db_session, technicien, monkeypatch):
    monkeypatch.setattr(settings, "assistance_plafond_mensuel_usd", 0.01)
    journal.enregistrer_appel(
        db_session, fonction="test", utilisateur_id=technicien.id,
        volume_caracteres=10, duree_ms=100, cout_estime_usd=None, succes=False,
    )
    assert configuration.plafond_depasse(db_session) is False
