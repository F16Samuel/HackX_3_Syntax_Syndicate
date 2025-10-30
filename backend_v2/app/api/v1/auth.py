# backend_v2/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated

from app.db import get_database
from app.schemas.auth import UserCreate, Token
from app.schemas.user import UserPublic
from app.models.user import UserInDB, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.auth_dependency import get_current_user, CurrentUserDep, DbDep

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Type annotation for form dependency
FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

async def _register_user(user_data: UserCreate, role: UserRole, db: AsyncIOMotorDatabase) -> UserPublic:
    """Helper function to register a new user."""
    # Check if email already exists
    existing_user = await db["users"].find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = UserInDB(
        email=user_data.email,
        hashed_password=hashed_password,
        role=role
    )

    # Convert to dict for insertion, using by_alias=True to handle '_id'
    user_doc = new_user.model_dump(by_alias=True, exclude=["id"])
    
    try:
        result = await db["users"].insert_one(user_doc)
    except Exception as e: # Catch potential duplicate key error on email
        await db.client.admin.command('ping') # Check connection
        print(f"Registration Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user."
        )
    
    # Return the public model, matching the API contract
    return UserPublic(
        id=result.inserted_id,
        email=new_user.email,
        role=new_user.role
    )

@router.post(
    "/candidate/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new candidate"
)
async def register_candidate(user_in: UserCreate, db: DbDep):
    """
    Register a new user with the **candidate** role.
    """
    return await _register_user(user_in, UserRole.CANDIDATE, db)

@router.post(
    "/recruiter/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new recruiter"
)
async def register_recruiter(user_in: UserCreate, db: DbDep):
    """
    Register a new user with the **recruiter** role.
    """
    return await _register_user(user_in, UserRole.RECRUITER, db)

async def _login_user(
    form_data: OAuth2PasswordRequestForm,
    role: UserRole,
    db: AsyncIOMotorDatabase
) -> Token:
    """Helper function to log in a user and check their role."""
    user_doc = await db["users"].find_one({"email": form_data.username})

    if not user_doc:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    try:
        user = UserInDB(**user_doc)
    except Exception:
        raise HTTPException(status_code=500, detail="Error processing user data")
        
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # CRITICAL: Verify the user has the role required for this endpoint
    if user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. You are not a '{role.value}'."
        )

    # Create the token with user ID (sub) and role
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    # Return the token response, matching the API contract
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        email=user.email
    )

@router.post("/candidate/login", response_model=Token, summary="Login for candidates")
async def login_candidate(form_data: FormDep, db: DbDep):
    """
    Log in a **candidate** user. Returns a JWT token.
    
    This endpoint uses form-data (username and password) as required by OAuth2.
    """
    return await _login_user(form_data, UserRole.CANDIDATE, db)

@router.post("/recruiter/login", response_model=Token, summary="Login for recruiters")
async def login_recruiter(form_data: FormDep, db: DbDep):
    """
    Log in a **recruiter** user. Returns a JWT token.
    
    This endpoint uses form-data (username and password) as required by OAuth2.
    """
    return await _login_user(form_data, UserRole.RECRUITER, db)


@router.get("/me", response_model=UserPublic, summary="Get current user profile")
async def read_users_me(current_user: CurrentUserDep):
    """
    Get the profile of the currently authenticated user.
    """
    # current_user is UserInDB, Pydantic automatically maps it to UserPublic
    return current_user

