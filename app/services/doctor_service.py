from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse


class DoctorService:
    @staticmethod
    async def get_all_doctors(db: AsyncSession, clinic_id: Optional[UUID] = None) -> List[Doctor]:
        query = select(Doctor)
        if clinic_id:
            query = query.where(Doctor.clinic_id == clinic_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_doctor_by_id(db: AsyncSession, doctor_id: UUID) -> Optional[Doctor]:
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_doctor_by_user_id(db: AsyncSession, user_id: UUID) -> Optional[Doctor]:
        result = await db.execute(select(Doctor).where(Doctor.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_doctor(db: AsyncSession, doctor_data: DoctorCreate) -> Doctor:
        doctor = Doctor(**doctor_data.dict())
        db.add(doctor)
        await db.commit()
        await db.refresh(doctor)
        return doctor

    @staticmethod
    async def update_doctor(db: AsyncSession, doctor_id: UUID, doctor_data: DoctorUpdate) -> Optional[Doctor]:
        doctor = await DoctorService.get_doctor_by_id(db, doctor_id)
        if not doctor:
            return None
        
        for key, value in doctor_data.dict(exclude_unset=True).items():
            setattr(doctor, key, value)
        
        await db.commit()
        await db.refresh(doctor)
        return doctor

    @staticmethod
    async def delete_doctor(db: AsyncSession, doctor_id: UUID) -> bool:
        doctor = await DoctorService.get_doctor_by_id(db, doctor_id)
        if not doctor:
            return False
        
        await db.delete(doctor)
        await db.commit()
        return True
