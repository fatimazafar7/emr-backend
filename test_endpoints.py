import urllib.request
import urllib.parse
import json

data = urllib.parse.urlencode({"username": "admin@emr.com", "password": "Admin123!"}).encode("utf-8")
req = urllib.request.Request("http://localhost:8000/api/v1/auth/login", data=data)
try:
    with urllib.request.urlopen(req) as res:
        token = json.loads(res.read().decode("utf-8"))["access_token"]
except Exception as e:
    exit(1)

endpoints = ["/api/v1/doctors/", "/api/v1/appointments/", "/api/v1/billing/", "/api/v1/patients/", "/api/v1/inventory/", "/api/v1/ai/stats"]
for endpoint in endpoints:
    url = "http://localhost:8000" + endpoint
    req2 = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req2) as res:
            print(f"{endpoint}: {res.status}")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"{endpoint}: {e.code} - {err_msg}")
