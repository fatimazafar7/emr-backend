import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

passed = 0
failed = 0
failed_tests = []

# State
shared_state = {
    "token": None,
    "clinic_id": "00000000-0000-0000-0000-000000000000",
    "admin_token": None,
    "doc_token": None,
    "doctor_user_id": None,
    "doctor_id": None,
    "patient_user_id": None,
    "patient_id": None,
    "appointment_id": None,
    "prescription_id": None,
    "lab_result_id": None,
    "medical_record_id": None,
    "vital_id": None,
    "billing_id": None
}

def log_result(name, method, url, status_code, expected_codes, error_msg=""):
    global passed, failed
    if status_code in expected_codes:
        print(f"✅ PASS - {method} {url} - {status_code}")
        passed += 1
        return True
    else:
        print(f"❌ FAIL - {method} {url} - {status_code} Error: {error_msg}")
        failed += 1
        failed_tests.append(f"{method} {url} - Status: {status_code}, Error: {error_msg}")
        return False

def make_req(name, method, url, expected_codes=(200, 201), data=None, json_data=None, use_auth=True):
    full_url = BASE_URL + url
    headers = {}
    if use_auth and shared_state["token"]:
        headers["Authorization"] = f"Bearer {shared_state['token']}"
        
    try:
        if method == "GET":
            res = requests.get(full_url, headers=headers)
        elif method == "POST":
            # For login, it's form data
            if data is not None:
                res = requests.post(full_url, headers=headers, data=data)
            else:
                res = requests.post(full_url, headers=headers, json=json_data)
        elif method == "PUT":
            res = requests.put(full_url, headers=headers, json=json_data)
        elif method == "PATCH":
            res = requests.patch(full_url, headers=headers, json=json_data)
        else:
            return None
            
        success = log_result(name, method, url, res.status_code, expected_codes, res.text)
        return {"success": success, "data": res.json() if res.content else None, "status": res.status_code}
    except Exception as e:
        log_result(name, method, url, 500, expected_codes, str(e))
        return {"success": False, "data": None, "status": 500}

print("Starting API Tests...")

# 1. HEALTH CHECK
make_req("Health Check", "GET", "/health", use_auth=False) # Note: the root app actually mounts health without /api/v1 prefix, but we will test what was asked if it's there, or test both.
res_health = requests.get("http://localhost:8000/health")
log_result("Health Check Root", "GET", "/health", res_health.status_code, (200,))

# 2. AUTH TESTS
admin_email = f"admin_test_{uuid4().hex[:6]}@example.com"
pw = "Admin123!"
make_req("Register Admin", "POST", "/auth/register", json_data={
    "email": admin_email, "password": pw, "first_name": "Sys", "last_name": "Admin", "role": "admin"
}, use_auth=False)

login_res = make_req("Login Admin", "POST", "/auth/login", data={"username": admin_email, "password": pw}, use_auth=False)
if login_res["success"]:
    shared_state["admin_token"] = login_res["data"]["access_token"]
    shared_state["token"] = shared_state["admin_token"]
    refresh_token = login_res["data"].get("refresh_token")

make_req("Get Me", "GET", "/auth/me")
make_req("Refresh Token", "POST", "/auth/refresh", json_data={"refresh_token": refresh_token} if login_res["success"] else {})

# 3. CLINIC TESTS
clinic_res = make_req("Create Clinic", "POST", "/clinics/", json_data={
    "name": "Test Clinic", "address": "123 Test St", "city": "NY", "state": "NY", "country": "USA", "phone": "123", "email": "c@c.com", "is_active": True
})
if clinic_res["success"] and clinic_res["data"]:
    shared_state["clinic_id"] = clinic_res["data"].get("id", shared_state["clinic_id"])

make_req("List Clinics", "GET", "/clinics/")
if shared_state["clinic_id"]:
    make_req("Get Clinic", "GET", f"/clinics/{shared_state['clinic_id']}")
    make_req("Update Clinic", "PUT", f"/clinics/{shared_state['clinic_id']}", json_data={"name": "Updated Clinic Name"})

# 4. DOCTOR TESTS
doc_email = f"doc_{uuid4().hex[:6]}@example.com"
doc_user_res = make_req("Register Doctor User", "POST", "/auth/register", json_data={
    "email": doc_email, "password": pw, "first_name": "John", "last_name": "Doe", "role": "doctor", "clinic_id": shared_state["clinic_id"]
}, use_auth=False)
if doc_user_res["success"]:
    shared_state["doctor_user_id"] = doc_user_res["data"]["id"]

doc_profile = make_req("Create Doctor Profile", "POST", "/doctors/", json_data={
    "user_id": shared_state.get("doctor_user_id", str(uuid4())),
    "clinic_id": shared_state["clinic_id"],
    "specialty": "Cardiology",
    "license_number": "LIC-123456",
    "years_experience": "5",
    "rating": 5.0,
    "is_available": True
})
if doc_profile["success"] and doc_profile["data"]:
    shared_state["doctor_id"] = doc_profile["data"].get("id")

make_req("List Doctors", "GET", "/doctors/")
if shared_state["doctor_id"]:
    make_req("Get Doctor", "GET", f"/doctors/{shared_state['doctor_id']}")

# 5. PATIENT TESTS
pat_email = f"pat_{uuid4().hex[:6]}@example.com"
pat_user_res = make_req("Register Patient User", "POST", "/auth/register", json_data={
    "email": pat_email, "password": pw, "first_name": "Jane", "last_name": "Smith", "role": "patient", "clinic_id": shared_state["clinic_id"]
}, use_auth=False)
if pat_user_res["success"]:
    shared_state["patient_user_id"] = pat_user_res["data"]["id"]

pat_profile = make_req("Create Patient", "POST", "/patients/", json_data={
    "user_id": shared_state.get("patient_user_id", str(uuid4())),
    "clinic_id": shared_state["clinic_id"],
    "date_of_birth": "1990-01-01",
    "gender": "female",
    "blood_type": "O+",
    "allergies": "Peanuts",
    "emergency_contact_name": "John Smith",
    "emergency_contact_phone": "555-5555",
    "insurance_provider": "BlueCross",
    "insurance_number": "INS123"
})
if pat_profile["success"] and pat_profile["data"]:
    shared_state["patient_id"] = pat_profile["data"].get("id")

make_req("List Patients", "GET", "/patients/")
if shared_state["patient_id"]:
    make_req("Get Patient", "GET", f"/patients/{shared_state['patient_id']}")
    make_req("Update Patient", "PUT", f"/patients/{shared_state['patient_id']}", json_data={"allergies": "None currently"})

# 6. APPOINTMENT TESTS
dummy_doc = shared_state["doctor_id"] or str(uuid4())
dummy_pat = shared_state["patient_id"] or str(uuid4())

doc_login = make_req("Login Doctor", "POST", "/auth/login", data={"username": doc_email, "password": pw}, use_auth=False)
if doc_login["success"]:
    shared_state["doc_token"] = doc_login["data"]["access_token"]
    
# Use doctor token
if shared_state.get("doc_token"):
    shared_state["token"] = shared_state["doc_token"]

appt_res = make_req("Create Appointment", "POST", "/appointments/", json_data={
    "patient_id": dummy_pat,
    "doctor_id": dummy_doc,
    "clinic_id": shared_state["clinic_id"],
    "scheduled_at": "2026-12-01T10:00:00Z",
    "duration_minutes": 30,
    "type": "checkup",
    "status": "scheduled",
    "reason": "Annual checkup",
    "notes": "Patient requested early morning"
})
if appt_res["success"] and appt_res["data"]:
    shared_state["appointment_id"] = appt_res["data"].get("id")

make_req("List Appointments", "GET", "/appointments/")
if shared_state["appointment_id"]:
    make_req("Get Appointment", "GET", f"/appointments/{shared_state['appointment_id']}")
    # Assume PATCH endpoint requires {'status': '...'} or uses query param: using query param as seen in generic fastapi updates often, but json body is safer based on routing pattern. We will pass params and json.
    make_req("Patch Appointment Status", "PATCH", f"/appointments/{shared_state['appointment_id']}/status?status=completed", json_data={"status": "completed"})

# 7. PRESCRIPTION TESTS
pres_res = make_req("Create Prescription", "POST", "/prescriptions/", json_data={
    "patient_id": dummy_pat,
    "doctor_id": dummy_doc,
    "appointment_id": shared_state["appointment_id"],
    "medication_name": "Amoxicillin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "duration_days": 10,
    "instructions": "Take with meals",
    "is_active": True,
    "start_date": "2026-04-01T00:00:00Z"
})
if pres_res["success"] and pres_res["data"]:
    shared_state["prescription_id"] = pres_res["data"].get("id")

make_req("List Prescriptions", "GET", "/prescriptions/")
if shared_state["prescription_id"]:
    make_req("Get Prescription", "GET", f"/prescriptions/{shared_state['prescription_id']}")

# 8. LAB RESULT TESTS
lab_res = make_req("Create Lab Result", "POST", "/lab-results/", json_data={
    "patient_id": dummy_pat,
    "doctor_id": dummy_doc,
    "test_name": "Blood Panel",
    "test_type": "Blood",
    "result_value": "Normal",
    "unit": "mg/dL",
    "normal_range_min": 10.0,
    "normal_range_max": 50.0,
    "status": "pending",
    "result_status": "normal"
})
if lab_res["success"] and lab_res["data"]:
    shared_state["lab_result_id"] = lab_res["data"].get("id")

make_req("List Labs", "GET", "/lab-results/")
if shared_state["lab_result_id"]:
    make_req("Get Lab Result", "GET", f"/lab-results/{shared_state['lab_result_id']}")
    make_req("Patch Lab Status", "PATCH", f"/lab-results/{shared_state['lab_result_id']}/status?status=reviewed")

# 9. MEDICAL RECORDS TESTS
med_res = make_req("Create Medical Record", "POST", "/medical-records/", json_data={
    "patient_id": dummy_pat,
    "doctor_id": dummy_doc,
    "appointment_id": shared_state.get("appointment_id"),
    "record_type": "SOAP Note",
    "chief_complaint": "Headache",
    "diagnosis": "Stress tension",
    "treatment_plan": "Rest",
    "notes": "Patient advised to reduce stress"
})
if med_res["success"] and med_res["data"]:
    shared_state["medical_record_id"] = med_res["data"].get("id")

make_req("List Medical Records", "GET", "/medical-records/")
if shared_state["medical_record_id"]:
    make_req("Get Medical Record", "GET", f"/medical-records/{shared_state['medical_record_id']}")

# 10. VITALS TESTS
vital_res = make_req("Create Vitals", "POST", "/vitals/", json_data={
    "patient_id": dummy_pat,
    "recorded_by": shared_state.get("doctor_user_id", dummy_doc),
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "heart_rate": 70,
    "temperature": 36.6,
    "weight_kg": 70.0,
    "height_cm": 175.0,
    "blood_oxygen": 99,
    "blood_sugar": 90,
    "notes": "Patient looks healthy"
})
if vital_res["success"] and vital_res["data"]:
    shared_state["vital_id"] = vital_res["data"].get("id")

if dummy_pat:
    make_req("List Patient Vitals", "GET", f"/vitals/patient/{dummy_pat}")

# 11. BILLING TESTS
# Billing usually requires admin or receptionist
if shared_state.get("admin_token"):
    shared_state["token"] = shared_state["admin_token"]

bill_res = make_req("Create Billing", "POST", "/billing/", json_data={
    "patient_id": dummy_pat,
    "clinic_id": shared_state["clinic_id"],
    "appointment_id": shared_state["appointment_id"],
    "services": [{"name": "Consultation", "price": 100}],
    "subtotal": 100.0,
    "insurance_coverage": 80.0,
    "total_amount": 20.0,
    "status": "pending",
    "due_date": "2026-12-01T00:00:00Z"
})
if bill_res["success"] and bill_res["data"]:
    shared_state["billing_id"] = bill_res["data"].get("id")

make_req("List Billing", "GET", "/billing/")
if shared_state["billing_id"]:
    make_req("Patch Billing Status", "PATCH", f"/billing/{shared_state['billing_id']}/status?payment_status=paid")

# 12. AI AGENT TESTS
# In order to test AI, we log in as doctor for most of these paths
doc_login = make_req("Login Doctor", "POST", "/auth/login", data={"username": doc_email, "password": pw}, use_auth=False)
if doc_login["success"]:
    shared_state["token"] = doc_login["data"]["access_token"]
    
make_req("AI Diagnosis", "POST", "/ai/diagnosis", json_data={
    "patient_id": dummy_pat, "symptoms": ["headache"], "duration": "1 day", "history": []
})
make_req("AI Records Summary", "POST", "/ai/records-summary", json_data={
    "patient_id": dummy_pat
})
make_req("AI Prescription Check", "POST", "/ai/prescription-check", json_data={
    "patient_id": dummy_pat, "medication": "Advil", "dosage": "200mg", "frequency": "once a day"
})

lab_id = shared_state["lab_result_id"] or str(uuid4())
make_req("AI Lab Interpret", "POST", "/ai/lab-interpret", json_data={
    "lab_result_id": lab_id
})

# Admin specific AI Tests
# Switch back to admin token
if shared_state.get("admin_token"):
    shared_state["token"] = shared_state["admin_token"]

make_req("AI Generate Bill", "POST", "/ai/generate-bill", json_data={
    "appointment_id": shared_state["appointment_id"] or str(uuid4())
})
make_req("AI Stats", "GET", "/ai/stats")
make_req("AI Sessions", "GET", "/ai/sessions")

# Summary format print
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("TEST SUMMARY")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"Total:  {passed + failed}")
print(f"Passed: {passed} ✅")
print(f"Failed: {failed}  ❌")

if failed > 0:
    print("\nFAILED TESTS:")
    for f in failed_tests:
        print(f"- {f}")
