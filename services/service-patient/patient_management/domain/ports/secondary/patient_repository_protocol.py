from abc import ABC, abstractmethod
from typing import Optional, List 
from uuid import UUID
from datetime import date

from patient_management.domain.entities.patient import Patient

class PatientRepositoryProtocol(ABC):
    """
    Port secondaire pour le repository des patients.
    Cette interface définit comment les opérations sur les patients doivent être effectuées.
    """
    
    @abstractmethod
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """
        Récupère un patient par son ID.
        
        Args:
            patient_id: L'ID du patient à récupérer
            
        Returns:
            Optional[Patient]: Le patient trouvé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Patient]:
        """
        Récupère un patient par son email.
        
        Args:
            email: L'email du patient à récupérer
            
        Returns:
            Optional[Patient]: Le patient trouvé ou None si non trouvé
        """
        pass
    
    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        """
        Crée un nouveau patient.
        
        Args:
            patient: Le patient à créer
            
        Returns:
            Patient: Le patient créé avec son ID généré
        """
        pass
    
    @abstractmethod
    async def update(self, patient: Patient) -> Patient:
        """
        Met à jour un patient existant.
        
        Args:
            patient: Le patient à mettre à jour
            
        Returns:
            Patient: Le patient mis à jour
        """
        pass
    
    @abstractmethod
    async def delete(self, patient_id: UUID) -> bool:
        """
        Supprime un patient.
        
        Args:
            patient_id: L'ID du patient à supprimer
            
        Returns:
            bool: True si le patient a été supprimé, False sinon
        """
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Liste tous les patients avec pagination.
        
        Args:
            skip: Le nombre de patients à sauter
            limit: Le nombre maximum de patients à retourner
            
        Returns:
            List[Patient]: La liste des patients
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Patient]:
        """
        Recherche des patients selon différents critères.
        
        Args:
            name: Le nom ou prénom du patient (recherche partielle)
            date_of_birth: La date de naissance du patient
            email: L'email du patient (recherche exacte)
            phone: Le numéro de téléphone du patient (recherche partielle)
            skip: Le nombre de patients à sauter
            limit: Le nombre maximum de patients à retourner
            
        Returns:
            List[Patient]: La liste des patients correspondant aux critères
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Compte le nombre total de patients.
        
        Returns:
            int: Le nombre total de patients
        """
        pass