"""Tests de l'écran Paramètres (revue d'ensemble 2026-09-10 — retour direct
de l'utilisateur : "le système n'affiche pas tous les modules dans la barre
latérale" — le module manquant était Paramètres, présent dans la maquette
(id="p-param") mais jamais construit)."""
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_reserve_a_l_administrateur(client, technicien):
    reponse = client.get("/api/v1/parametres", headers=_entete(technicien))
    assert reponse.status_code == 403


def test_referentiels_reflètent_les_donnees_reelles(client, administrateur, site):
    reponse = client.get("/api/v1/parametres", headers=_entete(administrateur))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["referentiels"]["sites"] >= 1
    # Les totaux d'énumération sont fixes (12 catégories de risque réelles,
    # 5 modèles de checklist) — pas des valeurs inventées côté écran.
    assert corps["referentiels"]["categories_risque_total"] == 12
    assert corps["referentiels"]["modeles_checklist"] == 5


def test_etat_sauvegarde_sans_archive_encore_creee(client, administrateur, tmp_path, monkeypatch):
    """Avant la première exécution du job planifié, l'écran doit dire la
    vérité (aucune sauvegarde) plutôt qu'inventer une date."""
    from app.api.v1 import parametres as module_parametres

    monkeypatch.setattr(module_parametres.settings, "sauvegarde_dir", str(tmp_path / "aucune"))
    reponse = client.get("/api/v1/parametres", headers=_entete(administrateur))
    corps = reponse.json()
    assert corps["sauvegarde"]["nombre_archives"] == 0
    assert corps["sauvegarde"]["derniere"] is None


def test_etat_sauvegarde_reflete_une_archive_reelle(client, administrateur, tmp_path, monkeypatch):
    from app.api.v1 import parametres as module_parametres
    from app.services.sauvegarde_service import sauvegarder

    base = tmp_path / "base.sqlite3"
    import sqlite3

    cx = sqlite3.connect(base)
    cx.execute("CREATE TABLE t (id INTEGER)")
    cx.commit()
    cx.close()

    dossier = tmp_path / "sauvegardes"
    monkeypatch.setattr(module_parametres.settings, "sauvegarde_dir", str(dossier))
    monkeypatch.setattr("app.services.sauvegarde_service.settings.database_url", f"sqlite:///{base}")
    monkeypatch.setattr("app.services.sauvegarde_service.settings.storage_dir", str(tmp_path / "storage_absent"))
    sauvegarder(dossier, retention=14)

    reponse = client.get("/api/v1/parametres", headers=_entete(administrateur))
    corps = reponse.json()
    assert corps["sauvegarde"]["nombre_archives"] == 1
    assert corps["sauvegarde"]["derniere"]["type_base"] == "sqlite"
