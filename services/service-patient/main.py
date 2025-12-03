from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://patient_user:patient_pass@db-patient:5432/patients_db")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))

# FastAPI app
app = FastAPI(
    title="Patient Management Service",
    description="Microservice for managing patient data",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    date_of_birth: Optional[str] = None
    address: Optional[str] = None

class PatientResponse(PatientBase):
    id: str
    is_active: bool = True
    created_at: str

# In-memory storage (temporaire - à remplacer par vraie DB)
patients_db = {}

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "patient-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/patients", response_model=PatientResponse, status_code=201)
async def create_patient(patient: PatientBase):
    """Create a new patient"""
    patient_id = f"PAT-{len(patients_db) + 1:04d}"
    patient_data = {
        "id": patient_id,
        **patient.model_dump(),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    patients_db[patient_id] = patient_data
    logger.info(f"Patient created: {patient_id}")
    return patient_data

@app.get("/api/patients", response_model=List[PatientResponse])
async def list_patients(skip: int = 0, limit: int = 100):
    """List all active patients"""
    active_patients = [
        p for p in patients_db.values() 
        if p.get("is_active", True)
    ]
    return active_patients[skip:skip+limit]

@app.get("/api/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    """Get a specific patient by ID"""
    patient = patients_db.get(patient_id)
    if not patient or not patient.get("is_active", True):
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/api/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: str, patient_update: PatientBase):
    """Update patient information"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_data = patients_db[patient_id]
    for key, value in patient_update.model_dump().items():
        patient_data[key] = value
    
    patient_data["updated_at"] = datetime.utcnow().isoformat()
    patients_db[patient_id] = patient_data
    
    logger.info(f"Patient updated: {patient_id}")
    return patient_data

@app.delete("/api/patients/{patient_id}", status_code=204)
async def delete_patient(patient_id: str):
    """Soft delete a patient"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patients_db[patient_id]["is_active"] = False
    patients_db[patient_id]["deleted_at"] = datetime.utcnow().isoformat()
    
    logger.info(f"Patient deleted: {patient_id}")
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
