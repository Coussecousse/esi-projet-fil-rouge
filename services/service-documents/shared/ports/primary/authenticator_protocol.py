from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class AuthenticatorProtocol(ABC):
    """
    Port primaire pour l'authentification.
    Cette interface définit comment l'authentification doit être gérée.
    """
    
    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crée un token d'accès JWT.
        
        Args:
            data: Les données à encoder dans le token
            expires_delta: Durée de validité du token (optionnel)
            
        Returns:
            str: Le token d'accès JWT encodé
        """
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie si un mot de passe en clair correspond au hash stocké.
        
        Args:
            plain_password: Le mot de passe en clair
            hashed_password: Le hash du mot de passe stocké
            
        Returns:
            bool: True si le mot de passe correspond, False sinon
        """
        pass
    
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        """
        Génère un hash à partir d'un mot de passe en clair.
        
        Args:
            password: Le mot de passe en clair
            
        Returns:
            str: Le hash du mot de passe
        """
        pass