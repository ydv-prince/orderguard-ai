import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from app.database import get_db
from app.models import Base

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

import uuid

def test_register_and_login():
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_{unique_id}@merchant.com"
    
    # Register
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "role": "admin"
    })
    assert res.status_code == 200
    assert res.json()["email"] == email
    
    # Login
    res = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "password123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
    
    return res.json()["access_token"]

def test_create_order():
    token = test_register_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    
    order_data = {
        "customer_details": {"name": "John Doe", "email": "john@example.com"},
        "shipping_address": "123 Main St, Anytown, CA",
        "items": [{"item_id": "SKU-1", "price": 50.0}],
        "total_amount": 50.0
    }
    
    res = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "pending"
    assert res.json()["total_amount"] == 50.0

def test_get_orders():
    token = test_register_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.get("/api/v1/orders/", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
