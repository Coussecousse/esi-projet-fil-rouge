# medisecure-backend/patient_management/application/dtos/patient_dtos.py
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from uuid import UUID

# DTOs pour la création et la mise à jour de patients
class PatientCreateDTO(BaseModel):
    """DTO pour la création d'un patient"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    
    # Informations médicales
    blood_type: Optional[str] = Field(None, max_length=10)
    allergies: Optional[Dict[str, Any]] = None
    chronic_diseases: Optional[Dict[str, Any]] = None
    current_medications: Optional[Dict[str, Any]] = None
    
    # Informations de consentement
    has_consent: bool = True  # Changé de False à True par défaut
    gdpr_consent: bool = True  # Changé de False à True par défaut
    has_guardian_consent: bool = False  # Pour les mineurs
    
    # Informations administratives
    insurance_provider: Optional[str] = Field(None, max_length=100)
    insurance_id: Optional[str] = Field(None, max_length=100)
    
    # Métadonnées
    notes: Optional[str] = None
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Valide que la date de naissance n'est pas dans le futur"""
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

class PatientUpdateDTO(BaseModel):
    """DTO pour la mise à jour d'un patient"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    
    # Informations médicales
    blood_type: Optional[str] = Field(None, max_length=10)
    allergies: Optional[Dict[str, Any]] = None
    chronic_diseases: Optional[Dict[str, Any]] = None
    current_medications: Optional[Dict[str, Any]] = None
    
    # Informations de consentement
    has_consent: Optional[bool] = None
    gdpr_consent: Optional[bool] = None
    
    # Informations administratives
    insurance_provider: Optional[str] = Field(None, max_length=100)
    insurance_id: Optional[str] = Field(None, max_length=100)
    
    # Métadonnées
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Valide que la date de naissance n'est pas dans le futur"""
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

# DTOs pour les réponses
class PatientResponseDTO(BaseModel):
    """DTO pour la réponse avec un patient"""
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    
    # Informations médicales
    blood_type: Optional[str] = None
    allergies: Optional[Dict[str, Any]] = None
    chronic_diseases: Optional[Dict[str, Any]] = None
    current_medications: Optional[Dict[str, Any]] = None
    
    # Informations de consentement
    has_consent: bool
    gdpr_consent: bool
    consent_date: Optional[datetime] = None
    
    # Informations administratives
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    
    # Métadonnées
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True

class PatientListResponseDTO(BaseModel):
    """DTO pour la réponse avec une liste de patients"""
    patients: List[PatientResponseDTO]
    total: int
    skip: int
    limit: int

# DTOs pour la recherche
class PatientSearchDTO(BaseModel):
    """DTO pour la recherche de patients"""
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skip: int = 0
    limit: int = 100