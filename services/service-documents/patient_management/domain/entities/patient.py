from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, List, Any
from uuid import UUID

@dataclass
class Patient:
    """
    Entité Patient du domaine.
    Représente un patient dans le système MediSecure.
    """
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
    allergies: Dict[str, Any] = field(default_factory=dict)
    chronic_diseases: Dict[str, Any] = field(default_factory=dict)
    current_medications: Dict[str, Any] = field(default_factory=dict)
    
    # Informations de consentement
    has_consent: bool = False
    consent_date: Optional[datetime] = None
    gdpr_consent: bool = False
    
    # Informations administratives
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    
    # Métadonnées
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet du patient"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calcule l'âge du patient en années"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def update_consent(self, consent: bool, gdpr_consent: bool) -> None:
        """Met à jour les consentements du patient"""
        self.has_consent = consent
        self.gdpr_consent = gdpr_consent
        
        if consent:
            self.consent_date = datetime.utcnow()
        
        self.updated_at = datetime.utcnow()
    
    def update_medical_info(
        self,
        blood_type: Optional[str] = None,
        allergies: Optional[Dict[str, Any]] = None,
        chronic_diseases: Optional[Dict[str, Any]] = None,
        current_medications: Optional[Dict[str, Any]] = None
    ) -> None:
        """Met à jour les informations médicales du patient"""
        if blood_type is not None:
            self.blood_type = blood_type
        
        if allergies is not None:
            self.allergies = allergies
        
        if chronic_diseases is not None:
            self.chronic_diseases = chronic_diseases
        
        if current_medications is not None:
            self.current_medications = current_medications
        
        self.updated_at = datetime.utcnow()
    
    def update_contact_info(
        self,
        address: Optional[str] = None,
        city: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None
    ) -> None:
        """Met à jour les informations de contact du patient"""
        if address is not None:
            self.address = address
        
        if city is not None:
            self.city = city
        
        if postal_code is not None:
            self.postal_code = postal_code
        
        if country is not None:
            self.country = country
        
        if phone_number is not None:
            self.phone_number = phone_number
        
        if email is not None:
            self.email = email
        
        self.updated_at = datetime.utcnow()
    
    def update_insurance(
        self,
        insurance_provider: Optional[str] = None,
        insurance_id: Optional[str] = None
    ) -> None:
        """Met à jour les informations d'assurance du patient"""
        if insurance_provider is not None:
            self.insurance_provider = insurance_provider
        
        if insurance_id is not None:
            self.insurance_id = insurance_id
        
        self.updated_at = datetime.utcnow()