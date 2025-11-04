from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

class AppointmentStatus(str, Enum):
    """Énumération des statuts de rendez-vous"""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"

@dataclass
class Appointment:
    """
    Entité Appointment du domaine.
    Représente un rendez-vous dans le système MediSecure.
    """
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    @property
    def duration_minutes(self) -> int:
        """Calcule la durée du rendez-vous en minutes"""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Annule le rendez-vous"""
        self.status = AppointmentStatus.CANCELLED
        if reason:
            self.notes = reason
        self.updated_at = datetime.utcnow()
    
    def confirm(self) -> None:
        """Confirme le rendez-vous"""
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Marque le rendez-vous comme terminé"""
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.utcnow()
    
    def reschedule(self, start_time: datetime, end_time: datetime) -> None:
        """Replanifie le rendez-vous"""
        self.start_time = start_time
        self.end_time = end_time
        self.status = AppointmentStatus.SCHEDULED
        self.updated_at = datetime.utcnow()