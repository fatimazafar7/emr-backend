import requests

# Login to get token (using default test user)
try:
    res = requests.post("http://localhost:8000/api/v1/auth/login", data={"username": "admin@emr.com", "password": "password"})
    token = res.json().get("access_token")
    if not token:
        print("Login failed:", res.text)
        exit(1)
        
    res2 = requests.get("http://localhost:8000/api/v1/inventory/", headers={"Authorization": f"Bearer {token}"})
    print("STATUS:", res2.status_code)
    print("RESPONSE:", res2.text)
except Exception as e:
    print("Error:", e)
