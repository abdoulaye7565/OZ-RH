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


def test_modules_non_disponibles_liste_seulement_ce_qui_manque_reellement(client, referent_sheq):
    """EPI, Inspections, Formations et Documents ont désormais un module
    réel (chantier du 2026-09-07) : ils calculent un indicateur, ils ne sont
    plus listés comme indisponibles. Seuls les incidents environnementaux et
    la sécurité des données (coffre-fort, toujours bloqué) le restent."""
    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    corps = reponse.json()
    assert set(corps["modules_non_disponibles"]) == {"incidents_environnementaux", "coffre_fort"}
    for module in ("epi", "inspections", "formations", "documents", "satisfaction"):
        assert module not in corps["modules_non_disponibles"]
        assert module in corps


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


# --- Indicateurs ajoutés le 2026-09-08 : EPI, Inspections, Formations,
# Documents, Satisfaction — chacun désormais un vrai module (voir
# docs/JOURNAL.md, "Documents en sous-dossiers réels + module Inspections"
# puis "Tableau de bord synchronisé aux données réelles").


def test_securite_compte_accidents_et_presque_accidents(client, db_session, technicien, referent_sheq, site):
    _creer_signalement(db_session, site, technicien, datetime.now(timezone.utc), statut=StatutSignalement.NOUVEAU)
    accident = Signalement(
        reference="SIG-2026-ACC1",
        type=TypeSignalement.ACCIDENT,
        site_id=site.id,
        lieu="Terrain",
        description="Chute",
        anonyme=False,
        auteur_id=technicien.id,
        date_constat=datetime.now(timezone.utc) - timedelta(days=5),
        date_saisie=datetime.now(timezone.utc) - timedelta(days=5),
        statut=StatutSignalement.CLOTURE,
    )
    presque = Signalement(
        reference="SIG-2026-PA1",
        type=TypeSignalement.PRESQUE_ACCIDENT,
        site_id=site.id,
        lieu="Terrain",
        description="Glissade évitée",
        anonyme=False,
        auteur_id=technicien.id,
        date_constat=datetime.now(timezone.utc),
        date_saisie=datetime.now(timezone.utc),
        statut=StatutSignalement.NOUVEAU,
    )
    db_session.add_all([accident, presque])
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    securite = reponse.json()["securite"]
    assert securite["accidents_periode"] == 1
    assert securite["presque_accidents_periode"] == 1
    assert securite["jours_sans_accident"] == 5


def test_securite_jours_sans_accident_nul_si_aucun_accident_jamais(client, referent_sheq):
    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    assert reponse.json()["securite"]["jours_sans_accident"] is None


def test_inspections_realisees_et_taux_conformite_moyen(client, db_session, technicien, referent_sheq, site):
    from app.models.inspection import Inspection

    cloturee = Inspection(
        modele="locaux",
        site_id=site.id,
        inspecteur_id=technicien.id,
        date=date.today(),
        points=[
            {"point_checklist_id": 1, "libelle": "Point A", "cotation": "C", "observation": None, "photo": None},
            {"point_checklist_id": 2, "libelle": "Point B", "cotation": "NC", "observation": None, "photo": None},
        ],
        statut="cloturee",
    )
    en_cours = Inspection(
        modele="incendie",
        site_id=site.id,
        inspecteur_id=technicien.id,
        date=date.today(),
        points=[{"point_checklist_id": 3, "libelle": "Point C", "cotation": "C", "observation": None, "photo": None}],
        statut="en_cours",
    )
    db_session.add_all([cloturee, en_cours])
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    inspections = reponse.json()["inspections"]
    # Seule la clôturée compte : 1 conforme / 2 cotés = 0.5.
    assert inspections["realisees_periode"] == 1
    assert inspections["taux_conformite_moyen"] == pytest.approx(0.5)


def test_epi_distingue_a_verifier_bientot_et_depasse(client, db_session, referent_sheq):
    from app.models.epi import Epi

    proche = Epi(
        numero="H-100",
        type="harnais",
        marque_modele="Test",
        date_mise_service=date.today() - timedelta(days=300),
        date_limite=date.today() + timedelta(days=2000),
        derniere_verification=date.today() - timedelta(days=360),
        prochaine_verification=date.today() + timedelta(days=5),
        statut="en_service",
    )
    depasse = Epi(
        numero="H-101",
        type="harnais",
        marque_modele="Test",
        date_mise_service=date.today() - timedelta(days=400),
        date_limite=date.today() + timedelta(days=2000),
        derniere_verification=date.today() - timedelta(days=400),
        prochaine_verification=date.today() - timedelta(days=30),
        statut="a_verifier",
    )
    db_session.add_all([proche, depasse])
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    epi = reponse.json()["epi"]
    assert epi["a_verifier_bientot"] == 1
    assert epi["verifications_depassees"] == 1


def test_documents_a_reviser_et_en_attente_approbation(client, db_session, referent_sheq, administrateur):
    from app.models.document import Document

    a_reviser = Document(
        reference="PRO-SHEQ-099",
        intitule="Procédure de test",
        niveau=3,
        version="01",
        redacteur_id=referent_sheq.id,
        approbateur_id=administrateur.id,
        statut="en_vigueur",
        date_revue=date.today() + timedelta(days=10),
        confidentialite="normal",
    )
    en_attente = Document(
        reference="PRO-SHEQ-098",
        intitule="Autre procédure",
        niveau=3,
        version="01",
        redacteur_id=referent_sheq.id,
        statut="en_approbation",
        confidentialite="normal",
    )
    db_session.add_all([a_reviser, en_attente])
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    documents = reponse.json()["documents"]
    assert documents["a_reviser_bientot"] == 1
    assert documents["en_attente_approbation"] == 1


def test_satisfaction_reclamations_et_note_moyenne(client, db_session, technicien, referent_sheq, site):
    from app.models.enquete_satisfaction import EnqueteSatisfaction
    from app.models.reponse_satisfaction import ReponseSatisfaction

    enquete = EnqueteSatisfaction(
        client="Client Test",
        site_id=site.id,
        intervention="Intervention test",
        technicien_id=technicien.id,
        envoyee_le=datetime.now(timezone.utc),
        repondu=True,
    )
    db_session.add(enquete)
    db_session.flush()
    reponse_faible = ReponseSatisfaction(
        enquete_id=enquete.id,
        notes=[{"critere": "Qualité", "note": 1}, {"critere": "Délais", "note": 2}],
        recommandation="non",
        necessite_analyse=True,
        date_reponse=datetime.now(timezone.utc),
    )
    db_session.add(reponse_faible)
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    satisfaction = reponse.json()["satisfaction"]
    assert satisfaction["reclamations_periode"] == 1
    assert satisfaction["note_moyenne"] == pytest.approx(1.5)


def test_echeances_proches_melange_actions_epi_documents_formations(client, db_session, referent_sheq, administrateur, technicien, site):
    from app.models.document import Document
    from app.models.epi import Epi
    from app.models.seance import Seance

    db_session.add(
        Epi(
            numero="H-200",
            type="harnais",
            marque_modele="Test",
            date_mise_service=date.today() - timedelta(days=300),
            date_limite=date.today() + timedelta(days=2000),
            derniere_verification=date.today() - timedelta(days=360),
            prochaine_verification=date.today() + timedelta(days=3),
            statut="en_service",
        )
    )
    db_session.add(
        Document(
            reference="PRO-SHEQ-097",
            intitule="Procédure échéance",
            niveau=3,
            version="01",
            redacteur_id=referent_sheq.id,
            approbateur_id=administrateur.id,
            statut="en_vigueur",
            date_revue=date.today() + timedelta(days=4),
            confidentialite="normal",
        )
    )
    db_session.add(
        Seance(
            theme="Sensibilisation sécurité",
            date=date.today() + timedelta(days=6),
            lieu="Siège",
            animateur_id=referent_sheq.id,
            statut="planifiee",
        )
    )
    db_session.commit()

    reponse = client.get("/api/v1/tableau-de-bord", headers=_entete(referent_sheq))
    echeances = reponse.json()["echeances_proches"]
    types = {e["type"] for e in echeances}
    assert "epi" in types
    assert "document" in types
    assert "formation" in types
    # Triées par proximité, pas par type ni par ordre d'insertion.
    dates_triees = [e["echeance"] for e in echeances]
    assert dates_triees == sorted(dates_triees)
