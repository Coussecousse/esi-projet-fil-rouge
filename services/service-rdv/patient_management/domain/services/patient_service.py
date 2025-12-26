from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List 
from uuid import UUID

from patient_management.domain.entities.patient import Patient
from patient_management.domain.exceptions.patient_exceptions import (
    MissingPatientConsentException,
    MissingGuardianConsentException,
    MissingRequiredFieldException
)

class PatientService:
    """
    Service du domaine pour les opérations liées aux patients.
    Contient la logique métier pour la gestion des patients.
    """
    
    def validate_patient_data(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        gender: str
    ) -> None:
        """
        Valide les données d'un patient.
        
        Args:
            first_name: Le prénom du patient
            last_name: Le nom du patient
            date_of_birth: La date de naissance du patient
            gender: Le genre du patient
            
        Raises:
            MissingRequiredFieldException: Si un champ requis est manquant
        """
        if not first_name:
            raise MissingRequiredFieldException("first_name")
        
        if not last_name:
            raise MissingRequiredFieldException("last_name")
        
        if not date_of_birth:
            raise MissingRequiredFieldException("date_of_birth")
        
        if not gender:
            raise MissingRequiredFieldException("gender")
        
        # Vérifier que la date de naissance n'est pas dans le futur
        if date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future")
    
    def check_consent_for_minor(self, patient: Patient, has_guardian_consent: bool) -> None:
        """
        Vérifie si le consentement du tuteur légal est nécessaire pour un mineur.
        
        Args:
            patient: Le patient à vérifier
            has_guardian_consent: Indique si le tuteur légal a donné son consentement
            
        Raises:
            MissingGuardianConsentException: Si le patient est mineur et que le consentement
                du tuteur légal est manquant
        """
        # Vérifier si le patient est mineur (moins de 18 ans)
        if patient.age < 18 and not has_guardian_consent:
            raise MissingGuardianConsentException(patient.id)
    
    def check_access_permission(self, patient: Patient, user_id: UUID) -> None:
        """
        Vérifie si un utilisateur a la permission d'accéder aux données d'un patient.
        
        Args:
            patient: Le patient dont on veut accéder aux données
            user_id: L'ID de l'utilisateur qui demande l'accès
            
        Raises:
            MissingPatientConsentException: Si le patient n'a pas donné son consentement
                pour l'accès à ses données
        """
        # Vérifier si le patient a donné son consentement
        if not patient.has_consent:
            raise MissingPatientConsentException(patient.id)
        
        # Note: Ici, on pourrait ajouter d'autres vérifications, comme
        # vérifier si l'utilisateur est le médecin traitant du patient,
        # ou s'il fait partie du personnel médical autorisé.