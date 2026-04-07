from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import models FIRST to ensure proper SQLAlchemy mapper configuration
from app.models import (
    User, UserRole, Clinic, Doctor, Diagnosis, 
    Visit, Patient, Appointment, MedicalRecord,
    Prescription, LabResult, Vital, Billing,
    InventoryItem, AISession
)

from app.routers import (
    auth, users, patients, doctors, clinics, 
    appointments, prescriptions, lab_results, 
    medical_records, vitals, billing, ai, inventory,
    diagnosis, visits
)
from app.database import create_all_tables
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Middleware (Outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
),

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred.", "details": str(exc)},
    )

@app.on_event("startup")
async def startup_event():
    await create_all_tables()

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/")
async def root():
    return {
        "message": "EMR AI Backend API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(doctors.router, prefix="/api/v1/doctors", tags=["Doctors"])
app.include_router(clinics.router, prefix="/api/v1/clinics", tags=["Clinics"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"])
app.include_router(lab_results.router, prefix="/api/v1/lab-results", tags=["Lab Results"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["Medical Records"])
app.include_router(vitals.router, prefix="/api/v1/vitals", tags=["Vitals"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(diagnosis.router, prefix="/api/v1/diagnoses", tags=["Diagnoses"])
app.include_router(visits.router, prefix="/api/v1/visits", tags=["Visits"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
