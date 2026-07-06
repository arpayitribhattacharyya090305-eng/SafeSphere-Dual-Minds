from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.database_models import User

client = TestClient(app)

def test_auth_flow():
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)

    # Cleanup any existing test user first
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "testuser@safesphere.org").first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()

    # 1. Signup a test user
    signup_payload = {
        "email": "testuser@safesphere.org",
        "password": "testpassword",
        "full_name": "Test SafeSphere Citizen"
    }
    r = client.post("/api/auth/signup", json=signup_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "testuser@safesphere.org"
    assert data["full_name"] == "Test SafeSphere Citizen"
    
    # 2. Login the user
    login_payload = {
        "email": "testuser@safesphere.org",
        "password": "testpassword"
    }
    r = client.post("/api/auth/login", json=login_payload)
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token is not None
    
    # 3. Get profile (/auth/me)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["full_name"] == "Test SafeSphere Citizen"
    
    # 4. Update profile (/auth/profile)
    update_payload = {
        "full_name": "Updated SafeSphere Citizen",
        "location_address": "Khar, Mumbai",
        "location_lat": 19.0682,
        "location_lng": 72.8402,
        "medical_conditions": "Asthma",
        "family_members": [{"name": "Aria", "relationship": "Sister", "age": 22}],
        "emergency_contacts": [{"name": "Papa", "relationship": "Father", "phone": "9876543210"}]
    }
    r = client.put("/api/auth/profile", json=update_payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["full_name"] == "Updated SafeSphere Citizen"
    assert data["location_address"] == "Khar, Mumbai"
    assert data["location_lat"] == 19.0682
    assert data["medical_conditions"] == "Asthma"
    assert data["family_members"] == [{"name": "Aria", "relationship": "Sister", "age": 22}]
    
    # 5. Get profile again to ensure changes persisted
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["full_name"] == "Updated SafeSphere Citizen"
    assert data["location_address"] == "Khar, Mumbai"
    
    # 6. Logout
    r = client.post("/api/auth/logout", headers=headers)
    assert r.status_code == 200
    
    # 7. Me request should now fail
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 401

    # Final database cleanup
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "testuser@safesphere.org").first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()
