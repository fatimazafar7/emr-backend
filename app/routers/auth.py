from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, TokenRefresh
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role,
        clinic_id=user_in.clinic_id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create corresponding profile based on role
    if user.role == "patient":
        from app.models.patient import Patient
        patient = Patient(
            user_id=user.id,
            clinic_id=user.clinic_id or "12a681ac-a370-487a-b3ee-3f381d361064",  # Default clinic
            date_of_birth="1990-01-01",  # Default, can be updated later
            gender="other",  # Default, can be updated later
            blood_type="O+",  # Default, can be updated later
            allergies="None recorded",  # Default, can be updated later
            emergency_contact_name="Not provided",  # Default, can be updated later
            emergency_contact_phone="Not provided",  # Default, can be updated later
            insurance_provider="Not provided",  # Default, can be updated later
            insurance_number="Not provided"  # Default, can be updated later
        )
        db.add(patient)
        await db.commit()
        
    elif user.role == "doctor":
        from app.models.doctor import Doctor
        doctor = Doctor(
            user_id=user.id,
            clinic_id=user.clinic_id or "12a681ac-a370-487a-b3ee-3f381d361064",  # Default clinic
            specialization="General Practice",  # Default, can be updated later
            license_number="Pending",  # Default, can be updated later
            experience_years=0,  # Default, can be updated later
            education="Not provided",  # Default, can be updated later
            certifications="None"  # Default, can be updated later
        )
        db.add(doctor)
        await db.commit()
    
    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user

@router.post("/refresh")
async def refresh_token(token_in: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = verify_token(token_in.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}
