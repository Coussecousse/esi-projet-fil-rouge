from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime, date
from copy import deepcopy

from appointment_management.domain.entities.appointment import Appointment
from appointment_management.domain.ports.secondary.appointment_repository_protocol import AppointmentRepositoryProtocol

class InMemoryAppointmentRepository(AppointmentRepositoryProtocol):
    """
    Adaptateur secondaire pour le repository des rendez-vous en mémoire (pour les tests).
    Implémente le port AppointmentRepositoryProtocol.
    """
    
    def __init__(self):
        """
        Initialise le repository avec une liste vide de rendez-vous.
        """
        self.appointments: Dict[UUID, Appointment] = {}
    
    async def get_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        """
        Récupère un rendez-vous par son ID.
        
        Args:
            appointment_id: L'ID du rendez-vous à récupérer
            
        Returns:
            Optional[Appointment]: Le rendez-vous trouvé ou None si non trouvé
        """
        appointment = self.appointments.get(appointment_id)
        if appointment:
            return deepcopy(appointment)
        return None
    
    async def create(self, appointment: Appointment) -> Appointment:
        """
        Crée un nouveau rendez-vous.
        
        Args:
            appointment: Le rendez-vous à créer
            
        Returns:
            Appointment: Le rendez-vous créé avec son ID généré
        """
        self.appointments[appointment.id] = deepcopy(appointment)
        return deepcopy(appointment)
    
    async def update(self, appointment: Appointment) -> Appointment:
        """
        Met à jour un rendez-vous existant.
        
        Args:
            appointment: Le rendez-vous à mettre à jour
            
        Returns:
            Appointment: Le rendez-vous mis à jour
        """
        self.appointments[appointment.id] = deepcopy(appointment)
        return deepcopy(appointment)
    
    async def delete(self, appointment_id: UUID) -> bool:
        """
        Supprime un rendez-vous.
        
        Args:
            appointment_id: L'ID du rendez-vous à supprimer
            
        Returns:
            bool: True si le rendez-vous a été supprimé, False sinon
        """
        if appointment_id not in self.appointments:
            return False
        
        del self.appointments[appointment_id]
        return True
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """
        Liste tous les rendez-vous avec pagination.
        
        Args:
            skip: Le nombre de rendez-vous à sauter
            limit: Le nombre maximum de rendez-vous à retourner
            
        Returns:
            List[Appointment]: La liste des rendez-vous
        """
        appointments = list(self.appointments.values())
        return [deepcopy(appointment) for appointment in appointments[skip:skip + limit]]
    
    async def get_by_patient(self, patient_id: UUID, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """
        Récupère les rendez-vous d'un patient.
        
        Args:
            patient_id: L'ID du patient
            skip: Le nombre de rendez-vous à sauter
            limit: Le nombre maximum de rendez-vous à retourner
            
        Returns:
            List[Appointment]: La liste des rendez-vous du patient
        """
        patient_appointments = [
            appointment for appointment in self.appointments.values()
            if appointment.patient_id == patient_id
        ]
        return [deepcopy(appointment) for appointment in patient_appointments[skip:skip + limit]]
    
    async def get_by_doctor(self, doctor_id: UUID, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """
        Récupère les rendez-vous d'un médecin.
        
        Args:
            doctor_id: L'ID du médecin
            skip: Le nombre de rendez-vous à sauter
            limit: Le nombre maximum de rendez-vous à retourner
            
        Returns:
            List[Appointment]: La liste des rendez-vous du médecin
        """
        doctor_appointments = [
            appointment for appointment in self.appointments.values()
            if appointment.doctor_id == doctor_id
        ]
        return [deepcopy(appointment) for appointment in doctor_appointments[skip:skip + limit]]
    
    async def get_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """
        Récupère les rendez-vous dans une plage de dates.
        
        Args:
            start_date: La date de début
            end_date: La date de fin
            skip: Le nombre de rendez-vous à sauter
            limit: Le nombre maximum de rendez-vous à retourner
            
        Returns:
            List[Appointment]: La liste des rendez-vous dans la plage de dates
        """
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        date_range_appointments = [
            appointment for appointment in self.appointments.values()
            if (
                (appointment.start_time >= start_datetime and appointment.start_time <= end_datetime) or
                (appointment.end_time >= start_datetime and appointment.end_time <= end_datetime)
            )
        ]
        return [deepcopy(appointment) for appointment in date_range_appointments[skip:skip + limit]]
    
    async def count(self) -> int:
        """
        Compte le nombre total de rendez-vous.
        
        Returns:
            int: Le nombre total de rendez-vous
        """
        return len(self.appointments)