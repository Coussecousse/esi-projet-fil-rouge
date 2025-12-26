from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from uuid import UUID

from shared.domain.enums.roles import UserRole

# DTOs pour les utilisateurs
class UserCreateDTO(BaseModel):
    """DTO pour la création d'un utilisateur"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole
    
    class Config:
        use_enum_values = True

class UserUpdateDTO(BaseModel):
    """DTO pour la mise à jour d'un utilisateur"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    
    class Config:
        use_enum_values = True

class UserResponseDTO(BaseModel):
    """DTO pour la réponse avec un utilisateur"""
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# DTOs pour l'authentification
class TokenRequestDTO(BaseModel):
    """DTO pour la demande de token d'authentification"""
    username: str  # En fait l'email de l'utilisateur
    password: str

class TokenResponseDTO(BaseModel):
    """DTO pour la réponse avec un token d'authentification"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponseDTO

class PasswordResetRequestDTO(BaseModel):
    """DTO pour la demande de réinitialisation de mot de passe"""
    email: EmailStr

class PasswordResetConfirmDTO(BaseModel):
    """DTO pour la confirmation de réinitialisation de mot de passe"""
    token: str
    new_password: str

class EmailConfirmationDTO(BaseModel):
    """DTO pour la confirmation d'email"""
    token: str

# DTOs génériques
class PaginatedResponseDTO(BaseModel):
    """DTO pour une réponse paginée"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponseDTO(BaseModel):
    """DTO pour une réponse d'erreur"""
    detail: str
    status_code: int
    path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)