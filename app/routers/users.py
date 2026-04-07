from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.models.user import User
from app.dependencies import get_current_user, require_role
from app.services.user_service import UserService

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"])),
    clinic_id: Optional[str] = Query(None, description="Filter by clinic ID"),
    role: Optional[str] = Query(None, description="Filter by role")
):
    if role:
        users = await UserService.get_users_by_role(db, role)
    elif clinic_id:
        try:
            clinic_uuid = UUID(clinic_id)
            users = await UserService.get_all_users(db, clinic_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid clinic ID format")
    else:
        users = await UserService.get_all_users(db)
    
    return users

@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        user_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user_obj = await UserService.get_user_by_id(db, user_uuid)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin"]))
):
    # Check if user with this email already exists
    existing_user = await UserService.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user = await UserService.create_user(db, user_in)
    return user

@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin"]))
):
    try:
        user_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Check if email is being updated and if it already exists
    if user_in.email:
        existing_user = await UserService.get_user_by_email(db, user_in.email)
        if existing_user and str(existing_user.id) != id:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user = await UserService.update_user(db, user_uuid, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.delete("/{id}")
async def delete_user(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin"]))
):
    try:
        user_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    success = await UserService.delete_user(db, user_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"status": "ok", "message": "User deleted successfully"}
