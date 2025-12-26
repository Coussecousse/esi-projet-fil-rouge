from typing import Optional, Dict, Any 
from uuid import UUID

from patient_management.domain.entities.patient import Patient
from patient_management.domain.services.patient_service import PatientService
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol
from patient_management.domain.exceptions.patient_exceptions import PatientNotFoundException
from patient_management.application.dtos.patient_dtos import PatientUpdateDTO, PatientResponseDTO

class UpdatePatientUseCase:
    """
    Cas d'utilisation pour la mise à jour d'un patient.
    Orchestrer la logique de mise à jour d'un patient existant.
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
    
    async def execute(self, patient_id: UUID, data: PatientUpdateDTO) -> PatientResponseDTO:
        """
        Exécute le cas d'utilisation.
        
        Args:
            patient_id: L'ID du patient à mettre à jour
            data: Les données pour la mise à jour du patient
            
        Returns:
            PatientResponseDTO: Le patient mis à jour
            
        Raises:
            PatientNotFoundException: Si le patient n'est pas trouvé
        """
        # Récupérer le patient existant
        patient = await self.patient_repository.get_by_id(patient_id)
        
        if not patient:
            raise PatientNotFoundException(patient_id)
        
        # Mettre à jour les données du patient si elles sont fournies
        if data.first_name is not None:
            patient.first_name = data.first_name
        
        if data.last_name is not None:
            patient.last_name = data.last_name
        
        if data.date_of_birth is not None:
            # Valider que la date de naissance n'est pas dans le futur
            self.patient_service.validate_patient_data(
                patient.first_name,
                patient.last_name,
                data.date_of_birth,
                patient.gender
            )
            patient.date_of_birth = data.date_of_birth
        
        if data.gender is not None:
            patient.gender = data.gender
        
        # Mettre à jour les informations de contact
        patient.update_contact_info(
            address=data.address,
            city=data.city,
            postal_code=data.postal_code,
            country=data.country,
            phone_number=data.phone_number,
            email=data.email
        )
        
        # Mettre à jour les informations médicales
        patient.update_medical_info(
            blood_type=data.blood_type,
            allergies=data.allergies,
            chronic_diseases=data.chronic_diseases,
            current_medications=data.current_medications
        )
        
        # Mettre à jour les informations de consentement
        if data.has_consent is not None or data.gdpr_consent is not None:
            patient.update_consent(
                consent=data.has_consent if data.has_consent is not None else patient.has_consent,
                gdpr_consent=data.gdpr_consent if data.gdpr_consent is not None else patient.gdpr_consent
            )
        
        # Mettre à jour les informations d'assurance
        patient.update_insurance(
            insurance_provider=data.insurance_provider,
            insurance_id=data.insurance_id
        )
        
        # Mettre à jour les métadonnées
        if data.notes is not None:
            patient.notes = data.notes
        
        if data.is_active is not None:
            patient.is_active = data.is_active
        
        # Sauvegarder les modifications dans le repository
        updated_patient = await self.patient_repository.update(patient)
        
        # Convertir l'entité en DTO de réponse
        return PatientResponseDTO(
            id=updated_patient.id,
            first_name=updated_patient.first_name,
            last_name=updated_patient.last_name,
            date_of_birth=updated_patient.date_of_birth,
            gender=updated_patient.gender,
            address=updated_patient.address,
            city=updated_patient.city,
            postal_code=updated_patient.postal_code,
            country=updated_patient.country,
            phone_number=updated_patient.phone_number,
            email=updated_patient.email,
            blood_type=updated_patient.blood_type,
            allergies=updated_patient.allergies,
            chronic_diseases=updated_patient.chronic_diseases,
            current_medications=updated_patient.current_medications,
            has_consent=updated_patient.has_consent,
            gdpr_consent=updated_patient.gdpr_consent,
            consent_date=updated_patient.consent_date,
            insurance_provider=updated_patient.insurance_provider,
            insurance_id=updated_patient.insurance_id,
            notes=updated_patient.notes,
            created_at=updated_patient.created_at,
            updated_at=updated_patient.updated_at,
            is_active=updated_patient.is_active
        )