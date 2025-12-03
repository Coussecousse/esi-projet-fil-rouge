from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
import os
from datetime import datetime
import uuid

# Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio_access")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_secret")
BUCKET_NAME = "medical-documents"

# MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure bucket exists
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

app = FastAPI(title="Document Management Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-service"}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...), patient_id: str = None):
    try:
        file_id = str(uuid.uuid4())
        object_name = f"{patient_id}/{file_id}_{file.filename}" if patient_id else f"{file_id}_{file.filename}"
        
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            file.file,
            length=-1,
            part_size=10*1024*1024,
            content_type=file.content_type
        )
        
        return {
            "document_id": file_id,
            "filename": file.filename,
            "patient_id": patient_id,
            "upload_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents(patient_id: str = None):
    try:
        prefix = f"{patient_id}/" if patient_id else ""
        objects = minio_client.list_objects(BUCKET_NAME, prefix=prefix)
        return [{"name": obj.object_name, "size": obj.size} for obj in objects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
