from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import logging
from dotenv import load_dotenv

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

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Initialiser le container
container = Container()

# Informations de version pour l'API
API_VERSION = "1.0.0"
API_PREFIX = "/api"  # Ne pas utiliser os.getenv ici, mais définir explicitement

app = FastAPI(
    title="MediSecure API",
    description="API pour la gestion des dossiers patients et des rendez-vous médicaux",
    version=API_VERSION,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# Configuration CORS - Modification pour accepter les requêtes du frontend
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost",
    "http://frontend",
    "http://frontend-service:3001",
    "http://frontend-service:3000",
    "*" # Pour le developpement, à retirer en production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
async def health_check():
    """Endpoint de vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Événement de démarrage de l'application
@app.on_event("startup")
async def startup_event():
    logger.info("=== MediSecure API démarrée ===")
    logger.info(f"Version: {API_VERSION}")
    logger.info(f"Environnement: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Préfixe API: {API_PREFIX}")
    logger.info(f"CORS Origins: {origins}")
    
    # Afficher toutes les routes pour débogage
    for route in app.routes:
        logger.info(f"Route: {route.path}, methods: {route.methods}")

# Événement d'arrêt de l'application
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== MediSecure API arrêtée ===")

if __name__ == "__main__":
    import uvicorn
    
    # Configurer le serveur Uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    logger.info(f"Démarrage du serveur sur {host}:{port} (reload: {reload})")
    uvicorn.run("api.main:app", host=host, port=port, reload=reload)