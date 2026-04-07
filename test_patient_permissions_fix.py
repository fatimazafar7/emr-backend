#!/usr/bin/env python3
"""
Test script to verify patient permissions fix for medical records, prescriptions, and lab results
"""

import asyncio
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

class PatientPermissionsTester:
    def __init__(self):
        self.patient_token = None
        self.patient_user_id = None

    async def setup_patient_login(self):
        """Login as a test patient"""
        login_url = f"{BASE_URL}/auth/login"
        
        # First register a test patient
        register_data = {
            "email": "testpatient@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Patient",
            "role": "patient",
            "clinic_id": "12a681ac-a370-487a-b3ee-3f381d361064"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                print("✅ Test patient registered successfully")
            else:
                print(f"⚠️ Patient registration failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Registration error: {e}")
        
        # Login as patient
        login_data = {
            "username": "testpatient@example.com",
            "password": "testpass123"
        }
        
        try:
            response = requests.post(login_url, data=login_data)
            if response.status_code == 200:
                data = response.json()
                self.patient_token = data.get('access_token')
                self.patient_user_id = data.get('user', {}).get('id')
                print(f"✅ Patient login successful, user_id: {self.patient_user_id}")
                return True
            else:
                print(f"❌ Patient login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get_auth_headers(self):
        """Get authorization headers for patient"""
        return {"Authorization": f"Bearer {self.patient_token}"}

    async def test_medical_records_access(self):
        """Test patient can access their own medical records"""
        print("\n🩺 Testing Medical Records Access...")
        
        try:
            # Test GET all medical records
            response = requests.get(
                f"{BASE_URL}/medical-records/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                records = response.json()
                print(f"✅ Patient can read their medical records: {len(records)} records found")
            else:
                print(f"❌ Medical records GET failed: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Test POST medical record
            record_data = {
                "patient_name": "Test Patient",
                "diagnosis": "Test diagnosis",
                "treatment": "Test treatment",
                "notes": "Test notes",
                "clinic_id": "12a681ac-a370-487a-b3ee-3f381d361064"
            }
            
            response = requests.post(
                f"{BASE_URL}/medical-records/",
                json=record_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 201:
                print("✅ Patient can create medical record")
            else:
                print(f"❌ Medical record creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Medical records test error: {e}")

    async def test_prescriptions_access(self):
        """Test patient can access their own prescriptions"""
        print("\n💊 Testing Prescriptions Access...")
        
        try:
            # Test GET all prescriptions
            response = requests.get(
                f"{BASE_URL}/prescriptions/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                prescriptions = response.json()
                print(f"✅ Patient can read their prescriptions: {len(prescriptions)} prescriptions found")
            else:
                print(f"❌ Prescriptions GET failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Prescriptions test error: {e}")

    async def test_lab_results_access(self):
        """Test patient can access their own lab results"""
        print("\n🔬 Testing Lab Results Access...")
        
        try:
            # Test GET all lab results
            response = requests.get(
                f"{BASE_URL}/lab-results/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                lab_results = response.json()
                print(f"✅ Patient can read their lab results: {len(lab_results)} results found")
            else:
                print(f"❌ Lab results GET failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Lab results test error: {e}")

    async def run_all_tests(self):
        """Run all patient permission tests"""
        print("🚀 Starting Patient Permissions Test")
        print("=" * 50)
        
        # Setup patient login
        if not await self.setup_patient_login():
            print("❌ Cannot proceed without patient login")
            return
        
        # Run tests
        await self.test_medical_records_access()
        await self.test_prescriptions_access()
        await self.test_lab_results_access()
        
        print("\n" + "=" * 50)
        print("✅ Patient permissions test completed!")

async def main():
    """Main test runner"""
    tester = PatientPermissionsTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
