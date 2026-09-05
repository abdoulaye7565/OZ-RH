"""Importer ce module enregistre les 14 entités auprès de Base.metadata — nécessaire
pour qu'Alembic les détecte à l'autogénération et que les relations inter-modèles
(chaînes de classes) se résolvent."""
from app.models.action import Action
from app.models.configuration import Configuration
from app.models.document import Document
from app.models.epi import Epi
from app.models.equipement import Equipement
from app.models.evaluation_slam import EvaluationSlam
from app.models.inspection import Inspection
from app.models.journal_acces import JournalAcces
from app.models.permis import Permis, permis_intervenants
from app.models.risque import Risque
from app.models.secret import Secret
from app.models.signalement import Signalement
from app.models.site import Site
from app.models.utilisateur import Utilisateur

__all__ = [
    "Action",
    "Configuration",
    "Document",
    "Epi",
    "Equipement",
    "EvaluationSlam",
    "Inspection",
    "JournalAcces",
    "Permis",
    "permis_intervenants",
    "Risque",
    "Secret",
    "Signalement",
    "Site",
    "Utilisateur",
]
