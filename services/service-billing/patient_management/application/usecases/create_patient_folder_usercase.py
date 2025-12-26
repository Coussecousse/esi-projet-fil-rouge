from datetime import date
from typing import Optional, Dict, Any 
from uuid import UUID
from uuid import uuid4

from patient_management.domain.entities.patient import Patient
from patient_management.domain.services.patient_service import PatientService
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol
from patient_management.domain.exceptions.patient_exceptions import PatientAlreadyExistsException
from patient_management.application.dtos.patient_dtos import PatientCreateDTO, PatientResponseDTO
from shared.ports.primary.id_generator_protocol import IdGeneratorProtocol

class CreatePatientFolderUseCase:
    """
    Cas d'utilisation pour la création d'un dossier patient.
    Orchestrer la logique de création d'un nouveau patient.
    """
    
    def __init__(
        self,
        patient_repository: PatientRepositoryProtocol,
        patient_service: PatientService,
        id_generator: IdGeneratorProtocol
    ):
        """
        Initialise le cas d'utilisation avec les dépendances nécessaires.
        
        Args:
            patient_repository: Le repository des patients
            patient_service: Le service du domaine pour les patients
            id_generator: Le générateur d'identifiants
        """
        self.patient_repository = patient_repository
        self.patient_service = patient_service
        self.id_generator = id_generator
    
    async def execute(self, data: PatientCreateDTO) -> PatientResponseDTO:
        """
        Exécute le cas d'utilisation.
        
        Args:
            data: Les données pour la création du patient
            
        Returns:
            PatientResponseDTO: Le patient créé
            
        Raises:
            PatientAlreadyExistsException: Si un patient avec le même email existe déjà
            MissingRequiredFieldException: Si un champ requis est manquant
            MissingGuardianConsentException: Si le patient est mineur et que le consentement
                du tuteur légal est manquant
        """
        # Valider les données du patient
        self.patient_service.validate_patient_data(
            data.first_name,
            data.last_name,
            data.date_of_birth,
            data.gender
        )
        
        # Vérifier si un patient avec le même email existe déjà
        if data.email:
            existing_patient = await self.patient_repository.get_by_email(data.email)
            if existing_patient:
                raise PatientAlreadyExistsException("email", data.email)
        
        # Créer une nouvelle entité Patient
        patient_id = self.id_generator.generate_id()
        
        patient = Patient(
            id=patient_id,
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            address=data.address,
            city=data.city,
            postal_code=data.postal_code,
            country=data.country,
            phone_number=data.phone_number,
            email=data.email,
            blood_type=data.blood_type,
            allergies=data.allergies or {},
            chronic_diseases=data.chronic_diseases or {},
            current_medications=data.current_medications or {},
            has_consent=data.has_consent,
            gdpr_consent=data.gdpr_consent,
            insurance_provider=data.insurance_provider,
            insurance_id=data.insurance_id,
            notes=data.notes
        )
        
        # Vérifier si le consentement du tuteur légal est nécessaire pour un mineur
        self.patient_service.check_consent_for_minor(patient, data.has_guardian_consent)
        
        # Sauvegarder le patient dans le repository
        created_patient = await self.patient_repository.create(patient)
        
        # Convertir l'entité en DTO de réponse
        return PatientResponseDTO(
            id=created_patient.id,
            first_name=created_patient.first_name,
            last_name=created_patient.last_name,
            date_of_birth=created_patient.date_of_birth,
            gender=created_patient.gender,
            address=created_patient.address,
            city=created_patient.city,
            postal_code=created_patient.postal_code,
            country=created_patient.country,
            phone_number=created_patient.phone_number,
            email=created_patient.email,
            blood_type=created_patient.blood_type,
            allergies=created_patient.allergies,
            chronic_diseases=created_patient.chronic_diseases,
            current_medications=created_patient.current_medications,
            has_consent=created_patient.has_consent,
            gdpr_consent=created_patient.gdpr_consent,
            consent_date=created_patient.consent_date,
            insurance_provider=created_patient.insurance_provider,
            insurance_id=created_patient.insurance_id,
            notes=created_patient.notes,
            created_at=created_patient.created_at,
            updated_at=created_patient.updated_at,
            is_active=created_patient.is_active
        )