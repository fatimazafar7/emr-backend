#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.security import verify_token
from app.models.user import User
from sqlalchemy import select
import json

class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only debug medical records endpoints
        if "/medical-records/" in str(request.url):
            print(f"\n🔍 === DEBUG MIDDLEWARE ===")
            print(f"📍 URL: {request.url}")
            print(f"📍 Method: {request.method}")
            print(f"📍 Headers: {dict(request.headers)}")
            
            # Check Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header:
                print(f"🔑 Auth Header: {auth_header[:50]}...")
                
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    print(f"🔑 Token: {token[:50]}...")
                    
                    # Verify token
                    payload = verify_token(token)
                    if payload:
                        print(f"✅ Token Payload: {payload}")
                        
                        # Get user from database
                        from app.database import get_db
                        async for db in get_db():
                            try:
                                user_id = payload.get("sub")
                                result = await db.execute(select(User).where(User.id == user_id))
                                user = result.scalar_one_or_none()
                                
                                if user:
                                    print(f"✅ User Found: {user.email}")
                                    print(f"✅ User Role: {user.role}")
                                    print(f"✅ User ID: {user.id}")
                                    print(f"✅ User Active: {user.is_active}")
                                    
                                    # Check if patient has patient profile
                                    if user.role == "patient":
                                        from app.models.patient import Patient
                                        patient_result = await db.execute(
                                            select(Patient).where(Patient.user_id == user.id)
                                        )
                                        patient = patient_result.scalar_one_or_none()
                                        
                                        if patient:
                                            print(f"✅ Patient Profile: {patient.id}")
                                            print(f"✅ Patient Clinic: {patient.clinic_id}")
                                        else:
                                            print(f"❌ NO PATIENT PROFILE FOUND!")
                                else:
                                    print(f"❌ USER NOT FOUND!")
                                
                                break
                            except Exception as e:
                                print(f"❌ Database Error: {e}")
                                break
                    else:
                        print(f"❌ INVALID TOKEN!")
                else:
                    print(f"❌ INVALID AUTH FORMAT!")
            else:
                print(f"❌ NO AUTH HEADER!")
        
        # Continue with the request
        try:
            response = await call_next(request)
            
            # Debug response
            if "/medical-records/" in str(request.url):
                print(f"📤 Response Status: {response.status_code}")
                
                # Try to read response body
                try:
                    body = await response.body()
                    if body:
                        print(f"📤 Response Body: {body.decode()[:200]}...")
                except:
                    pass
                
                print(f"🔍 === END DEBUG ===\n")
            
            return response
            
        except HTTPException as e:
            if "/medical-records/" in str(request.url):
                print(f"❌ HTTP Exception: {e.status_code} - {e.detail}")
                print(f"🔍 === END DEBUG ===\n")
            raise e
        except Exception as e:
            if "/medical-records/" in str(request.url):
                print(f"❌ General Exception: {e}")
                print(f"🔍 === END DEBUG ===\n")
            raise e

# Add this middleware to the FastAPI app
def add_debug_middleware(app):
    app.add_middleware(DebugMiddleware)
    print("🔍 Debug middleware added for medical records endpoints")
