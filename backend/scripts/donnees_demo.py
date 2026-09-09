"""Jeu de données de démonstration (prompt 5.3) — données fictives uniquement
(CLAUDE.md, point 10), inspirées des données réelles utilisées comme référence
de conception (docs/formulaires/) mais aucune n'en est issue.

Peuple une base VIDE via l'API réelle (comme le ferait un utilisateur), pas par
insertion SQL directe : chaque enregistrement passe par les mêmes règles
métier et validations que la vraie application. Seuls les 2 sites et le
premier compte administrateur sont créés en base directement, faute de route
API pour le premier (aucune route `/sites` n'existe, cf. docs/JOURNAL.md,
prompt 5.3) et par nécessité pour le second (`POST /auth/utilisateurs`
exige déjà un administrateur authentifié — amorçage impossible autrement).

Usage :
    python scripts/donnees_demo.py

Refuse de s'exécuter si la base contient déjà des utilisateurs (garde-fou
contre un lancement accidentel sur une base en service — règle 2, CLAUDE.md :
on n'écrase jamais de données existantes)."""
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402

settings.scheduler_actif = False  # même précaution que tests/conftest.py

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.core.security import hacher_mot_de_passe  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.enums import RoleUtilisateur, TypeSite  # noqa: E402
from app.models.site import Site  # noqa: E402
from app.models.utilisateur import Utilisateur  # noqa: E402

MOT_DE_PASSE_DEMO = "Demo-SHEQ-2026!"


def _bootstrap_sites_et_admin() -> tuple[Site, Site, Utilisateur]:
    Base.metadata.create_all(engine)  # sans effet si `alembic upgrade head` a déjà été exécuté
    db = SessionLocal()
    try:
        if db.scalar(select(Utilisateur).limit(1)) is not None:
            print("La base contient déjà des utilisateurs — arrêt (pas de double semis).", file=sys.stderr)
            sys.exit(1)

        siege = Site(nom="Siège Bamako", type=TypeSite.SIEGE, adresse="Hamdallaye ACI 2000, Bamako")
        client_site = Site(nom="Pylône Orange Kalabancoro", type=TypeSite.CLIENT, adresse="Kalabancoro, Bamako")
        db.add_all([siege, client_site])
        db.commit()

        admin = Utilisateur(
            nom="Traoré", prenom="Alassane", identifiant="a.traore",
            mot_de_passe=hacher_mot_de_passe(MOT_DE_PASSE_DEMO),
            role=RoleUtilisateur.ADMINISTRATEUR, site_id=siege.id, courriel="a.traore@hirondelles-it-lab.ml",
        )
        db.add(admin)
        db.commit()
        db.refresh(siege)
        db.refresh(client_site)
        db.refresh(admin)
        return siege, client_site, admin
    finally:
        db.close()


class Session_:
    """Petit assistant : un utilisateur + son jeton, pour lisibilité des appels ci-dessous."""

    def __init__(self, client: TestClient, identifiant: str, mot_de_passe: str):
        reponse = client.post("/api/v1/auth/connexion", json={"identifiant": identifiant, "mot_de_passe": mot_de_passe})
        reponse.raise_for_status()
        self.jeton = reponse.json()["access_token"]
        self.client = client

    def _entete(self) -> dict:
        return {"Authorization": f"Bearer {self.jeton}"}

    def get(self, url, **kw):
        return self.client.get(url, headers=self._entete(), **kw)

    def post(self, url, **kw):
        return self.client.post(url, headers=self._entete(), **kw)

    def patch(self, url, **kw):
        return self.client.patch(url, headers=self._entete(), **kw)


def _verifier(reponse, contexte: str) -> dict:
    if reponse.status_code >= 400:
        print(f"ÉCHEC — {contexte} : {reponse.status_code} {reponse.text}", file=sys.stderr)
        reponse.raise_for_status()
    print(f"OK — {contexte}")
    return reponse.json()


def peupler() -> None:
    siege, client_site, admin = _bootstrap_sites_et_admin()

    with TestClient(app) as client:
        admin_s = Session_(client, "a.traore", MOT_DE_PASSE_DEMO)

        # --- Utilisateurs (un par rôle a minima, section 6 de CLAUDE.md) ---
        utilisateurs = {}
        for identifiant, nom, prenom, role, site in [
            ("o.diarra", "Diarra", "Oumou", RoleUtilisateur.REFERENT_SHEQ, siege),
            ("f.traore", "Traoré", "Fatoumata", RoleUtilisateur.RESPONSABLE, siege),
            ("a.kone", "Koné", "Abdoulaye", RoleUtilisateur.TECHNICIEN, siege),
            ("s.diallo", "Diallo", "Seydou", RoleUtilisateur.TECHNICIEN, client_site),
            ("m.sangare", "Sangaré", "Mariam", RoleUtilisateur.COLLABORATEUR, siege),
        ]:
            corps = _verifier(
                admin_s.post(
                    "/api/v1/auth/utilisateurs",
                    json={
                        "nom": nom, "prenom": prenom, "identifiant": identifiant,
                        "mot_de_passe": MOT_DE_PASSE_DEMO, "role": role.value, "site_id": site.id,
                        "courriel": f"{identifiant}@hirondelles-it-lab.ml",
                    },
                ),
                f"création utilisateur {prenom} {nom} ({role.value})",
            )
            utilisateurs[identifiant] = corps

        referent_s = Session_(client, "o.diarra", MOT_DE_PASSE_DEMO)
        responsable_s = Session_(client, "f.traore", MOT_DE_PASSE_DEMO)
        technicien_s = Session_(client, "a.kone", MOT_DE_PASSE_DEMO)
        technicien2_s = Session_(client, "s.diallo", MOT_DE_PASSE_DEMO)
        technicien_id = utilisateurs["a.kone"]["id"]

        # --- Risques (registre, section 5.2.5) : un par niveau pour démontrer
        # le code couleur (faible/modéré/élevé/critique, point 8 CLAUDE.md) ---
        for danger, categorie, unite, proba, gravite, mesures in [
            ("Chute de hauteur lors d'une montée sur pylône", "Chute / Circulation", "Techniciens terrain", 2, 2,
             "Port du harnais et de la longe obligatoire, vérifié avant chaque intervention"),
            ("Contact électrique lors d'une intervention sur armoire", "Électrique", "Techniciens terrain", 2, 4,
             "Consignation systématique avant intervention, EPI isolants"),
            ("Effondrement de pylône par corrosion non détectée", "Chute / Circulation", "Techniciens terrain", 2, 5,
             "Inspection visuelle trimestrielle, plan de maintenance préventive"),
            ("Troubles musculo-squelettiques (port de charges)", "Ergonomique", "Techniciens terrain", 3, 2,
             "Formation gestes et postures, matériel de manutention"),
        ]:
            _verifier(
                referent_s.post(
                    "/api/v1/risques",
                    json={
                        "danger": danger, "categorie": categorie, "unite_travail": unite,
                        "cotation": {
                            "probabilite": proba, "gravite": gravite,
                            "mesures_proposees": mesures, "date_evaluation": str(date.today()),
                        },
                    },
                ),
                f"création risque « {danger[:40]}... »",
            )

        # --- EPI (section 5.3.2) ---
        epi = _verifier(
            referent_s.post(
                "/api/v1/epi",
                json={
                    "type": "harnais", "marque_modele": "Petzl Avao Bod",
                    "date_mise_service": str(date.today() - timedelta(days=200)),
                    "date_limite": str(date.today() + timedelta(days=1600)),
                    "porteur_id": technicien_id,
                },
            ),
            "création EPI (harnais)",
        )
        _verifier(
            referent_s.post(f"/api/v1/epi/{epi['id']}/verification-periodique", json={"conforme": True}),
            "vérification périodique EPI",
        )

        # --- Équipements + fiche de configuration (section 5.2.3) ---
        equipement = _verifier(
            technicien_s.post(
                "/api/v1/equipements",
                json={
                    "identity": "KAL-ST-01",
                    "marque": "MikroTik", "modele": "hAP ac2", "numero_serie": "MK-DEMO-0001",
                    "site_id": client_site.id, "emplacement": "Local technique",
                    "date_installation": str(date.today() - timedelta(days=400)),
                },
            ),
            "création équipement (MikroTik)",
        )
        _verifier(
            technicien_s.post(
                "/api/v1/configurations",
                data={
                    "equipement_id": str(equipement["id"]), "type_intervention": "installation",
                    "version_logicielle": "RouterOS 7.15",
                    "parametres_reseau": '{"adresse_ip_masque": "10.10.0.1/24", "dhcp_serveur": "actif"}',
                    "parametres_sansfil": '{"mode": "station", "frequence": "5180 MHz", "protocole": "802.11ac"}',
                    "signal_dbm": "-58", "ccq_pourcent": "92",
                },
            ),
            "création fiche de configuration",
        )

        # --- Signalements (un normal, un anonyme) ---
        _verifier(
            technicien_s.post(
                "/api/v1/signalements",
                data={
                    "type": "situation_dangereuse", "site_id": str(client_site.id),
                    "lieu": "Pied du pylône", "description": "Portail d'accès au site resté ouvert la nuit.",
                    "anonyme": "false", "date_constat": datetime.now(timezone.utc).isoformat(),
                },
            ),
            "création signalement (situation dangereuse)",
        )
        _verifier(
            technicien2_s.post(
                "/api/v1/signalements",
                data={
                    "type": "presque_accident", "site_id": str(siege.id),
                    "lieu": "Escalier du siège", "description": "Marche descellée, quasi-chute évitée de justesse.",
                    "anonyme": "true", "date_constat": datetime.now(timezone.utc).isoformat(),
                },
            ),
            "création signalement (anonyme)",
        )

        # --- SLAM + Permis (règle de blocage, section 5.2.2) ---
        _verifier(
            technicien_s.post("/api/v1/slam", json={"etapes_validees": [[True] * 4 for _ in range(4)], "decision": "GO"}),
            "évaluation SLAM (GO) — a.kone",
        )
        permis = _verifier(
            technicien_s.post(
                "/api/v1/permis",
                json={
                    "site_id": client_site.id, "nature_travaux": "Remplacement d'antenne secteur",
                    "support": "pylone", "hauteur_estimee": 24,
                    "intervenant_ids": [technicien_id], "surveillant_id": utilisateurs["o.diarra"]["id"],
                    "debut_validite": datetime.now(timezone.utc).isoformat(),
                    "fin_validite": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
                },
            ),
            "demande de permis de travail",
        )
        _verifier(responsable_s.post(f"/api/v1/permis/{permis['id']}/valider"), "validation du permis")

        # Second technicien SANS évaluation SLAM : démontre le blocage.
        permis_bloque = _verifier(
            technicien2_s.post(
                "/api/v1/permis",
                json={
                    "site_id": siege.id, "nature_travaux": "Intervention toiture — sans SLAM préalable (démo blocage)",
                    "support": "toiture", "intervenant_ids": [utilisateurs["s.diallo"]["id"]],
                    "surveillant_id": utilisateurs["o.diarra"]["id"],
                    "debut_validite": datetime.now(timezone.utc).isoformat(),
                    "fin_validite": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
                },
            ),
            "demande de permis (démonstration de la règle de blocage — SLAM absent)",
        )
        reponse_validation = responsable_s.post(f"/api/v1/permis/{permis_bloque['id']}/valider")
        print(f"   -> tentative de validation : {reponse_validation.status_code} "
              f"(statut attendu : bloqué par la règle métier, motif détaillé dans la réponse)")

        # --- Inspection (checklist réelle FOR-SHEQ-005/010/011, seedée par migration) ---
        points = referent_s.get("/api/v1/points-checklist", params={"type_inspection": "locaux"}).json()
        inspection = _verifier(
            technicien_s.post(
                "/api/v1/inspections",
                json={
                    "modele": "locaux", "site_id": siege.id,
                    "points": [
                        {"point_checklist_id": points[0]["id"], "cotation": "C"},
                        {"point_checklist_id": points[1]["id"], "cotation": "NC", "observation": "Extincteur hors date de contrôle."},
                    ],
                },
            ),
            "inspection locaux (siège)",
        )

        # --- Formations (section 5.3.3) ---
        competence = _verifier(
            referent_s.post("/api/v1/formations/competences", json={"libelle": "Travail en hauteur", "periodicite_mois": 24}),
            "création compétence (Travail en hauteur)",
        )
        seance = _verifier(
            referent_s.post(
                "/api/v1/formations/seances",
                json={
                    "theme": "Recyclage travail en hauteur", "date": str(date.today()),
                    "lieu": "Siège Bamako", "animateur_id": utilisateurs["o.diarra"]["id"],
                    "competence_id": competence["id"],
                },
            ),
            "création séance de formation",
        )
        _verifier(
            referent_s.post(f"/api/v1/formations/seances/{seance['id']}/emargement", json={"participant_id": technicien_id, "present": True}),
            "émargement séance",
        )

        # --- Audit interne (référentiel FOR-SHEQ-017, section 5.3.4) ---
        campagne = _verifier(referent_s.post("/api/v1/audits/campagnes", json={}), "ouverture campagne d'audit")
        exigences = referent_s.get("/api/v1/audits/exigences").json()
        _verifier(
            referent_s.patch(
                f"/api/v1/audits/campagnes/{campagne['id']}/cotations",
                json=[
                    {"exigence_id": exigences[0]["id"], "cotation": 2, "constat": "Politique SHEQ affichée et diffusée."},
                    {"exigence_id": exigences[1]["id"], "cotation": 0, "ecart": "Registre des risques non mis à jour depuis 8 mois."},
                ],
            ),
            "cotation de la campagne d'audit",
        )

        # --- Revue de direction (FOR-SHEQ-016, section 5.3.4) ---
        revue = _verifier(
            responsable_s.post(
                "/api/v1/revues",
                json={
                    "date": str(date.today()), "lieu": "Siège Bamako",
                    "periode_debut": str(date.today() - timedelta(days=90)), "periode_fin": str(date.today()),
                    "participants": "A. Traoré (administrateur), F. Traoré (responsable), O. Diarra (référent SHEQ)",
                },
            ),
            "revue de direction",
        )
        _verifier(
            responsable_s.post(
                f"/api/v1/revues/{revue['id']}/decisions",
                json={
                    "libelle": "Mettre à jour le registre des risques", "responsable_id": utilisateurs["o.diarra"]["id"],
                    "echeance": str(date.today() + timedelta(days=30)),
                },
            ),
            "décision de revue de direction",
        )

        # --- Documents (section 5.3.5) ---
        document = _verifier(
            referent_s.post(
                "/api/v1/documents",
                data={"reference": "POL-SHEQ-001", "intitule": "Politique SHEQ", "niveau": "1"},
            ),
            "dépôt document (Politique SHEQ, brouillon)",
        )
        _verifier(referent_s.post(f"/api/v1/documents/{document['id']}/soumettre-approbation"), "soumission à approbation")
        _verifier(responsable_s.post(f"/api/v1/documents/{document['id']}/approuver"), "approbation du document")

        # --- Visiteurs (section 5.3.6, REG-SHEQ-004) ---
        visiteur = _verifier(
            technicien_s.post(
                "/api/v1/visiteurs",
                json={
                    "nom": "Ibrahim Cissé", "societe": "Orange Mali", "motif": "Réunion technique",
                    "personne_visitee": "Oumou Diarra", "consignes_lues": True,
                },
            ),
            "enregistrement visiteur",
        )
        _verifier(technicien_s.post(f"/api/v1/visiteurs/{visiteur['id']}/depart"), "départ visiteur")

        # --- Déchets (REG-SHEQ-005) ---
        _verifier(
            referent_s.post(
                "/api/v1/dechets",
                json={
                    "date": str(date.today()), "type": "Batteries usagées", "description": "12 batteries plomb-acide, onduleur siège",
                    "quantite": "12 unités", "site_id": siege.id, "filiere": "Recyclage agréé — Mali Recyclage SA",
                },
            ),
            "enregistrement déchet",
        )

        print("\nJeu de données de démonstration créé avec succès.")
        print(f"Mot de passe commun à tous les comptes : {MOT_DE_PASSE_DEMO}")
        print("Identifiants : a.traore (administrateur), o.diarra (référent SHEQ), "
              "f.traore (responsable), a.kone / s.diallo (techniciens), m.sangare (collaborateur)")


if __name__ == "__main__":
    peupler()
