from sqlalchemy import Column, String, Date, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from shared.infrastructure.database.connection import Base

class PatientModel(Base):
    """Modèle SQLAlchemy pour la table des patients"""
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Informations personnelles
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Informations médicales
    blood_type = Column(String, nullable=True)
    allergies = Column(JSONB, nullable=True)
    chronic_diseases = Column(JSONB, nullable=True)
    current_medications = Column(JSONB, nullable=True)
    
    # Informations de consentement
    has_consent = Column(Boolean, default=False)
    consent_date = Column(DateTime, nullable=True)
    gdpr_consent = Column(Boolean, default=False)
    
    # Informations administratives
    insurance_provider = Column(String, nullable=True)
    insurance_id = Column(String, nullable=True)
    
    # Métadonnées
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relations
    user = relationship("UserModel", foreign_keys=[user_id])
    # Utiliser une chaîne simple pour éviter les imports circulaires
    appointments = relationship("AppointmentModel", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"