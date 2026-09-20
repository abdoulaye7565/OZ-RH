"""Tests de l'écran de gestion des rôles (revue d'ensemble 2026-09-10 —
retour direct de l'utilisateur : "je ne vois pas la gestion des rôles").

La matrice existait déjà dans app/core/permissions.py mais n'était exposée
par aucune route — ces tests vérifient qu'elle l'est désormais, fidèlement
(par introspection, pas une copie qui pourrait se désynchroniser)."""
from app.core.permissions import Permissions
from app.core.security import creer_access_token


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_ouvert_a_tout_utilisateur_authentifie(client, technicien):
    reponse = client.get("/api/v1/roles", headers=_entete(technicien))
    assert reponse.status_code == 200


def test_refuse_sans_authentification(client):
    assert client.get("/api/v1/roles").status_code == 401


def test_cinq_roles_avec_perimetre(client, administrateur):
    corps = client.get("/api/v1/roles", headers=_entete(administrateur)).json()
    assert len(corps["roles"]) == 5
    valeurs = {r["valeur"] for r in corps["roles"]}
    assert valeurs == {"administrateur", "referent_sheq", "responsable", "technicien", "collaborateur"}
    assert all(r["perimetre"] for r in corps["roles"])


def test_permissions_refletent_reellement_permissions_py(client, administrateur):
    """Ce test échouerait si l'écran se mettait à recopier une liste figée au
    lieu de lire `Permissions` par introspection — garde-fou contre la
    désynchronisation qui a justifié cette revue."""
    corps = client.get("/api/v1/roles", headers=_entete(administrateur)).json()
    cles_api = {p["cle"] for p in corps["permissions"]}
    cles_reelles = {
        cle for cle, valeur in vars(Permissions).items() if not cle.startswith("_") and isinstance(valeur, tuple)
    }
    assert cles_api == cles_reelles

    gerer_utilisateurs = next(p for p in corps["permissions"] if p["cle"] == "GERER_UTILISATEURS")
    assert gerer_utilisateurs["roles"] == ["administrateur"]

    valider_permis = next(p for p in corps["permissions"] if p["cle"] == "VALIDER_PERMIS")
    assert set(valider_permis["roles"]) == {"responsable", "administrateur"}
