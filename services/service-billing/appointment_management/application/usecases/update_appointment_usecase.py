# Chemin: medisecure-backend/appointment_management/application/usecases/update_appointment_usecase.py

from uuid import UUID
from datetime import datetime
from typing import Optional

from appointment_management.domain.entities.appointment import Appointment, AppointmentStatus
from appointment_management.domain.services.appointment_service import AppointmentService
from appointment_management.domain.ports.secondary.appointment_repository_protocol import AppointmentRepositoryProtocol
from appointment_management.application.dtos.appointment_dtos import AppointmentUpdateDTO, AppointmentResponseDTO

class UpdateAppointmentUseCase:
    """
    Cas d'utilisation pour la mise à jour d'un rendez-vous.
    Orchestrer la logique de mise à jour d'un rendez-vous existant.
    """
    
    def __init__(
        self,
        appointment_repository: AppointmentRepositoryProtocol,
        appointment_service: AppointmentService
    ):
        """
        Initialise le cas d'utilisation avec les dépendances nécessaires.
        
        Args:
            appointment_repository: Le repository des rendez-vous
            appointment_service: Le service du domaine pour les rendez-vous
        """
        self.appointment_repository = appointment_repository
        self.appointment_service = appointment_service
    
    async def execute(self, appointment_id: UUID, data: AppointmentUpdateDTO) -> AppointmentResponseDTO:
        """
        Exécute le cas d'utilisation.
        
        Args:
            appointment_id: L'ID du rendez-vous à mettre à jour
            data: Les données pour la mise à jour du rendez-vous
            
        Returns:
            AppointmentResponseDTO: Le rendez-vous mis à jour
            
        Raises:
            AppointmentNotFoundException: Si le rendez-vous n'est pas trouvé
            ValueError: Si les heures de début et de fin sont invalides
        """
        # Récupérer le rendez-vous existant
        appointment = await self.appointment_repository.get_by_id(appointment_id)
        
        if not appointment:
            raise ValueError(f"Rendez-vous avec ID {appointment_id} non trouvé")
        
        # Mettre à jour les champs si fournis
        if data.start_time is not None and data.end_time is not None:
            # Valider les nouvelles heures
            self.appointment_service.validate_appointment_times(data.start_time, data.end_time)
            
            # Vérifier si le nouveau créneau est disponible
            existing_appointments = await self.appointment_repository.get_by_doctor(
                appointment.doctor_id, 
                skip=0, 
                limit=1000
            )
            
            if self.appointment_service.check_appointment_overlap(
                existing_appointments, 
                data.start_time, 
                data.end_time,
                appointment_id
            ):
                raise ValueError("Ce créneau horaire est déjà occupé par un autre rendez-vous")
            
            # Mettre à jour les heures
            appointment.start_time = data.start_time
            appointment.end_time = data.end_time
        elif data.start_time is not None or data.end_time is not None:
            # Si seulement l'une des heures est fournie, utiliser l'autre de l'appointment existant
            start_time = data.start_time if data.start_time is not None else appointment.start_time
            end_time = data.end_time if data.end_time is not None else appointment.end_time
            
            # Valider les heures
            self.appointment_service.validate_appointment_times(start_time, end_time)
            
            # Vérifier si le nouveau créneau est disponible
            existing_appointments = await self.appointment_repository.get_by_doctor(
                appointment.doctor_id, 
                skip=0, 
                limit=1000
            )
            
            if self.appointment_service.check_appointment_overlap(
                existing_appointments, 
                start_time, 
                end_time,
                appointment_id
            ):
                raise ValueError("Ce créneau horaire est déjà occupé par un autre rendez-vous")
            
            # Mettre à jour les heures
            appointment.start_time = start_time
            appointment.end_time = end_time
        
        # Mettre à jour le statut si fourni
        if data.status is not None:
            try:
                appointment.status = AppointmentStatus(data.status)
            except ValueError:
                raise ValueError(f"Statut invalide: {data.status}")
        
        # Mettre à jour les autres champs
        if data.reason is not None:
            appointment.reason = data.reason
        
        if data.notes is not None:
            appointment.notes = data.notes
        
        # Mettre à jour la date de mise à jour
        appointment.updated_at = datetime.utcnow()
        
        # Sauvegarder les modifications
        updated_appointment = await self.appointment_repository.update(appointment)
        
        # Convertir l'entité en DTO de réponse
        return AppointmentResponseDTO(
            id=updated_appointment.id,
            patient_id=updated_appointment.patient_id,
            doctor_id=updated_appointment.doctor_id,
            start_time=updated_appointment.start_time,
            end_time=updated_appointment.end_time,
            status=updated_appointment.status.value,
            reason=updated_appointment.reason,
            notes=updated_appointment.notes,
            created_at=updated_appointment.created_at,
            updated_at=updated_appointment.updated_at,
            is_active=updated_appointment.is_active
        )