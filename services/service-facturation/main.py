from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://billing_user:billing_pass@db-mariadb:3306/billing_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InvoiceDB(Base):
    __tablename__ = "invoices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), nullable=False)
    appointment_id = Column(String(36))
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class InvoiceCreate(BaseModel):
    patient_id: str
    appointment_id: Optional[str] = None
    amount: float

class InvoiceResponse(BaseModel):
    id: str
    patient_id: str
    appointment_id: Optional[str]
    amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

app = FastAPI(title="Billing Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "billing-service"}

@app.post("/api/billing/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = InvoiceDB(
        id=str(uuid.uuid4()),
        **invoice.model_dump()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@app.get("/api/billing/invoices", response_model=List[InvoiceResponse])
async def list_invoices(patient_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(InvoiceDB)
    if patient_id:
        query = query.filter(InvoiceDB.patient_id == patient_id)
    return query.all()

@app.get("/api/billing/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
