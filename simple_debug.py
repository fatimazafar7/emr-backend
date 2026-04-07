#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User
from sqlalchemy import select

async def debug_existing_users():
    print("🔍 Debugging existing users...")
    
    async for db in get_db():
        try:
            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            print(f"📊 Found {len(users)} users in database:")
            
            for user in users:
                print(f"✅ User: {user.email}")
                print(f"   ID: {user.id}")
                print(f"   Role: {user.role}")
                print(f"   Active: {user.is_active}")
                print(f"   Clinic: {user.clinic_id}")
                print(f"   Name: {user.first_name} {user.last_name}")
                print("---")
            
            if not users:
                print("❌ No users found in database!")
                print("🔧 You need to create a user first.")
                print("\n💡 To create a test user, run:")
                print("   curl -X POST http://localhost:8000/api/v1/auth/register \\")
                print("     -H 'Content-Type: application/json' \\")
                print("     -d '{")
                print("       \"email\": \"test@example.com\",")
                print("       \"password\": \"password123\",")
                print("       \"first_name\": \"Test\",")
                print("       \"last_name\": \"User\",")
                print("       \"role\": \"patient\"")
                print("     }'")
            
            break
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    asyncio.run(debug_existing_users())
