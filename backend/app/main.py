"""Point d'entrée de l'API SHEQ Management."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.actions import router as actions_router
from app.api.v1.audits import router as audits_router
from app.api.v1.auth import router as auth_router
from app.api.v1.configurations import router as configurations_router
from app.api.v1.dechets import router as dechets_router
from app.api.v1.documents import router as documents_router
from app.api.v1.epi import router as epi_router
from app.api.v1.equipements import router as equipements_router
from app.api.v1.evaluations_slam import router as slam_router
from app.api.v1.formations import router as formations_router
from app.api.v1.inspections import router as inspections_router
from app.api.v1.permis import router as permis_router
from app.api.v1.points_checklist import router as points_checklist_router
from app.api.v1.revues import router as revues_router
from app.api.v1.risques import router as risques_router
from app.api.v1.satisfaction import router as satisfaction_router
from app.api.v1.signalements import router as signalements_router
from app.api.v1.tableau_bord import router as tableau_bord_router
from app.api.v1.visiteurs import router as visiteurs_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(signalements_router, prefix="/api/v1")
app.include_router(actions_router, prefix="/api/v1")
app.include_router(tableau_bord_router, prefix="/api/v1")
app.include_router(epi_router, prefix="/api/v1")
app.include_router(slam_router, prefix="/api/v1")
app.include_router(permis_router, prefix="/api/v1")
app.include_router(points_checklist_router, prefix="/api/v1")
app.include_router(inspections_router, prefix="/api/v1")
app.include_router(equipements_router, prefix="/api/v1")
app.include_router(configurations_router, prefix="/api/v1")
app.include_router(risques_router, prefix="/api/v1")
app.include_router(formations_router, prefix="/api/v1")
app.include_router(audits_router, prefix="/api/v1")
app.include_router(revues_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(visiteurs_router, prefix="/api/v1")
app.include_router(dechets_router, prefix="/api/v1")
app.include_router(satisfaction_router, prefix="/api/v1")


@app.get("/health", tags=["système"])
def health() -> dict[str, str]:
    """Vérifie que l'API répond. Ne dépend d'aucune ressource externe (base, disque)."""
    return {"status": "ok", "environment": settings.environment}
