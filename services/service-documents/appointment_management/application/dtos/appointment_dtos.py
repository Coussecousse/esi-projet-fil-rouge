# medisecure-backend/appointment_management/application/dtos/appointment_dtos.py
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from uuid import UUID
import logging
logger = logging.getLogger(__name__)

# DTOs pour la création et la mise à jour de rendez-vous
class AppointmentCreateDTO(BaseModel):
    """DTO pour la création d'un rendez-vous"""
    patient_id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        # Configuration pour que Pydantic accepte et valide correctement les UUID
        json_encoders = {
            UUID: str
        }
        # Permettre de convertir automatiquement les types
        arbitrary_types_allowed = True
    
    @validator('end_time')
    def validate_end_time(cls, end_time, values):
        """Valide que l'heure de fin est après l'heure de début"""
        if 'start_time' in values and end_time <= values['start_time']:
            raise ValueError("L'heure de fin doit être après l'heure de début")
        return end_time
    
    @validator('patient_id', 'doctor_id', pre=True)
    def validate_uuid(cls, v):
        """Valide et convertit les champs UUID"""
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError(f"Format UUID invalide: {v}")
        elif isinstance(v, UUID):
            return v
        else:
            raise ValueError(f"Type non pris en charge pour UUID: {type(v)}")
    
    @validator('start_time', 'end_time', pre=True, always=True)
    def validate_datetime(cls, v):
        """Valide, convertit et rend naive les dates et heures (UTC)"""
        if v is None:
            return v
        dt = v
        # Analyse de chaîne à datetime
        if isinstance(v, str):
            try:
                if v.endswith('Z'):
                    v = v[:-1] + '+00:00'
                dt = datetime.fromisoformat(v)
            except ValueError:
                try:
                    dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        raise ValueError(f"Format de date invalide: {v}. Utilisez le format ISO 8601.")
        # Si le datetime est timezone-aware, le convertir en UTC et le rendre naive
        if isinstance(dt, datetime) and dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        
        return dt

class AppointmentUpdateDTO(BaseModel):
    """DTO pour la mise à jour d'un rendez-vous"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        # Configuration pour que Pydantic accepte et valide correctement les UUID
        json_encoders = {
            UUID: str
        }
        # Permettre de convertir automatiquement les types
        arbitrary_types_allowed = True
    
    @validator('end_time')
    def validate_end_time(cls, end_time, values):
        """Valide que l'heure de fin est après l'heure de début"""
        if end_time and 'start_time' in values and values['start_time'] and end_time <= values['start_time']:
            raise ValueError("L'heure de fin doit être après l'heure de début")
        return end_time
    
    @validator('start_time', 'end_time', pre=True, always=True)
    def validate_datetime(cls, v):
        """Valide, convertit et rend naive les dates et heures (UTC)"""
        if v is None:
            return v
        dt = v
        # Analyse de chaîne à datetime
        if isinstance(v, str):
            try:
                if v.endswith('Z'):
                    v = v[:-1] + '+00:00'
                dt = datetime.fromisoformat(v)
            except ValueError:
                try:
                    dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        raise ValueError(f"Format de date invalide: {v}. Utilisez le format ISO 8601.")
        if isinstance(dt, datetime) and dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    
    @validator('status')
    def validate_status(cls, v):
        """Valide que le statut est valide"""
        if v is not None:
            valid_statuses = ['SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'missed']
            if v not in valid_statuses:
                raise ValueError(f"Statut invalide. Les valeurs valides sont: {', '.join(valid_statuses)}")
        return v

# DTOs pour les réponses
class AppointmentResponseDTO(BaseModel):
    """DTO pour la réponse avec un rendez-vous"""
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True
        json_encoders = {
            UUID: str
        }
        # Permettre les conversions arbitraires de types
        arbitrary_types_allowed = True

class AppointmentListResponseDTO(BaseModel):
    """DTO pour la réponse avec une liste de rendez-vous"""
    appointments: List[AppointmentResponseDTO]
    total: int
    skip: int
    limit: int
    
    class Config:
        # Permettre les conversions arbitraires de types
        arbitrary_types_allowed = True