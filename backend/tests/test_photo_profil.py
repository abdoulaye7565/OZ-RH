"""Tests de la photo de profil (2026-09-10, retour direct de l'utilisateur —
"permettre à l'utilisateur d'insérer sa photo lors de la connexion", compris
comme un ajout en libre-service une fois connecté)."""
import io

from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _fichier_jpeg(nom="moi.jpg"):
    return {"photo": (nom, io.BytesIO(b"\xff\xd8\xff-contenu-jpeg-factice"), "image/jpeg")}


def test_deposer_sa_photo(client, technicien, tmp_path, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))

    reponse = client.post("/api/v1/auth/moi/photo", headers=_entete(technicien), files=_fichier_jpeg())
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["photo"] is not None
    assert corps["id"] == technicien.id

    # Le fichier existe réellement sur disque, hors base (point 9 CDC).
    assert (tmp_path / corps["photo"]).is_file()


def test_photo_accessible_via_la_route_dediee(client, technicien, tmp_path, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))

    client.post("/api/v1/auth/moi/photo", headers=_entete(technicien), files=_fichier_jpeg())
    reponse = client.get(f"/api/v1/auth/utilisateurs/{technicien.id}/photo", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert reponse.content == b"\xff\xd8\xff-contenu-jpeg-factice"


def test_sans_photo_la_route_renvoie_404(client, technicien, referent_sheq):
    reponse = client.get(f"/api/v1/auth/utilisateurs/{technicien.id}/photo", headers=_entete(referent_sheq))
    assert reponse.status_code == 404


def test_remplacer_la_photo_supprime_l_ancien_fichier(client, technicien, tmp_path, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))

    premiere = client.post(
        "/api/v1/auth/moi/photo", headers=_entete(technicien), files=_fichier_jpeg("premiere.jpg")
    ).json()
    chemin_premiere = tmp_path / premiere["photo"]
    assert chemin_premiere.is_file()

    seconde = client.post(
        "/api/v1/auth/moi/photo", headers=_entete(technicien), files=_fichier_jpeg("seconde.jpg")
    ).json()
    assert seconde["photo"] != premiere["photo"]
    assert not chemin_premiere.exists()  # l'ancien fichier orphelin est nettoyé
    assert (tmp_path / seconde["photo"]).is_file()


def test_retirer_sa_photo(client, technicien, tmp_path, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))

    client.post("/api/v1/auth/moi/photo", headers=_entete(technicien), files=_fichier_jpeg())
    reponse = client.post("/api/v1/auth/moi/photo/retirer", headers=_entete(technicien))
    assert reponse.status_code == 200
    assert reponse.json()["photo"] is None

    apres = client.get(f"/api/v1/auth/utilisateurs/{technicien.id}/photo", headers=_entete(technicien))
    assert apres.status_code == 404


def test_type_de_fichier_non_image_refuse(client, technicien):
    fichier = {"photo": ("document.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
    reponse = client.post("/api/v1/auth/moi/photo", headers=_entete(technicien), files=fichier)
    assert reponse.status_code == 400


def test_on_ne_peut_deposer_que_sa_propre_photo(client, technicien, referent_sheq, tmp_path, monkeypatch):
    """Aucune route ne prend d'`utilisateur_id` en paramètre pour le dépôt —
    seule /moi/photo existe : impossible par construction de déposer la photo
    de quelqu'un d'autre."""
    from app.core import config

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))

    reponse = client.post("/api/v1/auth/moi/photo", headers=_entete(technicien), files=_fichier_jpeg())
    assert reponse.json()["id"] == technicien.id
    assert reponse.json()["id"] != referent_sheq.id


def test_route_photo_exige_une_authentification(client, technicien):
    assert client.get(f"/api/v1/auth/utilisateurs/{technicien.id}/photo").status_code == 401
    assert client.post("/api/v1/auth/moi/photo", files=_fichier_jpeg()).status_code == 401
