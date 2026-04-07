from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash


class UserService:
    @staticmethod
    async def get_all_users(db: AsyncSession, clinic_id: Optional[UUID] = None) -> List[User]:
        query = select(User)
        if clinic_id:
            query = query.where(User.clinic_id == clinic_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        # Hash the password
        user_data_dict = user_data.dict()
        user_data_dict["hashed_password"] = get_password_hash(user_data_dict.pop("password"))
        
        user = User(**user_data_dict)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        for key, value in user_data.dict(exclude_unset=True).items():
            if key == "password":
                # Hash new password if provided
                setattr(user, "hashed_password", get_password_hash(value))
            else:
                setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True

    @staticmethod
    async def get_users_by_role(db: AsyncSession, role: str, clinic_id: Optional[UUID] = None) -> List[User]:
        query = select(User).where(User.role == role)
        if clinic_id:
            query = query.where(User.clinic_id == clinic_id)
        result = await db.execute(query)
        return result.scalars().all()
