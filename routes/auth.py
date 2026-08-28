from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr

from database import get_db
from models.db_models import User as DBUser
from models.user import UserRegister, UserResponse, Token
from middleware.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & User Management"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    existing_user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # 2. Extract string value from Enum safely
    role_str = user_data.role.value if hasattr(user_data.role, 'value') else str(user_data.role)

    # 3. Hash password and save user
    hashed_pwd = get_password_hash(user_data.password)
    new_user = DBUser(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_pwd,
        role=user_data.role  # Store the Enum directly, SQLAlchemy will handle it
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "role": role_val},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordSchema, db: Session = Depends(get_db)):
    # 1. Look up user by email in your database
    user = db.query(DBUser).filter(DBUser.email == payload.email).first()
    
    if user:
        # TODO: Generate secure reset token, save to DB, and dispatch email via SMTP/SendGrid
        pass
        
    # 2. Always return a generic success message to prevent user enumeration attacks
    return {"message": "If that email exists, password reset instructions have been sent."}

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: DBUser = Depends(get_current_user)):
    return current_user