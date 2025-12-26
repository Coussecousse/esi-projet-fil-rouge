from typing import Optional
from uuid import UUID

from patient_management.domain.entities.patient import Patient
from patient_management.domain.services.patient_service import PatientService
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol
from patient_management.domain.exceptions.patient_exceptions import PatientNotFoundException
from patient_management.application.dtos.patient_dtos import PatientResponseDTO

class GetPatientUseCase:
    """
    Cas d'utilisation pour récupérer un patient.
    Orchestrer la logique de récupération d'un patient.
    """
    
    def __init__(
        self,
        patient_repository: PatientRepositoryProtocol,
        patient_service: PatientService
    ):
        """
        Initialise le cas d'utilisation avec les dépendances nécessaires.
        
        Args:
            patient_repository: Le repository des patients
            patient_service: Le service du domaine pour les patients
        """
        self.patient_repository = patient_repository
        self.patient_service = patient_service
    
    async def execute(self, patient_id: UUID, user_id: UUID) -> PatientResponseDTO:
        """
        Exécute le cas d'utilisation.
        
        Args:
            patient_id: L'ID du patient à récupérer
            user_id: L'ID de l'utilisateur qui demande l'accès
            
        Returns:
            PatientResponseDTO: Le patient récupéré
            
        Raises:
            PatientNotFoundException: Si le patient n'est pas trouvé
            MissingPatientConsentException: Si le patient n'a pas donné son consentement
        """
        # Récupérer le patient
        patient = await self.patient_repository.get_by_id(patient_id)
        
        if not patient:
            raise PatientNotFoundException(patient_id)
        
        # Vérifier si l'utilisateur a la permission d'accéder aux données du patient
        self.patient_service.check_access_permission(patient, user_id)
        
        # Convertir l'entité en DTO de réponse
        return PatientResponseDTO(
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender,
            address=patient.address,
            city=patient.city,
            postal_code=patient.postal_code,
            country=patient.country,
            phone_number=patient.phone_number,
            email=patient.email,
            blood_type=patient.blood_type,
            allergies=patient.allergies,
            chronic_diseases=patient.chronic_diseases,
            current_medications=patient.current_medications,
            has_consent=patient.has_consent,
            gdpr_consent=patient.gdpr_consent,
            consent_date=patient.consent_date,
            insurance_provider=patient.insurance_provider,
            insurance_id=patient.insurance_id,
            notes=patient.notes,
            created_at=patient.created_at,
            updated_at=patient.updated_at,
            is_active=patient.is_active
        )