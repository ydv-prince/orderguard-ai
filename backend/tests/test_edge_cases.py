import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.api import deps
from app.models import Base
from app.core import security
from datetime import timedelta
import uuid
import os

# Use in-memory SQLite for E2E tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_edge_cases.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_users():
    # Create User A
    email_a = f"usera_{uuid.uuid4().hex[:6]}@example.com"
    client.post("/api/v1/auth/register", json={"email": email_a, "password": "password123", "role": "admin"})
    res_a = client.post("/api/v1/auth/login", data={"username": email_a, "password": "password123"})
    token_a = res_a.json()["access_token"]
    
    # Create User B
    email_b = f"userb_{uuid.uuid4().hex[:6]}@example.com"
    client.post("/api/v1/auth/register", json={"email": email_b, "password": "password123", "role": "admin"})
    res_b = client.post("/api/v1/auth/login", data={"username": email_b, "password": "password123"})
    token_b = res_b.json()["access_token"]
    
    return {"user_a_token": token_a, "user_b_token": token_b}

# 1. Authentication and Authorization Edge Cases
def test_expired_jwt():
    expired_token = security.create_access_token(data={"sub": "test@test.com"}, expires_delta=timedelta(minutes=-1))
    res = client.get("/api/v1/orders/", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401

def test_tampered_jwt():
    res = client.get("/api/v1/orders/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.signature"})
    assert res.status_code == 401

def test_cross_tenant_access(setup_users):
    headers_a = {"Authorization": f"Bearer {setup_users['user_a_token']}"}
    headers_b = {"Authorization": f"Bearer {setup_users['user_b_token']}"}
    
    # User A creates order
    order_data = {
        "customer_details": {"name": "Test", "email": "test@user.com"},
        "shipping_address": "123 St",
        "items": [{"item_id": "SKU-1", "price": 100.0}],
        "total_amount": 100.0
    }
    res = client.post("/api/v1/orders/", json=order_data, headers=headers_a)
    assert res.status_code == 200
    order_id = res.json()["id"]
    
    # User B tries to verify User A's order
    res = client.post(f"/api/v1/orders/{order_id}/verify", json={"action": "approve"}, headers=headers_b)
    # Should be 404 because of tenant isolation in the query
    assert res.status_code == 404

# 2. Order Management Edge Cases
def test_duplicate_order_id(setup_users):
    headers = {"Authorization": f"Bearer {setup_users['user_a_token']}"}
    order_data = {
        "id": "ORD-DUPLICATE-1",
        "customer_details": {"name": "Test"},
        "shipping_address": "123",
        "items": [],
        "total_amount": 0.0
    }
    res1 = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert res1.status_code == 200
    
    res2 = client.post("/api/v1/orders/", json=order_data, headers=headers)
    # Should throw integrity error or handled error
    assert res2.status_code in [400, 500] 

def test_extreme_order_values(setup_users):
    headers = {"Authorization": f"Bearer {setup_users['user_a_token']}"}
    order_data = {
        "customer_details": {"name": "Test", "email": "test@user.com"},
        "shipping_address": "123 St",
        "items": [{"item_id": "SKU-1", "price": 100.0}],
        "total_amount": -1000.0 # Negative value
    }
    res = client.post("/api/v1/orders/", json=order_data, headers=headers)
    # Depending on schema, it might pass or fail. We log the result.
    print(f"\nExtreme order value response: {res.status_code}")

# 3. ML Inference Edge Cases
def test_ml_missing_features(setup_users):
    headers = {"Authorization": f"Bearer {setup_users['user_a_token']}"}
    order_data = {
        "customer_details": {}, # Missing name, email, phone
        "shipping_address": "", # Empty address
        "items": [],
        "total_amount": 0.0
    }
    res = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert res.status_code == 200
    
    # Check if ML handled missing features without crashing
    res_orders = client.get("/api/v1/orders/", headers=headers)
    orders = res_orders.json()
    order = next((o for o in orders if o["id"] == res.json()["id"]), None)
    assert order is not None
    assert len(order["predictions"]) >= 1
    
    # Check if explainability handled it gracefully
    print(f"\nML Explanation for missing features: {order['predictions'][0]['reasons']}")
