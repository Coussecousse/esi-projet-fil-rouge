# shared/application/services/auth_service.py
from typing import Optional
from datetime import datetime, timedelta
import logging
import bcrypt
from jose import jwt, JWTError

from shared.infrastructure.config.settings import get_settings
from shared.domain.entities.user import User
from shared.ports.secondary.user_repository_protocol import UserRepositoryProtocol
from shared.application.dtos.common_dtos import TokenResponseDTO

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Service d'authentification utilisant le pattern Repository.
    
    Ce service encapsule la logique d'authentification et utilise
    le repository des utilisateurs pour l'accès aux données.
    """
    
    def __init__(self, user_repository: UserRepositoryProtocol):
        """
        Initialise le service d'authentification.
        
        Args:
            user_repository: Repository des utilisateurs injecté
        """
        self.user_repository = user_repository
        self.settings = get_settings()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur avec email et mot de passe.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Optional[User]: L'utilisateur authentifié ou None si échec
        """
        try:
            logger.info(f"Tentative d'authentification pour: {email}")
            
            # Récupérer l'utilisateur par email via le repository
            user = await self.user_repository.get_by_email(email)
            if not user:
                logger.warning(f"Utilisateur non trouvé: {email}")
                return None
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                logger.warning(f"Utilisateur inactif: {email}")
                return None
            
            # Récupérer le mot de passe hashé (méthode spécifique au repository)
            if hasattr(self.user_repository, 'get_hashed_password_by_email'):
                hashed_password = await self.user_repository.get_hashed_password_by_email(email)
            else:
                # Fallback pour les repositories qui n'ont pas cette méthode
                logger.warning("Repository doesn't support get_hashed_password_by_email, using fallback")
                return None
            
            if not hashed_password:
                logger.warning(f"Pas de mot de passe hashé trouvé pour: {email}")
                return None
            
            # Vérifier le mot de passe
            is_password_valid = self._verify_password(password, hashed_password)
            
            # Pour le développement : accepter aussi le mot de passe par défaut
            if not is_password_valid and self.settings.is_development():
                if password == "Admin123!":
                    logger.info("Utilisation du mot de passe par défaut pour le développement")
                    is_password_valid = True
            
            if not is_password_valid:
                logger.warning(f"Mot de passe incorrect pour: {email}")
                return None
            
            logger.info(f"Authentification réussie pour: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {str(e)}")
            return None
    
    def create_access_token(self, user: User, expires_delta: timedelta = None) -> str:
        """
        Crée un token JWT pour un utilisateur authentifié.
        
        Args:
            user: Utilisateur pour lequel créer le token
            expires_delta: Durée de validité du token (optionnel)
            
        Returns:
            str: Token JWT signé
        """
        try:
            # Données à encoder dans le token
            token_data = {
                "sub": user.email,
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            
            # Définir l'expiration
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=self.settings.security.access_token_expire_minutes
                )
            
            token_data.update({"exp": expire})
            
            # Encoder le token
            encoded_jwt = jwt.encode(
                token_data, 
                self.settings.security.jwt_secret_key, 
                algorithm=self.settings.security.jwt_algorithm
            )
            
            logger.info(f"Token créé pour l'utilisateur: {user.email}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du token: {str(e)}")
            raise
    
    async def login(self, email: str, password: str) -> Optional[TokenResponseDTO]:
        """
        Processus complet de connexion : authentification + création du token.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Optional[TokenResponseDTO]: Réponse avec token et informations utilisateur
        """
        try:
            # Authentifier l'utilisateur
            user = await self.authenticate_user(email, password)
            if not user:
                return None
            
            # Créer le token d'accès
            access_token_expires = timedelta(
                minutes=self.settings.security.access_token_expire_minutes
            )
            access_token = self.create_access_token(user, access_token_expires)
            
            # Construire la réponse
            return TokenResponseDTO(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.settings.security.access_token_expire_minutes * 60,
                user={
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du processus de connexion: {str(e)}")
            return None
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie un mot de passe contre son hash.
        
        Args:
            plain_password: Mot de passe en clair
            hashed_password: Hash du mot de passe
            
        Returns:
            bool: True si le mot de passe est valide
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """
        Hash un mot de passe avec la configuration sécurisée.
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            str: Hash du mot de passe
        """
        salt = bcrypt.gensalt(rounds=self.settings.security.bcrypt_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Vérifie et décode un token JWT.
        
        Args:
            token: Token JWT à vérifier
            
        Returns:
            Optional[dict]: Payload du token si valide, None sinon
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.security.jwt_secret_key,
                algorithms=[self.settings.security.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token invalide: {str(e)}")
            return None