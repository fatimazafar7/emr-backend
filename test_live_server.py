#!/usr/bin/env python3

import asyncio
import sys
import os
import requests
import json
import time
import subprocess
from threading import Thread

# Add to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.utils.security import create_access_token
from app.schemas.medical_record import MedicalRecordCreate
from app.models.medical_record import MedicalRecord
from sqlalchemy import select

def start_server():
    """Start the FastAPI server in a subprocess"""
    print("🚀 Starting FastAPI server...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server started successfully")
            return process
    except:
        print("❌ Server failed to start")
        process.terminate()
        return None

async def test_live_endpoint():
    """Test the live medical records endpoint"""
    print("\n🧪 Testing live medical records endpoint...")
    
    async for db in get_db():
        try:
            # Get a test patient
            result = await db.execute(
                select(User, Patient)
                .join(Patient, User.id == Patient.user_id)
                .where(User.role == UserRole.patient)
                .limit(1)
            )
            user_patient = result.first()
            
            if not user_patient:
                print("❌ No test patient found")
                return False
            
            user, patient = user_patient
            print(f"✅ Test user: {user.email}")
            print(f"✅ Patient ID: {patient.id}")
            
            # Create token
            token = create_access_token({"sub": str(user.id)})
            print(f"✅ Token created")
            
            # Test API call
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "patient_name": f"{user.first_name} {user.last_name}",
                "record_type": "lab_result",
                "chief_complaint": "Live test complaint",
                "symptoms": "Live test symptoms",
                "doctor_name": "Live Test Doctor",
                "notes": "Live test notes",
                "visit_date": "2026-04-06",
                "created_by": "patient"
            }
            
            print("📡 Sending request to http://localhost:8000/api/v1/medical-records/")
            
            response = requests.post(
                "http://localhost:8000/api/v1/medical-records/",
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"📤 Response Status: {response.status_code}")
            print(f"📤 Response Body: {response.text[:200]}...")
            
            if response.status_code == 201:
                print("✅ SUCCESS: Medical record created!")
                
                # Clean up the created record
                response_data = response.json()
                if "id" in response_data:
                    record_id = response_data["id"]
                    delete_response = requests.delete(
                        f"http://localhost:8000/api/v1/medical-records/{record_id}",
                        headers=headers,
                        timeout=5
                    )
                    print(f"🧹 Test record deleted: {delete_response.status_code}")
                
                return True
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

async def main():
    print("🔍 === LIVE SERVER VERIFICATION ===\n")
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Cannot start server - aborting test")
        return
    
    try:
        # Test the endpoint
        success = await test_live_endpoint()
        
        if success:
            print("\n🎉 LIVE TEST PASSED!")
            print("✅ Medical records endpoint is working!")
            print("✅ You should be able to add medical records now!")
        else:
            print("\n❌ LIVE TEST FAILED!")
            print("❌ There are still issues with the medical records endpoint")
            print("🔧 Check the server output above for detailed error information")
        
    finally:
        # Stop server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
