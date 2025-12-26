# medisecure-backend/appointment_management/application/usecases/schedule_appointment_usecase.py
from uuid import UUID
from datetime import datetime
import logging

from appointment_management.domain.entities.appointment import Appointment, AppointmentStatus
from appointment_management.domain.services.appointment_service import AppointmentService
from appointment_management.domain.ports.secondary.appointment_repository_protocol import AppointmentRepositoryProtocol
from appointment_management.application.dtos.appointment_dtos import AppointmentCreateDTO, AppointmentResponseDTO
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol
from shared.ports.primary.id_generator_protocol import IdGeneratorProtocol
from patient_management.domain.exceptions.patient_exceptions import PatientNotFoundException

# Configuration du logging
logger = logging.getLogger(__name__)

class ScheduleAppointmentUseCase:
    """
    Cas d'utilisation pour la planification d'un rendez-vous.
    Orchestrer la logique de planification d'un nouveau rendez-vous.
    """
    
    def __init__(
        self,
        appointment_repository: AppointmentRepositoryProtocol,
        patient_repository: PatientRepositoryProtocol,
        appointment_service: AppointmentService,
        id_generator: IdGeneratorProtocol
    ):
        """
        Initialise le cas d'utilisation avec les dépendances nécessaires.
        
        Args:
            appointment_repository: Le repository des rendez-vous
            patient_repository: Le repository des patients
            appointment_service: Le service du domaine pour les rendez-vous
            id_generator: Le générateur d'identifiants
        """
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository
        self.appointment_service = appointment_service
        self.id_generator = id_generator
    
    async def execute(self, data: AppointmentCreateDTO) -> AppointmentResponseDTO:
        """
        Exécute le cas d'utilisation.
        
        Args:
            data: Les données pour la création du rendez-vous
            
        Returns:
            AppointmentResponseDTO: Le rendez-vous créé
            
        Raises:
            PatientNotFoundException: Si le patient n'est pas trouvé
            ValueError: Si les heures de début et de fin sont invalides
        """
        try:
            # Ajouter des logs pour les données reçues
            logger.info(f"Données de rendez-vous reçues: patient_id={data.patient_id}, doctor_id={data.doctor_id}")
            logger.info(f"Dates: start_time={data.start_time}, end_time={data.end_time}")
            
            # Validation des données
            if not data.patient_id:
                raise ValueError("ID du patient requis")
            if not data.doctor_id:
                raise ValueError("ID du médecin requis")
            if not data.start_time:
                raise ValueError("Heure de début requise")
            if not data.end_time:
                raise ValueError("Heure de fin requise")
            
            # S'assurer que les ID sont de type UUID
            patient_id = data.patient_id if isinstance(data.patient_id, UUID) else UUID(str(data.patient_id))
            doctor_id = data.doctor_id if isinstance(data.doctor_id, UUID) else UUID(str(data.doctor_id))
            
            # Valider les heures de début et de fin
            logger.debug("Validation des heures de rendez-vous")
            self.appointment_service.validate_appointment_times(data.start_time, data.end_time)
            
            # Vérifier si le patient existe
            logger.debug(f"Vérification de l'existence du patient {patient_id}")
            patient = await self.patient_repository.get_by_id(patient_id)
            if not patient:
                logger.error(f"Patient avec ID {patient_id} non trouvé")
                raise PatientNotFoundException(patient_id)
          
            # Vérifier si le créneau est disponible (aucun chevauchement)
            logger.debug(f"Vérification de la disponibilité du créneau pour le médecin {doctor_id}")
            existing_appointments = await self.appointment_repository.get_by_doctor(
                doctor_id, 
                skip=0, 
                limit=1000
            )
            
            if self.appointment_service.check_appointment_overlap(
                existing_appointments, 
                data.start_time, 
                data.end_time
            ):
                logger.warning("Chevauchement de rendez-vous détecté")
                raise ValueError("Ce créneau horaire est déjà occupé par un autre rendez-vous")
            
            # Générer un ID pour le rendez-vous
            logger.debug("Génération de l'ID du rendez-vous")
            appointment_id = self.id_generator.generate_id()
            
            # Créer l'entité Appointment
            logger.debug(f"Création de l'entité Appointment avec ID {appointment_id}")
            appointment = Appointment(
                id=appointment_id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                start_time=data.start_time,
                end_time=data.end_time,
                status=AppointmentStatus.SCHEDULED,
                reason=data.reason or "Consultation",
                notes=data.notes
            )
            
            # Sauvegarder le rendez-vous
            logger.info(f"Sauvegarde du rendez-vous {appointment_id}")
            try:
                created_appointment = await self.appointment_repository.create(appointment)
                logger.info(f"Rendez-vous {appointment_id} créé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du rendez-vous: {str(e)}")
                if "violates foreign key constraint" in str(e).lower():
                    raise ValueError("Les identifiants de médecin ou de patient sont invalides. Veuillez vérifier que le médecin et le patient existent.")
                raise
            
            # Convertir l'entité en DTO de réponse
            logger.debug(f"Conversion du rendez-vous {appointment_id} en DTO de réponse")
            response = AppointmentResponseDTO(
                id=created_appointment.id,
                patient_id=created_appointment.patient_id,
                doctor_id=created_appointment.doctor_id,
                start_time=created_appointment.start_time,
                end_time=created_appointment.end_time,
                status=created_appointment.status.value,
                reason=created_appointment.reason,
                notes=created_appointment.notes,
                created_at=created_appointment.created_at,
                updated_at=created_appointment.updated_at,
                is_active=created_appointment.is_active
            )
            
            logger.info(f"Rendez-vous {response.id} créé avec succès")
            return response
            
        except Exception as e:
            logger.exception(f"Erreur lors de la création du rendez-vous: {str(e)}")
            raise