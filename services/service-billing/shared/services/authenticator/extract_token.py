from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

security = HTTPBearer()

async def extract_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Extrait et valide le payload du token JWT.
    
    Args:
        credentials: Les informations d'authentification HTTP
        
    Returns:
        Dict[str, Any]: Le payload du token JWT
        
    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        # Récupérer le token
        token = credentials.credentials
        
        # Décoder le token
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY", "default_secret_key"), 
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
        )
        
        # Assurez-vous que le rôle est en majuscules pour la vérification ultérieure
        # Mais ne modifiez pas le payload original
        if "role" in payload and isinstance(payload["role"], str):
            payload["role"] = payload["role"].upper()
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )