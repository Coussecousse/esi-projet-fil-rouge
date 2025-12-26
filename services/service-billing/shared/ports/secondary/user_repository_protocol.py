from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from shared.domain.entities.user import User

class UserRepositoryProtocol(ABC):
    """
    Port secondaire pour le repository des utilisateurs.
    Cette interface définit comment les opérations sur les utilisateurs doivent être effectuées.
    """
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: L'ID de l'utilisateur à récupérer
            
        Returns:
            Optional[User]: L'utilisateur trouvé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.
        
        Args:
            email: L'email de l'utilisateur à récupérer
            
        Returns:
            Optional[User]: L'utilisateur trouvé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Crée un nouvel utilisateur.
        
        Args:
            user: L'utilisateur à créer
            
        Returns:
            User: L'utilisateur créé avec son ID généré
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Met à jour un utilisateur existant.
        
        Args:
            user: L'utilisateur à mettre à jour
            
        Returns:
            User: L'utilisateur mis à jour
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Supprime un utilisateur.
        
        Args:
            user_id: L'ID de l'utilisateur à supprimer
            
        Returns:
            bool: True si l'utilisateur a été supprimé, False sinon
        """
        pass
    
    @abstractmethod
    async def list_all(self) -> List[User]:
        """
        Liste tous les utilisateurs.
        
        Returns:
            List[User]: La liste de tous les utilisateurs
        """
        pass
    
    @abstractmethod
    async def list_by_role(self, role: str) -> List[User]:
        """
        Liste les utilisateurs par rôle.
        
        Args:
            role: Le rôle des utilisateurs à lister
            
        Returns:
            List[User]: La liste des utilisateurs ayant le rôle spécifié
        """
        pass