import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.api import deps
from app.models import Base
import uuid

# Use in-memory SQLite for E2E tests to avoid polluting the actual Supabase DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_e2e.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db
client = TestClient(app)

def test_full_workflow():
    # 1. Register a new user
    email = f"e2e_{uuid.uuid4().hex[:6]}@example.com"
    res = client.post("/api/v1/auth/register", json={"email": email, "password": "password123", "role": "admin"})
    assert res.status_code == 200, f"Registration failed: {res.text}"
    
    # 2. Login
    res = client.post("/api/v1/auth/login", data={"username": email, "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create an order
    order_data = {
        "customer_details": {"name": "Test User", "email": "test@user.com", "phone": "1234567890"},
        "shipping_address": "123 Test St",
        "items": [{"item_id": "SKU-TEST", "price": 100.0}],
        "total_amount": 100.0
    }
    res = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert res.status_code == 200, f"Create order failed: {res.text}"
    order_id = res.json()["id"]
    
    # 4. Fetch orders (Verify prediction was created)
    res = client.get("/api/v1/orders/", headers=headers)
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    assert orders[0]["status"] == "pending"
    # ML runs in background tasks, with TestClient background tasks run immediately synchronously
    assert len(orders[0]["predictions"]) == 1, "ML Prediction was not generated"
    
    # 5. Review & Verify order (Approve)
    res = client.post(f"/api/v1/orders/{order_id}/verify", json={"action": "approve", "notes": "Looks good"}, headers=headers)
    assert res.status_code == 200
    
    # 6. Fetch again to verify status update
    res = client.get("/api/v1/orders/", headers=headers)
    orders = res.json()
    assert orders[0]["status"] == "verified"

    print("\nE2E Workflow completed successfully!")
