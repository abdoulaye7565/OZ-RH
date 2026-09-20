"""Tests du module Notifications (prompt 4.4, chapitre 6.3 du CDC, tableau 3)."""
from datetime import date, datetime, timedelta, timezone

from app.core.security import creer_access_token
from app.models.action import Action
from app.models.enums import (
    CotationPoint,
    RoleUtilisateur,
    StatutDocument,
    StatutEpi,
    StatutInspection,
    TypeInspection,
    TypeMesureAction,
)
from app.models.epi import Epi
from app.models.document import Document
from app.models.inspection import Inspection


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


def test_nouveau_signalement_notifie_le_referent_sheq(client, technicien, referent_sheq, site):
    reponse = client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data={
            "type": "incident",
            "site_id": str(site.id),
            "lieu": "Pylône P12",
            "description": "Test notification.",
            "anonyme": "false",
            "date_constat": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert reponse.status_code == 201

    notifs = client.get("/api/v1/notifications", headers=_entete(referent_sheq)).json()
    assert len(notifs) == 1
    assert notifs[0]["type"] == "nouveau_signalement"
    assert notifs[0]["canal"] == "les_deux"
    # Aucun courriel configuré en test (SMTP_HOTE vide) : tentative journalisée
    # comme un échec explicite, jamais une réussite supposée.
    assert notifs[0]["courriel_envoye"] is False


def test_permis_en_attente_notifie_le_responsable(client, technicien, responsable, referent_sheq, site):
    # Contrôles automatiques : un SLAM GO du jour pour l'intervenant est requis
    # pour que le permis ne soit pas BLOQUE à la création (règle 1, CLAUDE.md) —
    # sans quoi aucune notification "en attente de validation" n'est émise.
    client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[True] * 4 for _ in range(4)], "decision": "GO"},
    )

    reponse = client.post(
        "/api/v1/permis",
        headers=_entete(technicien),
        json={
            "site_id": site.id,
            "nature_travaux": "Test",
            "support": "pylone",
            "intervenant_ids": [technicien.id],
            "surveillant_id": referent_sheq.id,
            # Créneau ancré à 08h-12h du jour même : `now() + 4h` seul basculait
            # au lendemain quand la suite tournait après 20h, ce qui déclenchait
            # légitimement la règle "un permis ne couvre qu'une seule journée"
            # (422) — test rendu instable, corrigé le 2026-09-10.
            "debut_validite": str(datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()),
            "fin_validite": str(datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()),
        },
    )
    assert reponse.status_code == 201
    assert reponse.json()["statut"] == "demande"

    notifs = client.get("/api/v1/notifications", headers=_entete(responsable)).json()
    assert any(n["type"] == "permis_en_attente" for n in notifs)


def test_decision_no_go_notifie_responsable_et_referent(client, technicien, responsable, referent_sheq):
    reponse = client.post(
        "/api/v1/slam",
        headers=_entete(technicien),
        json={"etapes_validees": [[False] * 4 for _ in range(4)], "decision": "NO_GO", "motif": "Vent fort"},
    )
    assert reponse.status_code == 201

    notifs_resp = client.get("/api/v1/notifications", headers=_entete(responsable)).json()
    notifs_ref = client.get("/api/v1/notifications", headers=_entete(referent_sheq)).json()
    assert any(n["type"] == "decision_no_go" for n in notifs_resp)
    assert any(n["type"] == "decision_no_go" for n in notifs_ref)


def test_compteur_et_marquage_lu(client, technicien, referent_sheq, site):
    client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data={
            "type": "incident", "site_id": str(site.id), "lieu": "X", "description": "Y",
            "anonyme": "false", "date_constat": datetime.now(timezone.utc).isoformat(),
        },
    )
    compteur = client.get("/api/v1/notifications/compteur", headers=_entete(referent_sheq)).json()
    assert compteur["non_lues"] == 1

    notif = client.get("/api/v1/notifications", headers=_entete(referent_sheq)).json()[0]
    client.post(f"/api/v1/notifications/{notif['id']}/lue", headers=_entete(referent_sheq))
    compteur = client.get("/api/v1/notifications/compteur", headers=_entete(referent_sheq)).json()
    assert compteur["non_lues"] == 0


def test_marquer_toutes_lues(client, technicien, referent_sheq, site):
    for _ in range(3):
        client.post(
            "/api/v1/signalements",
            headers=_entete(technicien),
            data={
                "type": "incident", "site_id": str(site.id), "lieu": "X", "description": "Y",
                "anonyme": "false", "date_constat": datetime.now(timezone.utc).isoformat(),
            },
        )
    assert client.get("/api/v1/notifications/compteur", headers=_entete(referent_sheq)).json()["non_lues"] == 3
    client.post("/api/v1/notifications/toutes-lues", headers=_entete(referent_sheq))
    assert client.get("/api/v1/notifications/compteur", headers=_entete(referent_sheq)).json()["non_lues"] == 0


def test_notification_invisible_a_un_autre_utilisateur(client, technicien, referent_sheq, responsable, site):
    client.post(
        "/api/v1/signalements",
        headers=_entete(technicien),
        data={
            "type": "incident", "site_id": str(site.id), "lieu": "X", "description": "Y",
            "anonyme": "false", "date_constat": datetime.now(timezone.utc).isoformat(),
        },
    )
    notif = client.get("/api/v1/notifications", headers=_entete(referent_sheq)).json()[0]
    reponse = client.post(f"/api/v1/notifications/{notif['id']}/lue", headers=_entete(responsable))
    assert reponse.status_code == 404


def test_technicien_ne_peut_pas_executer_les_taches_planifiees(client, technicien):
    reponse = client.post("/api/v1/notifications/executer-taches", headers=_entete(technicien))
    assert reponse.status_code == 403


def test_action_a_echeance_dans_sept_jours_notifiee(client, administrateur, referent_sheq, responsable, technicien, db_session):
    action = Action(
        libelle="Test action J-7",
        signalement_id=None,
        risque_id=None,
        inspection_id=None,
        type_mesure=TypeMesureAction.CORRECTIVE,
        responsable_id=technicien.id,
        echeance=date.today() + timedelta(days=7),
        cree_par_id=referent_sheq.id,
    )
    db_session.add(action)
    db_session.commit()

    rapport = client.post("/api/v1/notifications/executer-taches", headers=_entete(administrateur)).json()
    assert rapport["actions_notifiees"] == 1

    notifs = client.get("/api/v1/notifications", headers=_entete(technicien)).json()
    assert any(n["type"] == "action_echeance" for n in notifs)

    # Rejouer le job ne doit pas créer de doublon (déduplication).
    rapport_2 = client.post("/api/v1/notifications/executer-taches", headers=_entete(administrateur)).json()
    assert rapport_2["actions_notifiees"] == 0
    notifs_2 = client.get("/api/v1/notifications", headers=_entete(technicien)).json()
    assert len(notifs_2) == 1


def test_epi_verification_due_notifie_referent_et_porteur(client, administrateur, referent_sheq, technicien, db_session):
    epi = Epi(
        numero="H-999",
        type="harnais",
        marque_modele="Test",
        date_mise_service=date.today() - timedelta(days=358),
        date_limite=date.today().replace(year=date.today().year + 5),
        porteur_id=technicien.id,
        prochaine_verification=date.today() + timedelta(days=5),  # <= 7 jours
        statut=StatutEpi.EN_SERVICE,
        cree_par_id=referent_sheq.id,
    )
    db_session.add(epi)
    db_session.commit()

    rapport = client.post("/api/v1/notifications/executer-taches", headers=_entete(administrateur)).json()
    assert rapport["epi_notifies"] == 2  # référent SHEQ + porteur

    notifs_porteur = client.get("/api/v1/notifications", headers=_entete(technicien)).json()
    notifs_referent = client.get("/api/v1/notifications", headers=_entete(referent_sheq)).json()
    assert any(n["type"] == "epi_verification" for n in notifs_porteur)
    assert any(n["type"] == "epi_verification" for n in notifs_referent)


def test_document_a_reviser_notifie_le_referent(client, administrateur, referent_sheq, db_session):
    document = Document(
        reference="TEST-DOC-001",
        intitule="Document de test",
        niveau=3,
        version="01",
        redacteur_id=referent_sheq.id,
        statut=StatutDocument.EN_VIGUEUR,
        date_revue=date.today() + timedelta(days=20),  # <= 30 jours
        cree_par_id=referent_sheq.id,
    )
    db_session.add(document)
    db_session.commit()

    rapport = client.post("/api/v1/notifications/executer-taches", headers=_entete(administrateur)).json()
    assert rapport["documents_notifies"] == 1

    notifs = client.get("/api/v1/notifications", headers=_entete(referent_sheq)).json()
    assert any(n["type"] == "document_revue" for n in notifs)


def test_inspection_planifiee_notifie_le_dernier_inspecteur(client, administrateur, technicien, referent_sheq, site, db_session):
    from app.services.inspection_service import PERIODICITE_JOURS

    periodicite = PERIODICITE_JOURS[TypeInspection.LOCAUX]
    inspection = Inspection(
        modele=TypeInspection.LOCAUX,
        site_id=site.id,
        inspecteur_id=technicien.id,
        date=date.today() - timedelta(days=periodicite - 5),  # échéance dans 5 jours
        points=[{"point_checklist_id": 1, "libelle": "X", "cotation": CotationPoint.CONFORME.value, "observation": None, "photo": None}],
        statut=StatutInspection.CLOTUREE,
        cree_par_id=technicien.id,
    )
    db_session.add(inspection)
    db_session.commit()

    rapport = client.post("/api/v1/notifications/executer-taches", headers=_entete(administrateur)).json()
    assert rapport["inspections_notifiees"] == 1

    notifs = client.get("/api/v1/notifications", headers=_entete(technicien)).json()
    assert any(n["type"] == "inspection_planifiee" for n in notifs)
