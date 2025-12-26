from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from shared.domain.enums.roles import UserRole

@dataclass
class User:
    """
    Entité utilisateur du domaine.
    Représente un utilisateur dans le système MediSecure.
    """
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est un administrateur"""
        return self.role == UserRole.ADMIN
    
    def is_medical_staff(self) -> bool:
        """Vérifie si l'utilisateur fait partie du personnel médical"""
        return self.role in [UserRole.DOCTOR, UserRole.NURSE]
    
    def can_access_patient_data(self) -> bool:
        """Vérifie si l'utilisateur peut accéder aux données des patients"""
        return self.is_medical_staff() or self.is_admin() or self.role == UserRole.RECEPTIONIST