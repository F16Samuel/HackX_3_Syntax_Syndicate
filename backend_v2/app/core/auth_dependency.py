# backend_v2/app/core/auth_dependency.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import ValidationError
from typing import Annotated

from app.db import get_database
from app.core.security import decode_access_token
from app.models.user import UserInDB, UserRole

# This URL tells the OpenAPI docs (e.g., /docs) where to go to get a token.
# It points to one of the login routes as specified.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/candidate/login")

TokenDep = Annotated[str, Depends(oauth2_scheme)]
DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(token: TokenDep, db: DbDep) -> UserInDB:
    """
    Dependency to get the current user from a JWT token.
    Decodes the token, validates the user ID, and fetches the user from MongoDB.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        # Validate that user_id is a valid ObjectId before querying
        user_obj_id = ObjectId(user_id)
    except Exception:
        # This handles invalid ObjectId formats
        raise credentials_exception

    user_doc = await db["users"].find_one({"_id": user_obj_id})
    if user_doc is None:
        raise credentials_exception
    
    try:
        # Parse the doc into the Pydantic model
        return UserInDB(**user_doc)
    except ValidationError:
        # This might happen if the UserInDB model changes but old user docs exist
        raise credentials_exception

# Type annotation for the dependency
CurrentUserDep = Annotated[UserInDB, Depends(get_current_user)]

class RoleChecker:
    """
    Dependency class to check if the current user has one of the allowed roles.
    """
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: CurrentUserDep) -> UserInDB:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user.role.value}' is not authorized for this endpoint."
            )
        return user

# Specific role dependencies for use in routers
allow_candidate = Depends(RoleChecker([UserRole.CANDIDATE]))
allow_recruiter = Depends(RoleChecker([UserRole.RECRUITER]))

