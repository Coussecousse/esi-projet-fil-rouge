# shared/infrastructure/database/models/appointment_model.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from shared.infrastructure.database.connection import Base

class AppointmentStatus(str, enum.Enum):
    """Énumération des statuts de rendez-vous"""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"

class AppointmentModel(Base):
    """Modèle SQLAlchemy pour la table des rendez-vous"""
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informations sur le rendez-vous
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    reason = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relations
    patient = relationship("PatientModel", back_populates="appointments")
    doctor = relationship("UserModel", foreign_keys=[doctor_id])
    
    def __repr__(self):
        return f"<Appointment {self.id} for patient {self.patient_id}>"