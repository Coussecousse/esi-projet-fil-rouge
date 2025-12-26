from uuid import UUID
from typing import List

from appointment_management.domain.ports.secondary.appointment_repository_protocol import AppointmentRepositoryProtocol
from appointment_management.application.dtos.appointment_dtos import AppointmentResponseDTO, AppointmentListResponseDTO
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol
from patient_management.domain.exceptions.patient_exceptions import PatientNotFoundException

class GetPatientAppointmentsUseCase:
    """
    Cas d'utilisation pour récupérer les rendez-vous d'un patient.
    """
    
    def __init__(
        self,
        appointment_repository: AppointmentRepositoryProtocol,
        patient_repository: PatientRepositoryProtocol
    ):
        """
        Initialise le cas d'utilisation avec les dépendances nécessaires.
        
        Args:
            appointment_repository: Le repository des rendez-vous
            patient_repository: Le repository des patients
        """
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository
    
    async def execute(self, patient_id: UUID, skip: int = 0, limit: int = 100) -> AppointmentListResponseDTO:
        """
        Exécute le cas d'utilisation.
        
        Args:
            patient_id: L'ID du patient
            skip: Le nombre de rendez-vous à sauter
            limit: Le nombre maximum de rendez-vous à retourner
            
        Returns:
            AppointmentListResponseDTO: La liste des rendez-vous du patient
            
        Raises:
            PatientNotFoundException: Si le patient n'est pas trouvé
        """
        # Vérifier si le patient existe
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundException(patient_id)
        
        # Récupérer les rendez-vous du patient
        appointments = await self.appointment_repository.get_by_patient(patient_id, skip, limit)
        
        # Compter le nombre total de rendez-vous (approximatif sans pagination)
        total = len(appointments)
        
        # Convertir les entités en DTOs de réponse
        appointment_dtos = []
        for appointment in appointments:
            appointment_dtos.append(
                AppointmentResponseDTO(
                    id=appointment.id,
                    patient_id=appointment.patient_id,
                    doctor_id=appointment.doctor_id,
                    start_time=appointment.start_time,
                    end_time=appointment.end_time,
                    status=appointment.status.value,
                    reason=appointment.reason,
                    notes=appointment.notes,
                    created_at=appointment.created_at,
                    updated_at=appointment.updated_at,
                    is_active=appointment.is_active
                )
            )
        
        # Construire la réponse
        return AppointmentListResponseDTO(
            appointments=appointment_dtos,
            total=total,
            skip=skip,
            limit=limit
        )