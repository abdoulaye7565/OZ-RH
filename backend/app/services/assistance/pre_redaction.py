"""Pré-rédaction des rapports périodiques (prompt 6.4, chapitre 16.2.4 du CDC).

"Tous les chiffres proviennent de la base : l'assistance rédige le
commentaire, jamais la donnée" — chaque fonction construit son prompt à
partir de chiffres déjà calculés ailleurs (jamais recalculés ici, jamais
laissés au modèle à déduire), et l'instruction système le rappelle
explicitement pour limiter le risque d'un chiffre halluciné glissé dans le
commentaire."""
from app.services.assistance import client
from app.services.assistance.client import ResultatAppel

_INSTRUCTION_SYSTEME = (
    "Tu rédiges la synthèse d'un rapport SHEQ pour Hirondelles IT Lab. Commente "
    "UNIQUEMENT les chiffres fournis ci-dessous, en français, sur un ton factuel et "
    "professionnel (3 à 6 phrases). Ne mentionne, n'invente et ne déduis aucun "
    "chiffre qui ne figure pas explicitement dans les données fournies."
)


def generer_commentaire_revue(db, *, indicateurs: dict, decisions_reportees: list[dict], utilisateur_id: int) -> ResultatAppel:
    donnees = (
        f"Accidents/incidents : {indicateurs.get('accidents_incidents')}\n"
        f"Signalements : {indicateurs.get('signalements_total')}\n"
        f"Inspections réalisées : {indicateurs.get('inspections_realisees')}\n"
        f"Taux d'avancement du plan d'action : "
        f"{indicateurs.get('avancement_plan_action', {}).get('taux_avancement_global', 0) * 100:.0f} %\n"
        f"Risques nouveaux : {indicateurs.get('risques_nouveaux')}\n"
        f"Réévaluations de risques : {indicateurs.get('reevaluations_risques')}\n"
        f"Séances de formation réalisées : {indicateurs.get('seances_realisees')}\n"
        f"Décisions reportées de la revue précédente : {len(decisions_reportees)}"
    )
    prompt = f"{_INSTRUCTION_SYSTEME}\n\nDonnées de la période :\n{donnees}"
    return client.appeler(db, fonction="pre_redaction_revue", prompt=prompt, utilisateur_id=utilisateur_id)


def generer_commentaire_audit(db, *, score: dict, utilisateur_id: int) -> ResultatAppel:
    donnees = (
        f"Score total : {score['score_total']} / {score['score_maximal']}\n"
        f"Taux de conformité : {score['taux_conformite_pourcent']:.0f} %\n"
        f"Interprétation calculée : {score['interpretation']}\n"
        "Score par chapitre :\n"
        + "\n".join(
            f"- {c['chapitre']} : {c['score']} / {c['score_maximal']} ({c['taux_pourcent']:.0f} %)"
            for c in score["score_par_chapitre"]
        )
    )
    prompt = f"{_INSTRUCTION_SYSTEME}\n\nDonnées de la campagne :\n{donnees}"
    return client.appeler(db, fonction="pre_redaction_audit", prompt=prompt, utilisateur_id=utilisateur_id)
