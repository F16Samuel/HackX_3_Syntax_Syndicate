# backend_v2/app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserCreate(BaseModel):
    """
    Schema for user registration.
    Matches API contract.
    """
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Schema for the JWT token response.
    Matches API contract.
    """
    access_token: str
    token_type: str
    role: UserRole
    email: EmailStr

