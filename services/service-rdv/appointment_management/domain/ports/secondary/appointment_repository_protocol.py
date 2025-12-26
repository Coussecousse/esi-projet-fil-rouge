from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date

from appointment_management.domain.entities.appointment import Appointment

class AppointmentRepositoryProtocol(ABC):
    """
    Port secondaire pour le repository des rendez-vous.
    Cette interface définit comment les opérations sur les rendez-vous doivent être effectuées.
    """
    
    @abstractmethod
    async def get_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        """
        Récupère un rendez-vous par son ID.
        
        Args:
            appointment_id: L'ID du rendez-vous à récupérer
            
        Returns:
            Optional[Appointment]: Le rendez-vous trouvé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    async def create(self, appointment: Appointment) -> Appointment:
        """
        Crée un nouveau rendez-vous.
        
        Args:
            appointment: Le rendez-vous à créer
            
        Returns:
            Appointment: Le rendez-vous créé avec son ID généré
        """
        pass
    
    @abstractmethod
    async def update(self, appointment: Appointment) -> Appointment:
        """
        Met à jour un rendez-vous existant.
        
        Args:
            appointment: Le rendez-vous à mettre à jour
            
        Returns:
            Appointment: Le rendez-vous mis à jour
        """
        pass
    
    @abstractmethod
    async def delete(self, appointment_id: UUID) -> bool:
        """
        Supprime un rendez-vous.
        
        Args:
            appointment_id: L'ID du rendez-vous à supprimer
            
        Returns:
            bool: True si le rendez-vous a été supprimé, False sinon
        """
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """
        Liste tous les rendez-vous avec pagination.
        
        Args:
            skip: Le nombre de rendez-vous à sauter
            limit: Le nombre maximum de rendez-vous à retourner
            
        Returns:
            List[Appointment]: La liste des rendez-vous
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Compte le nombre total de rendez-vous.
        
        Returns:
            int: Le nombre total de rendez-vous
        """
        pass