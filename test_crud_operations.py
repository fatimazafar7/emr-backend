#!/usr/bin/env python3
"""
Comprehensive CRUD Operations Test Script
Tests Patients, Doctors, and Users CRUD operations
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_CREDENTIALS = {"email": "admin@example.com", "password": "admin123"}
DOCTOR_CREDENTIALS = {"email": "doctor@example.com", "password": "doctor123"}

class CRUDTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.doctor_token = None
        self.created_resources = {
            "users": [],
            "patients": [],
            "doctors": []
        }

    async def setup(self):
        """Initialize HTTP session and login"""
        self.session = aiohttp.ClientSession()
        
        # Login as admin
        await self.login("admin", ADMIN_CREDENTIALS)
        
        # Login as doctor
        await self.login("doctor", DOCTOR_CREDENTIALS)

    async def login(self, role: str, credentials: Dict[str, str]):
        """Login and store token"""
        login_url = f"{BASE_URL}/auth/login"
        
        form_data = aiohttp.FormData()
        form_data.add_field('username', credentials['email'])
        form_data.add_field('password', credentials['password'])
        
        try:
            async with self.session.post(login_url, data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get('access_token')
                    if role == "admin":
                        self.admin_token = token
                        print(f"✅ Admin login successful")
                    else:
                        self.doctor_token = token
                        print(f"✅ Doctor login successful")
                else:
                    print(f"❌ {role.title()} login failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
        except Exception as e:
            print(f"❌ {role.title()} login error: {e}")

    def get_headers(self, role: str = "admin"):
        """Get authorization headers"""
        token = self.admin_token if role == "admin" else self.doctor_token
        return {"Authorization": f"Bearer {token}"}

    async def test_user_crud(self):
        """Test User CRUD operations"""
        print("\n🔍 Testing User CRUD Operations...")
        
        # Create user
        user_data = {
            "email": "testuser@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "patient",
            "is_active": True
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/users/", 
                json=user_data,
                headers=self.get_headers("admin")
            ) as response:
                if response.status == 200:
                    user = await response.json()
                    user_id = user['id']
                    self.created_resources["users"].append(user_id)
                    print(f"✅ User created: {user['first_name']} {user['last_name']}")
                    
                    # Read user
                    async with self.session.get(
                        f"{BASE_URL}/users/{user_id}",
                        headers=self.get_headers("admin")
                    ) as response:
                        if response.status == 200:
                            user = await response.json()
                            print(f"✅ User read: {user['email']}")
                        else:
                            print(f"❌ User read failed: {response.status}")
                    
                    # Update user
                    update_data = {"first_name": "Updated", "last_name": "User"}
                    async with self.session.put(
                        f"{BASE_URL}/users/{user_id}",
                        json=update_data,
                        headers=self.get_headers("admin")
                    ) as response:
                        if response.status == 200:
                            print(f"✅ User updated successfully")
                        else:
                            print(f"❌ User update failed: {response.status}")
                    
                    # Delete user
                    async with self.session.delete(
                        f"{BASE_URL}/users/{user_id}",
                        headers=self.get_headers("admin")
                    ) as response:
                        if response.status == 200:
                            print(f"✅ User deleted successfully")
                            self.created_resources["users"].remove(user_id)
                        else:
                            print(f"❌ User deletion failed: {response.status}")
                else:
                    print(f"❌ User creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
        except Exception as e:
            print(f"❌ User CRUD error: {e}")

    async def test_doctor_crud(self):
        """Test Doctor CRUD operations"""
        print("\n🩺 Testing Doctor CRUD Operations...")
        
        # First create a user for the doctor
        user_data = {
            "email": "testdoctor@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Doctor",
            "role": "doctor",
            "is_active": True
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/users/", 
                json=user_data,
                headers=self.get_headers("admin")
            ) as response:
                if response.status == 200:
                    user = await response.json()
                    user_id = user['id']
                    
                    # Create doctor profile
                    doctor_data = {
                        "user_id": user_id,
                        "clinic_id": "00000000-0000-0000-0000-000000000000",  # Default clinic ID
                        "specialty": "Cardiology",
                        "license_number": "MD123456",
                        "years_experience": "5",
                        "rating": 4.5,
                        "is_available": True
                    }
                    
                    async with self.session.post(
                        f"{BASE_URL}/doctors/",
                        json=doctor_data,
                        headers=self.get_headers("admin")
                    ) as response:
                        if response.status == 200:
                            doctor = await response.json()
                            doctor_id = doctor['id']
                            self.created_resources["doctors"].append(doctor_id)
                            print(f"✅ Doctor created: {doctor['user']['first_name']} {doctor['user']['last_name']}")
                            
                            # Read doctor
                            async with self.session.get(
                                f"{BASE_URL}/doctors/{doctor_id}",
                                headers=self.get_headers("admin")
                            ) as response:
                                if response.status == 200:
                                    doctor = await response.json()
                                    print(f"✅ Doctor read: {doctor['specialty']}")
                                else:
                                    print(f"❌ Doctor read failed: {response.status}")
                            
                            # Update doctor
                            update_data = {"specialty": "Updated Specialty", "rating": 4.8}
                            async with self.session.put(
                                f"{BASE_URL}/doctors/{doctor_id}",
                                json=update_data,
                                headers=self.get_headers("admin")
                            ) as response:
                                if response.status == 200:
                                    print(f"✅ Doctor updated successfully")
                                else:
                                    print(f"❌ Doctor update failed: {response.status}")
                            
                            # Delete doctor
                            async with self.session.delete(
                                f"{BASE_URL}/doctors/{doctor_id}",
                                headers=self.get_headers("admin")
                            ) as response:
                                if response.status == 200:
                                    print(f"✅ Doctor deleted successfully")
                                    self.created_resources["doctors"].remove(doctor_id)
                                else:
                                    print(f"❌ Doctor deletion failed: {response.status}")
                        else:
                            print(f"❌ Doctor creation failed: {response.status}")
                            error_text = await response.text()
                            print(f"Error: {error_text}")
                    
                    # Clean up the user
                    async with self.session.delete(
                        f"{BASE_URL}/users/{user_id}",
                        headers=self.get_headers("admin")
                    ) as response:
                        pass  # Ignore result for cleanup
                else:
                    print(f"❌ Doctor user creation failed: {response.status}")
        except Exception as e:
            print(f"❌ Doctor CRUD error: {e}")

    async def test_patient_crud(self):
        """Test Patient CRUD operations"""
        print("\n👥 Testing Patient CRUD Operations...")
        
        # First create a user for the patient
        user_data = {
            "email": "testpatient@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Patient",
            "role": "patient",
            "is_active": True
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/users/", 
                json=user_data,
                headers=self.get_headers("admin")
            ) as response:
                if response.status == 200:
                    user = await response.json()
                    user_id = user['id']
                    
                    # Create patient profile
                    patient_data = {
                        "user_id": user_id,
                        "clinic_id": "00000000-0000-0000-0000-000000000000",  # Default clinic ID
                        "date_of_birth": "1990-01-01",
                        "gender": "male",
                        "blood_type": "A+",
                        "allergies": "None",
                        "emergency_contact_name": "Emergency Contact",
                        "emergency_contact_phone": "555-123-4567",
                        "insurance_provider": "Test Insurance",
                        "insurance_number": "INS123456"
                    }
                    
                    async with self.session.post(
                        f"{BASE_URL}/patients/",
                        json=patient_data,
                        headers=self.get_headers("admin")
                    ) as response:
                        if response.status == 200:
                            patient = await response.json()
                            patient_id = patient['id']
                            self.created_resources["patients"].append(patient_id)
                            print(f"✅ Patient created: {patient['user']['first_name']} {patient['user']['last_name']}")
                            
                            # Read patient
                            async with self.session.get(
                                f"{BASE_URL}/patients/{patient_id}",
                                headers=self.get_headers("admin")
                            ) as response:
                                if response.status == 200:
                                    patient = await response.json()
                                    print(f"✅ Patient read: {patient['blood_type']}")
                                else:
                                    print(f"❌ Patient read failed: {response.status}")
                            
                            # Update patient
                            update_data = {"allergies": "Updated allergies", "blood_type": "AB+"}
                            async with self.session.put(
                                f"{BASE_URL}/patients/{patient_id}",
                                json=update_data,
                                headers=self.get_headers("admin")
                            ) as response:
                                if response.status == 200:
                                    print(f"✅ Patient updated successfully")
                                else:
                                    print(f"❌ Patient update failed: {response.status}")
                            
                            # Delete patient
                            async with self.session.delete(
                                f"{BASE_URL}/patients/{patient_id}",
                                headers=self.get_headers("admin")
                            ) as response:
                                if response.status == 200:
                                    print(f"✅ Patient deleted successfully")
                                    self.created_resources["patients"].remove(patient_id)
                                else:
                                    print(f"❌ Patient deletion failed: {response.status}")
                        else:
                            print(f"❌ Patient creation failed: {response.status}")
                            error_text = await response.text()
                            print(f"Error: {error_text}")
                    
                    # Clean up the user
                    async with self.session.delete(
                        f"{BASE_URL}/users/{user_id}",
                        headers=self.get_headers("admin")
                    ) as response:
                        pass  # Ignore result for cleanup
                else:
                    print(f"❌ Patient user creation failed: {response.status}")
        except Exception as e:
            print(f"❌ Patient CRUD error: {e}")

    async def test_role_based_access(self):
        """Test role-based access control"""
        print("\n🔐 Testing Role-Based Access Control...")
        
        # Test doctor accessing admin endpoints (should fail)
        try:
            async with self.session.get(
                f"{BASE_URL}/users/",
                headers=self.get_headers("doctor")
            ) as response:
                if response.status == 403:
                    print(f"✅ Doctor correctly blocked from admin endpoint")
                else:
                    print(f"❌ Doctor access control failed: {response.status}")
        except Exception as e:
            print(f"❌ Access control test error: {e}")

    async def cleanup(self):
        """Clean up created resources"""
        print("\n🧹 Cleaning up created resources...")
        
        # Clean up any remaining resources
        for resource_type, ids in self.created_resources.items():
            for resource_id in ids:
                try:
                    endpoint = f"{BASE_URL}/{resource_type}/{resource_id}"
                    async with self.session.delete(
                        endpoint,
                        headers=self.get_headers("admin")
                    ) as response:
                        if response.status == 200:
                            print(f"✅ Cleaned up {resource_type[:-1]} {resource_id}")
                except Exception as e:
                    print(f"❌ Cleanup error for {resource_type} {resource_id}: {e}")

    async def run_all_tests(self):
        """Run all CRUD tests"""
        print("🚀 Starting Comprehensive CRUD Operations Test")
        print("=" * 50)
        
        try:
            await self.setup()
            
            # Run CRUD tests
            await self.test_user_crud()
            await self.test_doctor_crud()
            await self.test_patient_crud()
            await self.test_role_based_access()
            
            print("\n" + "=" * 50)
            print("✅ All CRUD tests completed!")
            
        except Exception as e:
            print(f"❌ Test suite error: {e}")
        finally:
            await self.cleanup()
            if self.session:
                await self.session.close()

async def main():
    """Main test runner"""
    tester = CRUDTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
