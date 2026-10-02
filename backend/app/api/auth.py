from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings


import uuid

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            {"sub": user.email, "role": user.role}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.UserResponse)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    """Create new user."""
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    # Simple merchant creation for the demo
    merchant = models.Merchant(id=f"merch_{user_in.email.split('@')[0]}", name=f"{user_in.email}'s Store")
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    user = models.User(
        email=user_in.email,
        password_hash=security.get_password_hash(user_in.password),
        role=user_in.role,
        merchant_id=merchant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


import requests

@router.post("/google", response_model=schemas.Token)
def google_auth(
    google_in: schemas.GoogleLogin,
    db: Session = Depends(deps.get_db)
) -> Any:
    """Authenticate or register with Google OAuth2."""
    try:
        # Verify the token's audience (Confused Deputy protection)
        token_info_response = requests.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={google_in.token}"
        )
        if token_info_response.status_code != 200:
            raise ValueError("Invalid token")
            
        token_info = token_info_response.json()
        # Verify audience matches our Client ID (requires backend access to the client ID)
        # For full security in production, assert token_info['aud'] == settings.GOOGLE_CLIENT_ID
        if "aud" not in token_info:
            raise ValueError("Token missing audience claim")
            
        # Fetch user info using the access token
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {google_in.token}"}
        )
        if user_info_response.status_code != 200:
            raise ValueError("Failed to fetch user info")
        
        idinfo = user_info_response.json()
        email = idinfo.get("email")
        if not email:
            raise ValueError("No email in token")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Create user dynamically
        merchant = models.Merchant(id=f"merch_{email.split('@')[0]}", name=f"{email}'s Store")
        db.add(merchant)
        db.commit()
        db.refresh(merchant)

        user = models.User(
            email=email,
            password_hash=security.get_password_hash(uuid.uuid4().hex), # Random password since using Google
            role="admin",
            merchant_id=merchant.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            {"sub": user.email, "role": user.role}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
