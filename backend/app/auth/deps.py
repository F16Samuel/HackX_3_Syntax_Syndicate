"""
FastAPI dependencies for authentication.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional

from ..db import get_database
from .service import AuthService

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Validates:
    - Token signature
    - Token expiration
    - User exists in database
    
    Returns user document.
    """
    token = credentials.credentials
    
    # Validate token and get user ID

    payload = auth_service.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await auth_service.get_user_by_id(ObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure current user is an admin.
    """
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin privileges required"
        )
    return current_user

async def get_current_recruiter(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure current user is a verified recruiter.
    """
    if "recruiter" not in current_user.get("roles", []):
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Recruiter privileges required"
        )
    if not current_user.get("is_recruiter_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter account not verified"
        )

    return current_user