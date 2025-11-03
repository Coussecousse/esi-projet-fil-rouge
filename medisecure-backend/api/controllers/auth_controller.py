# medisecure-backend/api/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
import logging

from shared.infrastructure.config.settings import get_settings
from shared.container.container import get_container
from shared.application.dtos.common_dtos import TokenResponseDTO
from shared.application.services.auth_service import AuthenticationService

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupérer les settings centralisées
settings = get_settings()

# Créer un router pour les endpoints d'authentification
router = APIRouter(prefix="/auth", tags=["auth"])

# Injection de dépendance pour le service d'authentification
def get_auth_service() -> AuthenticationService:
    """Récupère le service d'authentification depuis le container"""
    container = get_container()
    return container.auth_service()

@router.post("/login", response_model=TokenResponseDTO)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Endpoint de connexion utilisant OAuth2 avec mot de passe.
    Utilise le pattern Repository via le service d'authentification.
    
    Args:
        request: La requête HTTP
        form_data: Les données du formulaire de connexion
        auth_service: Service d'authentification injecté
        
    Returns:
        TokenResponseDTO: Le token d'accès et les informations de l'utilisateur
        
    Raises:
        HTTPException: En cas d'erreur d'authentification
    """
    try:
        logger.info(f"Tentative de connexion pour: {form_data.username}")
        
        # Utiliser le service d'authentification (pattern Repository)
        token_response = await auth_service.login(form_data.username, form_data.password)
        
        if not token_response:
            logger.warning(f"Échec de la connexion pour: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Connexion réussie pour: {form_data.username}")
        return token_response
        
    except HTTPException:
        # Re-lever les HTTPException telles quelles
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la connexion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/logout")
async def logout(request: Request):
    """Endpoint de déconnexion"""
    try:
        logger.info("Demande de déconnexion")
        return {"message": "Déconnexion réussie"}
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la déconnexion"
        )