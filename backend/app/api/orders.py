from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid
import joblib
import pandas as pd
import json

from app import schemas, models
from app.api import deps
from app.core.config import settings
import os

router = APIRouter()

# Load Model (In a real app, do this at startup)
try:
    model = joblib.load(settings.MODEL_PATH)
    meta_path = os.path.join(os.path.dirname(settings.MODEL_PATH), "metadata.json")
    with open(meta_path, "r") as f:
        model_meta = json.load(f)
except Exception as e:
    model = None
    model_meta = {}

def evaluate_risk(order: models.Order, db: Session):
    if not model:
        return
    
    # Feature extraction based on metadata expectations
    # This is simplified. In a real app, you map exact fields.
    features = {
        'order_value': order.total_amount,
        'items_count': len(order.items),
        'address_length': len(order.shipping_address),
        'name_length': len(order.customer_details.get("name", "")),
        'past_orders_from_ip': 0, # Defaulting for now
        'phone_valid': 1 if order.customer_details.get("phone") else 0,
        'email_valid': 1 if "@" in order.customer_details.get("email", "") else 0
    }
    
    df = pd.DataFrame([features])
    
    # Predict
    prob = model.predict_proba(df)[0][1]
    
    risk_tier = "low"
    if prob > 0.7:
        risk_tier = "high"
    elif prob > 0.4:
        risk_tier = "medium"
        
    try:
        classifier = model.named_steps['classifier']
        importances = classifier.feature_importances_
        preprocessor = model.named_steps['preprocessor']
        
        try:
            encoded_features = preprocessor.get_feature_names_out()
        except AttributeError:
            encoded_features = [f"feature_{i}" for i in range(len(importances))]
            
        feat_imp = list(zip(encoded_features, importances))
        feat_imp.sort(key=lambda x: x[1], reverse=True)
        
        top_factors = [f"{f[0]} (weight: {f[1]:.2f})" for f in feat_imp[:3]]
        reasons = {
            "top_features": top_factors, 
            "note": "Explanation shows primary statistical correlations, not direct causation. Certainty is probabilistic."
        }
    except Exception as e:
        reasons = {"top_features": ["Historical pattern match"], "note": "Detailed feature importance unavailable for this model version."}

    
    prediction = models.Prediction(
        order_id=order.id,
        model_version=model_meta.get("model_name", "unknown"),
        risk_score=float(prob),
        risk_tier=risk_tier,
        reasons=reasons
    )
    db.add(prediction)
    db.commit()

@router.post("/", response_model=schemas.OrderResponse)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: schemas.OrderCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    """Create new order."""
    order_id = order_in.id or f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order = models.Order(
        id=order_id,
        merchant_id=current_user.merchant_id,
        customer_details=order_in.customer_details,
        shipping_address=order_in.shipping_address,
        items=order_in.items,
        total_amount=order_in.total_amount,
        status="pending"
    )
    try:
        db.add(order)
        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid order data.")
    
    # Run ML prediction in background
    background_tasks.add_task(evaluate_risk, order, db)
    
    return order

@router.get("/", response_model=List[schemas.OrderWithPrediction])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve orders."""
    orders = db.query(models.Order).filter(models.Order.merchant_id == current_user.merchant_id).offset(skip).limit(limit).all()
    return orders

@router.post("/{order_id}/verify")
def verify_order(
    order_id: str,
    verification_in: schemas.VerificationCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Verify an order."""
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.merchant_id == current_user.merchant_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    verification = models.Verification(
        order_id=order.id,
        user_id=current_user.id,
        action=verification_in.action,
        notes=verification_in.notes
    )
    db.add(verification)
    
    # Update order status based on action
    if verification_in.action == "approve":
        order.status = "verified"
    elif verification_in.action == "prepaid_only":
        order.status = "prepaid_required"
        
    db.commit()
    return {"status": "success"}
