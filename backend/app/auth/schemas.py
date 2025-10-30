"""
Pydantic schemas for request/response validation in auth endpoints.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# Request Schemas

class RegisterRequest(BaseModel):
    """Candidate registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    
    @validator('password')
    def validate_password(cls, v):
        """Ensure password meets complexity requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class RecruiterRegisterRequest(BaseModel):
    """Recruiter registration request with invite code."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    invite_code: str = Field(..., min_length=6)
    
    @validator('password')
    def validate_password(cls, v):
        """Ensure password meets complexity requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    """Standard login request."""
    email: EmailStr
    password: str


class RecruiterLoginRequest(BaseModel):
    """Recruiter login request with optional invite code for verification."""
    email: EmailStr
    password: str
    invite_code: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request."""
    refresh_token: Optional[str] = None  # Optional if using cookies


# Response Schemas

class TokenResponse(BaseModel):
    """Token response after successful authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    name: str
    roles: List[str]
    is_recruiter_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Admin Schemas

class VerifyRecruiterRequest(BaseModel):
    """Admin request to verify a recruiter."""
    email: EmailStr
    verified: bool = True