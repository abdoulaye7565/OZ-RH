"""Tests du tableau de bord (prompt 1.5)."""
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import event

from app.core.security import creer_access_token
from app.models.action import Action
from app.models.cotation_risque import CotationRisque
from app.models.enums import (
    CategorieRisque,
    NiveauRisque,
    StatutAction,
    StatutSignalement,
    TypeMesureAction,
    TypeSignalement,
)
from app.models.risque import Risque
from app.models.signalement import Signalement


def _entete(utilisateur):
    jeton = creer_access_token(utilisateur.id, utilisateur.role.value)
    return {"Authorization": f"Bearer {jeton}"}


_compteur_reference = 0


def _creer_signalement(db, site, technicien, quand: datetime, statut=StatutSignalement.NOUVEAU):
    global _compteur_reference
    _compteur_reference += 1
    s = Signalement(
        reference=f"SIG-{quand.year}-{_compteur_reference:04d}",
        type=TypeSignalement.INCIDENT,
        site_id=site.id,
        lieu="Test",
        description="Test",
        anonyme=False,
        auteur_id=technicien.id,
        date_constat=quand,
        date_saisie=quand,
        statut=statut,
    )
    db.add(s)
    db.commit()
    return s


def test_tableau_de_bord_agrege_les_signalements_par_mois(client, db_session, technicien, referent_sheq, site):
    _creer_signalement(db_session, site, technicien, datetime(2026, 7, 10, tzinfo=timezone.utc))
    _creer_signalement(db_session, site, technicien, datetime(2026, 7, 15, tzinfo=timezone.utc))
    _creer_signalement(db_session, site, technicien, datetime(2026, 8, 1, tzinfo=timezone.utc))

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    assert reponse.status_code == 200
    corps = reponse.json()

    par_mois = {(p["annee"], p["mois"]): p["nombre"] for p in corps["signalements"]["par_mois"]}
    assert par_mois[(2026, 7)] == 2
    assert par_mois[(2026, 8)] == 1
    assert corps["signalements"]["total_periode"] == 3


def test_signalements_a_traiter_exclut_les_clotures(client, db_session, technicien, referent_sheq, site):
    _creer_signalement(db_session, site, technicien, datetime.now(timezone.utc), statut=StatutSignalement.NOUVEAU)
    _creer_signalement(db_session, site, technicien, datetime.now(timezone.utc), statut=StatutSignalement.EN_ANALYSE)
    _creer_signalement(db_session, site, technicien, datetime.now(timezone.utc), statut=StatutSignalement.CLOTURE)

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    corps = reponse.json()
    assert corps["signalements"]["nombre_a_traiter"] == 2
    statuts = {s["statut"] for s in corps["signalements"]["a_traiter"]}
    assert statuts == {"nouveau", "en_analyse"}


def test_filtre_periode(client, db_session, technicien, referent_sheq, site):
    _creer_signalement(db_session, site, technicien, datetime(2026, 1, 1, tzinfo=timezone.utc))
    _creer_signalement(db_session, site, technicien, datetime(2026, 6, 1, tzinfo=timezone.utc))

    reponse = client.get(
        "/api/v1/tableau-de-bord?date_debut=2026-05-01T00:00:00Z&date_fin=2026-12-31T23:59:59Z",
        headers=_entete(referent_sheq),
    )
    corps = reponse.json()
    assert corps["signalements"]["total_periode"] == 1


def test_filtre_site(client, db_session, technicien, referent_sheq, site):
    from app.models.site import Site
    from app.models.enums import TypeSite

    autre_site = Site(nom="Autre site", type=TypeSite.CLIENT)
    db_session.add(autre_site)
    db_session.commit()

    _creer_signalement(db_session, site, technicien, datetime.now(timezone.utc))
    _creer_signalement(db_session, autre_site, technicien, datetime.now(timezone.utc))

    reponse = client.get(f"/api/v1/tableau-de-bord?site_id={site.id}", headers=_entete(referent_sheq))
    corps = reponse.json()
    assert corps["signalements"]["total_periode"] == 1
    assert corps["site_id"] == site.id


def test_modules_non_disponibles_liste_ce_qui_manque(client, referent_sheq):
    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    corps = reponse.json()
    for module in ("epi", "inspections", "formations", "documents"):
        assert module in corps["modules_non_disponibles"]


def test_technicien_ne_peut_pas_consulter_le_tableau_de_bord(client, technicien):
    """Le tableau agrège TOUS les signalements, pas seulement les siens."""
    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(technicien))
    assert reponse.status_code == 403


@pytest.fixture()
def risque(db_session, referent_sheq):
    r = Risque(
        numero=1,
        danger="Chute",
        categorie=CategorieRisque.CHUTE_CIRCULATION,
        unite_travail="Terrain",
        cree_par_id=referent_sheq.id,
    )
    db_session.add(r)
    db_session.flush()
    db_session.add(
        CotationRisque(
            risque_id=r.id,
            probabilite=3,
            gravite=5,
            criticite=15,
            niveau=NiveauRisque.CRITIQUE,
            mesures_proposees="Harnais",
            date_evaluation=date.today(),
            auteur_id=referent_sheq.id,
            cree_par_id=referent_sheq.id,
        )
    )
    db_session.commit()
    return r


def test_actions_en_retard_et_echeances_proches(client, db_session, referent_sheq, risque):
    en_retard = Action(
        libelle="Action en retard",
        risque_id=risque.id,
        type_mesure=TypeMesureAction.CORRECTIVE,
        responsable_id=referent_sheq.id,
        echeance=date.today() - timedelta(days=3),
        statut=StatutAction.OUVERTE,
    )
    proche = Action(
        libelle="Action proche",
        risque_id=risque.id,
        type_mesure=TypeMesureAction.CORRECTIVE,
        responsable_id=referent_sheq.id,
        echeance=date.today() + timedelta(days=5),
        statut=StatutAction.OUVERTE,
    )
    lointaine = Action(
        libelle="Action lointaine",
        risque_id=risque.id,
        type_mesure=TypeMesureAction.CORRECTIVE,
        responsable_id=referent_sheq.id,
        echeance=date.today() + timedelta(days=90),
        statut=StatutAction.OUVERTE,
    )
    db_session.add_all([en_retard, proche, lointaine])
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    corps = reponse.json()

    assert corps["actions"]["nombre_en_retard"] == 1
    libelles_echeances = {a["libelle"] for a in corps["echeances_proches"]}
    assert "Action en retard" in libelles_echeances
    assert "Action proche" in libelles_echeances
    assert "Action lointaine" not in libelles_echeances


def test_aggregation_actions_utilise_group_by_pas_un_chargement_complet(db_session, referent_sheq, risque):
    """Vérifie que calculer_synthese émet des requêtes agrégées (GROUP BY / COUNT),
    pas un SELECT * chargeant toutes les lignes puis comptant en Python."""
    from app.services.action_service import calculer_synthese

    for i in range(5):
        db_session.add(
            Action(
                libelle=f"Action {i}",
                risque_id=risque.id,
                type_mesure=TypeMesureAction.CORRECTIVE,
                responsable_id=referent_sheq.id,
                echeance=date.today() + timedelta(days=10),
                statut=StatutAction.OUVERTE,
            )
        )
    db_session.commit()

    requetes = []
    def _capturer(conn, cursor, statement, parameters, context, executemany):
        requetes.append(statement)

    engine = db_session.get_bind()
    event.listen(engine, "before_cursor_execute", _capturer)
    try:
        calculer_synthese(db_session)
    finally:
        event.remove(engine, "before_cursor_execute", _capturer)

    requetes_select = [r for r in requetes if r.strip().upper().startswith("SELECT")]
    assert len(requetes_select) == 2, f"Attendu 2 requêtes agrégées, obtenu {len(requetes_select)} : {requetes_select}"
    for r in requetes_select:
        assert "GROUP BY" in r.upper() or "COUNT" in r.upper()
        assert "action.id" not in r.lower() or "count" in r.lower()
