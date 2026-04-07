from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.security import verify_token
from app.models.user import User
from sqlalchemy import select

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_role(roles: List[str]):
    # Normalize roles to lowercase strings
    required_roles = [r.lower() for r in roles]
    
    def role_checker(user: User = Depends(get_current_user)):
        # user.role might be an Enum member, let's ensure comparison works
        user_role_str = str(user.role.value).lower() if hasattr(user.role, 'value') else str(user.role).lower()
        
        # Also check if it's an Enum class representation like "UserRole.patient"
        if "." in user_role_str:
            user_role_str = user_role_str.split(".")[-1]
            
        print(f"🕵️ Checking role for {user.email}: '{user_role_str}' vs required {required_roles}")
        
        if user_role_str not in required_roles:
            print(f"❌ Role mismatch: '{user_role_str}' not in {required_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Insufficient permissions",
                    "required_roles": required_roles,
                    "your_role": user_role_str
                }
            )
        
        print(f"✅ Role check passed for '{user_role_str}'")
        return user
    return role_checker
