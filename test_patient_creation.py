#!/usr/bin/env python3

import asyncio
import hashlib
import requests

# Test login and patient creation
async def test_patient_creation():
    try:
        # Login first with correct hash
        password_hash = hashlib.sha256("password123".encode()).hexdigest()
        
        # First check if user exists with this hash
        check_data = {
            "username": "doctor@test.com",
            "password": "password123"
        }
        
        response = requests.post("http://localhost:8000/api/v1/auth/login", data=check_data)
        print("Login response:", response.status_code)
        
        if response.status_code != 200:
            print("Login failed:", response.text)
            return
            
        login_result = response.json()
        token = login_result["access_token"]
        
        # Create patient
        patient_data = {
            "user": {
                "email": "testpatient3@test.com",
                "password": "password123",
                "first_name": "Test",
                "last_name": "Patient3"
            },
            "user_id": "45d7932c-7221-4b0e-b555-d0d398f4bbe0",  # Use correct doctor user ID
            "clinic_id": "12a681ac-a370-487a-b3ee-3f381d361064",  # Use EMR AI Central HQ
            "date_of_birth": "1990-01-01",
            "gender": "male",  # Lowercase as expected
            "blood_type": "O+",
            "allergies": "None",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "555-0123",
            "insurance_provider": "Test Insurance",
            "insurance_number": "123456789"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post("http://localhost:8000/api/v1/patients/", 
                               json=patient_data, 
                               headers=headers)
        print("Patient creation response:", response.status_code)
        print("Response body:", response.text)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_patient_creation())
