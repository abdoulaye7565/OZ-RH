"""Service d'assistance IA (chapitre 16 du CDC — lot 6). Socle posé au prompt
6.1, première fonction métier (assistant documentaire) au prompt 6.2.

Point d'entrée unique pour le reste de l'application — aucun autre module
n'importe `client`, `embeddings`, `journal`, `configuration` ou `garde_fous`
directement (chapitre 16.3.1 : "aucun autre composant n'appelle directement
le service externe")."""
from app.services.assistance.assistant_documentaire import ReferenceSegment, ReponseAssistantDocumentaire, repondre
from app.services.assistance.client import ResultatAppel, appeler
from app.services.assistance.configuration import fonction_activee, plafond_depasse
from app.services.assistance.garde_fous import ContenuRefuseError, masquer_noms, verifier_pas_de_secret
from app.services.assistance.indexation import indexer_document, retirer_segments
from app.services.assistance.journal import depense_du_mois, enregistrer_appel
from app.services.assistance.pre_redaction import generer_commentaire_audit, generer_commentaire_revue

__all__ = [
    "ResultatAppel",
    "appeler",
    "fonction_activee",
    "plafond_depasse",
    "ContenuRefuseError",
    "masquer_noms",
    "verifier_pas_de_secret",
    "depense_du_mois",
    "enregistrer_appel",
    "indexer_document",
    "retirer_segments",
    "repondre",
    "ReponseAssistantDocumentaire",
    "ReferenceSegment",
    "generer_commentaire_revue",
    "generer_commentaire_audit",
]
