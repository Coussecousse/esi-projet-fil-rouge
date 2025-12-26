from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from shared.infrastructure.config.settings import get_settings, Settings
from shared.infrastructure.database.connection import get_db
from api.handlers.exception_handlers import (
    AppException, 
    app_exception_handler, 
    http_exception_handler, 
    validation_exception_handler
)
from api.middlewares.authentication_middleware import AuthenticationMiddleware

# Importer les routers
from patient_management.infrastructure.adapters.primary.controllers.patient_controller import router as patient_router
from api.controllers.auth_controller import router as auth_router
from appointment_management.infrastructure.adapters.primary.controllers.appointment_controller import router as appointment_router

# Importer et configurer le container
from shared.container.container import Container

# Récupérer les settings centralisées
settings = get_settings()

# Configuration du logging basée sur les settings
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format
)
logger = logging.getLogger(__name__)

# Initialiser le container
container = Container()

# Prefix API depuis les settings
API_PREFIX = "/api"

# Lifecycle de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("=== Démarrage de MediSecure API ===")
    logger.info(f"Version: {settings.version}")
    logger.info(f"Environnement: {settings.server.environment}")
    logger.info(f"Mode debug: {settings.server.debug}")
    logger.info(f"Préfixe API: {API_PREFIX}")
    yield
    # Shutdown
    logger.info("=== Arrêt de MediSecure API ===")

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins + (["*"] if settings.is_development() else []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware d'authentification
app.middleware("http")(AuthenticationMiddleware())

# Enregistrement des gestionnaires d'exceptions
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Inclure les routes avec le préfixe API
app.include_router(patient_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(appointment_router, prefix=API_PREFIX)

@app.get(f"{API_PREFIX}/health")
async def health_check(
    detailed: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de vérification de l'état de l'API - Version avancée
    
    Args:
        detailed: Si True, retourne des vérifications détaillées
        db: Session de base de données pour les vérifications
    
    Returns:
        Dict: État de santé de l'application et de ses dépendances
    """
    from shared.infrastructure.monitoring.health_checker import HealthChecker
    
    if detailed:
        # Health check complet avec vérifications détaillées
        health_checker = HealthChecker()
        return await health_checker.run_all_checks(session=db)
    else:
        # Health check basique pour les sondes Kubernetes
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "environment": settings.server.environment,
            "app_name": settings.app_name
        }

@app.get(f"{API_PREFIX}/health/live")
async def liveness_probe():
    """
    Sonde de vivacité (liveness probe) pour Kubernetes.
    Vérifie si l'application répond toujours.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get(f"{API_PREFIX}/health/ready") 
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Sonde de disponibilité (readiness probe) pour Kubernetes.
    Vérifie si l'application est prête à recevoir du trafic.
    """
    try:
        # Test rapide de la base de données
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "disconnected",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    # Configuration du serveur depuis les settings
    logger.info(f"Démarrage du serveur sur {settings.server.host}:{settings.server.port}")
    logger.info(f"Mode reload: {settings.is_development()}")
    
    uvicorn.run(
        "api.main:app", 
        host=settings.server.host, 
        port=settings.server.port, 
        reload=settings.is_development()
    )