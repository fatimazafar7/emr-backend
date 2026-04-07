import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from app.database import async_session, Base, engine, create_all_tables
from app.models.clinic import Clinic
from app.models.user import User, UserRole
from app.models.patient import Patient, Gender, BloodType
from app.models.doctor import Doctor
from app.models.appointment import Appointment, AppointmentType, AppointmentStatus
from app.models.prescription import Prescription
from app.models.lab_result import LabResult, ResultStatus, LabStatus
from app.models.vital import Vital
from app.utils.security import hash_password

async def seed_data():
    await create_all_tables()
    async with async_session() as db:
        # Create clinics
        clinics = [
            Clinic(id=uuid.uuid4(), name="EMR AI Central HQ", city="New York", country="USA", is_active=True),
            Clinic(id=uuid.uuid4(), name="Westside Clinic", city="New York", country="USA", is_active=True),
            Clinic(id=uuid.uuid4(), name="North Side Medical", city="New York", country="USA", is_active=True),
        ]
        db.add_all(clinics)
        await db.commit()

        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            email="admin@emr.com",
            hashed_password=hash_password("Admin123!"),
            first_name="System",
            last_name="Admin",
            role=UserRole.admin,
            clinic_id=clinics[0].id
        )
        db.add(admin)
        await db.commit()

        # Create doctors
        doctors = []
        for i in range(3):
            u_id = uuid.uuid4()
            d_user = User(
                id=u_id,
                email=f"doctor{i+1}@emr.com",
                hashed_password=hash_password("Doctor123!"),
                first_name=f"Doctor",
                last_name=f" {i+1}",
                role=UserRole.doctor,
                clinic_id=clinics[i % 3].id
            )
            db.add(d_user)
            await db.flush()
            
            doctor = Doctor(
                id=uuid.uuid4(),
                user_id=u_id,
                clinic_id=clinics[i % 3].id,
                specialty="General Medicine",
                license_number=f"LIC-{uuid.uuid4().hex[:6].upper()}",
                years_experience="10",
                rating=4.8
            )
            db.add(doctor)
            doctors.append(doctor)
        
        # Create patients
        patients = []
        for i in range(5):
            u_id = uuid.uuid4()
            p_user = User(
                id=u_id,
                email=f"patient{i+1}@emr.com",
                hashed_password=hash_password("Patient123!"),
                first_name=f"Patient",
                last_name=f" {i+1}",
                role=UserRole.patient,
                clinic_id=clinics[0].id
            )
            db.add(p_user)
            await db.flush()
            
            patient = Patient(
                id=uuid.uuid4(),
                user_id=u_id,
                clinic_id=clinics[0].id,
                date_of_birth="1990-01-01",
                gender=Gender.male if i % 2 == 0 else Gender.female,
                blood_type=BloodType.O_pos,
                allergies="None"
            )
            db.add(patient)
            patients.append(patient)

        await db.commit()

        # Add appointments, prescriptions, lab results, vitals
        for i, patient in enumerate(patients):
            doc = doctors[i % len(doctors)]
            appointment = Appointment(
                id=uuid.uuid4(),
                patient_id=patient.id,
                doctor_id=doc.id,
                clinic_id=patient.clinic_id,
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
                duration_minutes=30,
                type=AppointmentType.checkup,
                status=AppointmentStatus.scheduled,
                reason="Routine checkup"
            )
            db.add(appointment)
            
            prescription = Prescription(
                id=uuid.uuid4(),
                patient_id=patient.id,
                doctor_id=doc.id,
                appointment_id=appointment.id,
                medication_name="Amoxicillin",
                dosage="500mg",
                frequency="Twice a day",
                duration_days=7,
                instructions="Take after meals",
                is_active=True,
                start_date=datetime.now(timezone.utc)
            )
            db.add(prescription)
            
            lab_result = LabResult(
                id=uuid.uuid4(),
                patient_id=patient.id,
                doctor_id=doc.id,
                test_name="Complete Blood Count",
                test_type="Blood",
                result_value="Normal",
                unit="N/A",
                status=LabStatus.received,
                result_status=ResultStatus.normal,
            )
            db.add(lab_result)

            vital = Vital(
                id=uuid.uuid4(),
                patient_id=patient.id,
                recorded_by=doc.user_id,
                blood_pressure_systolic=120,
                blood_pressure_diastolic=80,
                heart_rate=72,
                temperature=36.6,
                weight_kg=70.0,
                height_cm=175.0,
                blood_oxygen=98,
                recorded_at=datetime.now(timezone.utc)
            )
            db.add(vital)

        await db.commit()
    print("Seeding completed successfully with extended mock data.")

if __name__ == "__main__":
    asyncio.run(seed_data())
