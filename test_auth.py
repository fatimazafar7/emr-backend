#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.utils.security import verify_token, create_access_token
from fastapi.security import OAuth2PasswordBearer
from unittest.mock import Mock, AsyncMock

async def test_auth_flow():
    print("🧪 Testing Authentication Flow...")
    
    # Test 1: Token creation and verification
    print("\n1. Testing token creation and verification:")
    test_user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token({"sub": test_user_id})
    print(f"✅ Token created: {token[:50]}...")
    
    payload = verify_token(token)
    print(f"✅ Token verified: {payload}")
    
    # Test 2: Role checking logic
    print("\n2. Testing role checking logic:")
    roles = ["doctor", "admin", "nurse", "patient"]
    print(f"✅ Required roles: {roles}")
    
    # Mock user with different roles
    for role in UserRole:
        mock_user = Mock(spec=User)
        mock_user.role = role.value
        mock_user.email = f"test-{role.value}@example.com"
        
        role_checker = require_role(roles)
        try:
            result = role_checker(mock_user)
            print(f"✅ Role {role.value}: PASSED")
        except Exception as e:
            print(f"❌ Role {role.value}: FAILED - {e}")
    
    # Test 3: User role enum values
    print("\n3. Testing user role enum values:")
    for role in UserRole:
        print(f"✅ {role.name}: '{role.value}' (type: {type(role.value)})")
    
    print("\n🎉 Authentication flow test completed!")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
