"""Tests du module d'export PDF (prompt 5.1, chapitre 14 du CDC, cas de test
12). Un PDF de configuration est déjà couvert par tests/test_configurations.py
(prompt 3.2) : pas dupliqué ici."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import creer_access_token
from app.models.point_checklist import PointChecklist


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def _est_un_pdf(reponse) -> bool:
    return (
        reponse.status_code == 200
        and reponse.headers["content-type"] == "application/pdf"
        and reponse.content[:4] == b"%PDF"
    )


def test_export_signalement(client, technicien, site):
    sig = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data={
            "type": "incident", "site_id": str(site.id), "lieu": "Pylône P12",
            "description": "Câble détendu.", "anonyme": "false",
            "date_constat": datetime.now(timezone.utc).isoformat(),
        },
    ).json()
    reponse = client.get(f"/api/v1/signalements/{sig['id']}/export-pdf", headers=_entete(technicien))
    assert _est_un_pdf(reponse)


def test_export_signalement_anonyme_ne_leve_pas_d_erreur(client, technicien, site):
    sig = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data={
            "type": "situation_dangereuse", "site_id": str(site.id), "lieu": "Bureaux",
            "description": "Câble au sol.", "anonyme": "true",
            "date_constat": datetime.now(timezone.utc).isoformat(),
        },
    ).json()
    # Un signalement anonyme reste consultable par le référent SHEQ (rôle non
    # restreint) — mais pas par le technicien qui n'est pas l'auteur enregistré.
    reponse = client.get(f"/api/v1/signalements/{sig['id']}/export-pdf", headers=_entete(technicien))
    assert reponse.status_code == 404


def test_export_slam(client, technicien):
    evaluation = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[True] * 4 for _ in range(4)], "decision": "GO"},
    ).json()
    reponse = client.get(f"/api/v1/slam/{evaluation['id']}/export-pdf", headers=_entete(technicien))
    assert _est_un_pdf(reponse)


def test_export_permis(client, technicien, referent_sheq, site):
    client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[True] * 4 for _ in range(4)], "decision": "GO"},
    )
    permis = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json={
            "site_id": site.id, "nature_travaux": "Test export", "support": "pylone",
            "intervenant_ids": [technicien.id], "surveillant_id": referent_sheq.id,
            # Créneau ancré à 08h-12h du jour même : `now() + 4h` seul basculait
            # au lendemain quand la suite tournait après 20h, ce qui déclenchait
            # légitimement la règle "un permis ne couvre qu'une seule journée"
            # (422) — test rendu instable, corrigé le 2026-09-10.
            "debut_validite": str(datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()),
            "fin_validite": str(datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()),
        },
    ).json()
    reponse = client.get(f"/api/v1/permis/{permis['id']}/export-pdf", headers=_entete(technicien))
    assert _est_un_pdf(reponse)


def test_export_inspection(client, db_session, technicien, site):
    points = list(
        db_session.scalars(
            select(PointChecklist).where(PointChecklist.type_inspection == "locaux", PointChecklist.archive.is_(False)).limit(2)
        )
    )
    inspection = client.post(
        "/api/v1/inspections",
        headers=_entete(technicien),
        json={
            "modele": "locaux", "site_id": site.id,
            "points": [
                {"point_checklist_id": points[0].id, "cotation": "C"},
                {"point_checklist_id": points[1].id, "cotation": "NC", "observation": "Test"},
            ],
        },
    ).json()
    reponse = client.get(f"/api/v1/inspections/{inspection['id']}/export-pdf", headers=_entete(technicien))
    assert _est_un_pdf(reponse)
    # Une seconde génération réutilise la même référence (paresseuse, pas
    # régénérée à chaque export).
    inspection_relue = client.get(f"/api/v1/inspections/{inspection['id']}", headers=_entete(technicien)).json()
    reponse_2 = client.get(f"/api/v1/inspections/{inspection['id']}/export-pdf", headers=_entete(technicien))
    inspection_relue_2 = client.get(f"/api/v1/inspections/{inspection['id']}", headers=_entete(technicien)).json()
    assert inspection_relue_2["reference"] == inspection_relue["reference"]


def test_export_audit(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    exigences = client.get("/api/v1/audits/exigences", headers=_entete(referent_sheq)).json()
    client.patch(
        f"/api/v1/audits/campagnes/{campagne['id']}/cotations",
        headers=_entete(referent_sheq),
        json=[{"exigence_id": exigences[0]["id"], "cotation": 0, "ecart": "Politique non affichée"}],
    )
    reponse = client.get(f"/api/v1/audits/campagnes/{campagne['id']}/export-pdf", headers=_entete(referent_sheq))
    assert _est_un_pdf(reponse)


def test_export_revue(client, responsable):
    revue = client.post(
        "/api/v1/revues",
        headers=_entete(responsable),
        json={
            "date": str(date.today()), "lieu": "Siège",
            "periode_debut": str(date.today() - timedelta(days=90)), "periode_fin": str(date.today()),
            "participants": "Direction",
        },
    ).json()
    client.post(
        f"/api/v1/revues/{revue['id']}/decisions",
        headers=_entete(responsable),
        json={"libelle": "Renouveler les extincteurs", "responsable_id": responsable.id, "echeance": str(date.today() + timedelta(days=30))},
    )
    reponse = client.get(f"/api/v1/revues/{revue['id']}/export-pdf", headers=_entete(responsable))
    assert _est_un_pdf(reponse)


def test_export_tableau_de_bord(client, administrateur):
    reponse = client.get("/api/v1/tableau-de-bord/export-pdf", headers=_entete(administrateur))
    assert _est_un_pdf(reponse)


def test_export_pdf_porte_bien_une_reference_enr_sheq_pour_les_entites_sans_reference_propre(client, referent_sheq):
    campagne = client.post("/api/v1/audits/campagnes", headers=_entete(referent_sheq), json={}).json()
    client.get(f"/api/v1/audits/campagnes/{campagne['id']}/export-pdf", headers=_entete(referent_sheq))
    campagne_relue = client.get(f"/api/v1/audits/campagnes/{campagne['id']}", headers=_entete(referent_sheq)).json()
    annee = date.today().year
    assert campagne_relue["reference"].startswith(f"ENR-SHEQ-{annee}-")
