from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str] = "reviewer"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    merchant_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Order Schemas
class OrderBase(BaseModel):
    customer_details: Dict[str, Any]
    shipping_address: str
    items: List[Dict[str, Any]]
    total_amount: float

class OrderCreate(OrderBase):
    # Optional ID, if the merchant provides their own
    id: Optional[str] = None

class OrderResponse(OrderBase):
    id: str
    merchant_id: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Prediction Schemas
class PredictionResponse(BaseModel):
    risk_score: float
    risk_tier: str
    reasons: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

# Verification Schemas
class VerificationCreate(BaseModel):
    action: str  # 'approve', 'reject', 'investigate'
    notes: Optional[str] = None

class OrderWithPrediction(OrderResponse):
    predictions: List[PredictionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class GoogleLogin(BaseModel):
    token: str
