from typing import Optional, List, Dict
from uuid import UUID
from shared.domain.entities.user import User
from shared.ports.secondary.user_repository_protocol import UserRepositoryProtocol

class InMemoryUserRepository(UserRepositoryProtocol):
    """
    Adaptateur secondaire pour le repository des utilisateurs en mémoire (pour les tests).
    Implémente le port UserRepositoryProtocol.
    """
    
    def __init__(self):
        """
        Initialise le repository avec une liste vide d'utilisateurs.
        """
        self.users: Dict[UUID, User] = {}
        self.email_index: Dict[str, UUID] = {}
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: L'ID de l'utilisateur à récupérer
            
        Returns:
            Optional[User]: L'utilisateur trouvé ou None si non trouvé
        """
        return self.users.get(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.
        
        Args:
            email: L'email de l'utilisateur à récupérer
            
        Returns:
            Optional[User]: L'utilisateur trouvé ou None si non trouvé
        """
        user_id = self.email_index.get(email)
        if not user_id:
            return None
        
        return self.users.get(user_id)
    
    async def create(self, user: User) -> User:
        """
        Crée un nouvel utilisateur.
        
        Args:
            user: L'utilisateur à créer
            
        Returns:
            User: L'utilisateur créé avec son ID généré
        """
        self.users[user.id] = user
        self.email_index[user.email] = user.id
        return user
    
    async def update(self, user: User) -> User:
        """
        Met à jour un utilisateur existant.
        
        Args:
            user: L'utilisateur à mettre à jour
            
        Returns:
            User: L'utilisateur mis à jour
        """
        # Si l'email a changé, mettre à jour l'index d'emails
        if user.id in self.users and self.users[user.id].email != user.email:
            old_email = self.users[user.id].email
            del self.email_index[old_email]
            self.email_index[user.email] = user.id
        
        self.users[user.id] = user
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """
        Supprime un utilisateur.
        
        Args:
            user_id: L'ID de l'utilisateur à supprimer
            
        Returns:
            bool: True si l'utilisateur a été supprimé, False sinon
        """
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        del self.email_index[user.email]
        del self.users[user_id]
        return True
    
    async def list_all(self) -> List[User]:
        """
        Liste tous les utilisateurs.
        
        Returns:
            List[User]: La liste de tous les utilisateurs
        """
        return list(self.users.values())
    
    async def list_by_role(self, role: str) -> List[User]:
        """
        Liste les utilisateurs par rôle.
        
        Args:
            role: Le rôle des utilisateurs à lister
            
        Returns:
            List[User]: La liste des utilisateurs ayant le rôle spécifié
        """
        return [user for user in self.users.values() if user.role.value == role]