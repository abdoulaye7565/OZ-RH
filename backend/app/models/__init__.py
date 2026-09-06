"""Importer ce module enregistre les 14 entités (+ hors dictionnaire, voir
point_checklist.py, cotation_risque.py et les modèles Formations/Audits/Revues
ajoutés au prompt 4.2) auprès de Base.metadata — nécessaire pour qu'Alembic
les détecte à l'autogénération et que les relations inter-modèles (chaînes de
classes) se résolvent."""
from app.models.action import Action
from app.models.campagne_audit import CampagneAudit
from app.models.competence import Competence
from app.models.configuration import Configuration
from app.models.cotation_audit import CotationAudit
from app.models.cotation_risque import CotationRisque
from app.models.decision_revue import DecisionRevue
from app.models.dechet import Dechet
from app.models.document import Document
from app.models.emargement import Emargement
from app.models.enquete_satisfaction import EnqueteSatisfaction
from app.models.epi import Epi
from app.models.equipement import Equipement
from app.models.evaluation_slam import EvaluationSlam
from app.models.exigence_audit import ExigenceAudit
from app.models.habilitation import Habilitation
from app.models.inspection import Inspection
from app.models.journal_acces import JournalAcces
from app.models.permis import Permis, permis_intervenants
from app.models.point_checklist import PointChecklist
from app.models.question_quiz import QuestionQuiz
from app.models.reponse_satisfaction import ReponseSatisfaction
from app.models.revue_direction import RevueDirection
from app.models.risque import Risque
from app.models.seance import Seance
from app.models.secret import Secret
from app.models.signalement import Signalement
from app.models.site import Site
from app.models.tentative_quiz import TentativeQuiz
from app.models.utilisateur import Utilisateur
from app.models.visiteur import Visiteur

__all__ = [
    "Action",
    "CampagneAudit",
    "Competence",
    "Configuration",
    "CotationAudit",
    "CotationRisque",
    "DecisionRevue",
    "Dechet",
    "Document",
    "Emargement",
    "EnqueteSatisfaction",
    "Epi",
    "Equipement",
    "EvaluationSlam",
    "ExigenceAudit",
    "Habilitation",
    "Inspection",
    "JournalAcces",
    "Permis",
    "permis_intervenants",
    "PointChecklist",
    "QuestionQuiz",
    "ReponseSatisfaction",
    "RevueDirection",
    "Risque",
    "Seance",
    "Secret",
    "Signalement",
    "Site",
    "TentativeQuiz",
    "Utilisateur",
    "Visiteur",
]
