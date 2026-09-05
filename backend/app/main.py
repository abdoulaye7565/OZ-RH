"""Point d'entrée de l'API SHEQ Management."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health", tags=["système"])
def health() -> dict[str, str]:
    """Vérifie que l'API répond. Ne dépend d'aucune ressource externe (base, disque)."""
    return {"status": "ok", "environment": settings.environment}
