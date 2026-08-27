from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    INVESTIGATOR = "Investigator"
    SPONSOR = "Sponsor"
    AUDITOR = "Auditor"
    ETHICS_COMMITTEE = "Ethics_Committee"
    ADMIN = "Admin"

class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.INVESTIGATOR

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True