from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
from copy import deepcopy

from patient_management.domain.entities.patient import Patient
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol

class InMemoryPatientRepository(PatientRepositoryProtocol):
    """
    Adaptateur secondaire pour le repository des patients en mémoire (pour les tests).
    Implémente le port PatientRepositoryProtocol.
    """
    
    def __init__(self):
        """
        Initialise le repository avec une liste vide de patients.
        """
        self.patients: Dict[UUID, Patient] = {}
        self.email_index: Dict[str, UUID] = {}
    
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """
        Récupère un patient par son ID.
        
        Args:
            patient_id: L'ID du patient à récupérer
            
        Returns:
            Optional[Patient]: Le patient trouvé ou None si non trouvé
        """
        # Retourner une copie du patient pour éviter les modifications non contrôlées
        patient = self.patients.get(patient_id)
        if patient:
            return deepcopy(patient)
        return None
    
    async def get_by_email(self, email: str) -> Optional[Patient]:
        """
        Récupère un patient par son email.
        
        Args:
            email: L'email du patient à récupérer
            
        Returns:
            Optional[Patient]: Le patient trouvé ou None si non trouvé
        """
        patient_id = self.email_index.get(email)
        if not patient_id:
            return None
        
        # Retourner une copie du patient pour éviter les modifications non contrôlées
        patient = self.patients.get(patient_id)
        if patient:
            return deepcopy(patient)
        return None
    
    async def create(self, patient: Patient) -> Patient:
        """
        Crée un nouveau patient.
        
        Args:
            patient: Le patient à créer
            
        Returns:
            Patient: Le patient créé avec son ID généré
        """
        # Stocker une copie du patient pour éviter les modifications non contrôlées
        self.patients[patient.id] = deepcopy(patient)
        
        # Indexer l'email si présent
        if patient.email:
            self.email_index[patient.email] = patient.id
        
        return deepcopy(patient)
    
    async def update(self, patient: Patient) -> Patient:
        """
        Met à jour un patient existant.
        
        Args:
            patient: Le patient à mettre à jour
            
        Returns:
            Patient: Le patient mis à jour
        """
        # Si l'email a changé, mettre à jour l'index d'emails
        if patient.id in self.patients:
            old_patient = self.patients[patient.id]
            if old_patient.email != patient.email:
                # Supprimer l'ancien index
                if old_patient.email:
                    self.email_index.pop(old_patient.email, None)
                
                # Ajouter le nouvel index
                if patient.email:
                    self.email_index[patient.email] = patient.id
        
        # Stocker une copie du patient pour éviter les modifications non contrôlées
        self.patients[patient.id] = deepcopy(patient)
        
        return deepcopy(patient)
    
    async def delete(self, patient_id: UUID) -> bool:
        """
        Supprime un patient.
        
        Args:
            patient_id: L'ID du patient à supprimer
            
        Returns:
            bool: True si le patient a été supprimé, False sinon
        """
        if patient_id not in self.patients:
            return False
        
        patient = self.patients[patient_id]
        
        # Supprimer l'index d'email si présent
        if patient.email:
            self.email_index.pop(patient.email, None)
        
        # Supprimer le patient
        del self.patients[patient_id]
        
        return True
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Liste tous les patients avec pagination.
        
        Args:
            skip: Le nombre de patients à sauter
            limit: Le nombre maximum de patients à retourner
            
        Returns:
            List[Patient]: La liste des patients
        """
        patients = list(self.patients.values())
        
        # Appliquer la pagination
        paginated_patients = patients[skip:skip + limit]
        
        # Retourner des copies des patients pour éviter les modifications non contrôlées
        return [deepcopy(patient) for patient in paginated_patients]
    
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
        # Filtrer les patients selon les critères fournis
        filtered_patients = list(self.patients.values())
        
        if name:
            filtered_patients = [
                p for p in filtered_patients
                if name.lower() in p.first_name.lower() or name.lower() in p.last_name.lower()
            ]
        
        if date_of_birth:
            filtered_patients = [
                p for p in filtered_patients
                if p.date_of_birth == date_of_birth
            ]
        
        if email:
            filtered_patients = [
                p for p in filtered_patients
                if p.email == email
            ]
        
        if phone:
            filtered_patients = [
                p for p in filtered_patients
                if p.phone_number and phone.lower() in p.phone_number.lower()
            ]
        
        # Appliquer la pagination
        paginated_patients = filtered_patients[skip:skip + limit]
        
        # Retourner des copies des patients pour éviter les modifications non contrôlées
        return [deepcopy(patient) for patient in paginated_patients]
    
    async def count(self) -> int:
        """
        Compte le nombre total de patients.
        
        Returns:
            int: Le nombre total de patients
        """
        return len(self.patients)