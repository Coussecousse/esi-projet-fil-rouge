from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import traceback

from shared.ports.primary.authenticator_protocol import AuthenticatorProtocol

# Charger les variables d'environnement
load_dotenv()

class BasicAuthenticator(AuthenticatorProtocol):
    """
    Adaptateur primaire pour l'authentification de base avec JWT.
    Implémente le port AuthenticatorProtocol.
    """
    
    def __init__(self):
        """
        Initialise l'authentificateur avec les clés et algorithmes de chiffrement.
        """
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "default_secret_key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crée un token d'accès JWT.
        
        Args:
            data: Les données à encoder dans le token
            expires_delta: Durée de validité du token (optionnel)
            
        Returns:
            str: Le token d'accès JWT encodé
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            print(f"Erreur lors de la création du token: {str(e)}")
            print(traceback.format_exc())
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie si un mot de passe en clair correspond au hash stocké.
        
        Args:
            plain_password: Le mot de passe en clair
            hashed_password: Le hash du mot de passe stocké
            
        Returns:
            bool: True si le mot de passe correspond, False sinon
        """
        try:
            print(f"Vérification du mot de passe. Mot de passe en clair: {plain_password}, Hash: {hashed_password}")
            result = self.pwd_context.verify(plain_password, hashed_password)
            print(f"Résultat de la vérification: {result}")
            return result
        except Exception as e:
            print(f"Erreur lors de la vérification du mot de passe: {str(e)}")
            print(traceback.format_exc())
            raise
    
    def get_password_hash(self, password: str) -> str:
        """
        Génère un hash à partir d'un mot de passe en clair.
        
        Args:
            password: Le mot de passe en clair
            
        Returns:
            str: Le hash du mot de passe
        """
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            print(f"Erreur lors du hachage du mot de passe: {str(e)}")
            print(traceback.format_exc())
            raise