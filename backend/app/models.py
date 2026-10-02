from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(String, primary_key=True, index=True) # e.g. "merch_001"
    name = Column(String, index=True)
    api_key_hash = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    orders = relationship("Order", back_populates="merchant")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.id"))
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="reviewer") # admin, reviewer
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True) # e.g. "ORD-2023-..."
    merchant_id = Column(String, ForeignKey("merchants.id"))
    customer_details = Column(JSON) # name, email, phone
    shipping_address = Column(String)
    items = Column(JSON)
    total_amount = Column(Float)
    status = Column(String, default="pending") # pending, verified, rejected, rto
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    merchant = relationship("Merchant", back_populates="orders")
    predictions = relationship("Prediction", back_populates="order")
    verifications = relationship("Verification", back_populates="order")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"))
    model_version = Column(String)
    risk_score = Column(Float)
    risk_tier = Column(String) # low, medium, high
    reasons = Column(JSON) # e.g. SHAP top features
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    order = relationship("Order", back_populates="predictions")

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String) # approve, reject, request_info
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    order = relationship("Order", back_populates="verifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True) # Can be null for system actions
    action = Column(String)
    resource = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
