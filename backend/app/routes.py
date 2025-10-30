"""
Protected routes and other application endpoints.
"""
from fastapi import APIRouter, Depends
from .auth.deps import get_current_user, get_current_recruiter
from .auth.schemas import UserResponse

router = APIRouter(prefix="/api/protected", tags=["Protected"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Protected endpoint - requires valid access token.
    """
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        roles=current_user["roles"],
        is_recruiter_verified=current_user.get("is_recruiter_verified", False),
        created_at=current_user["created_at"]
    )


@router.get("/recruiter/dashboard")
async def recruiter_dashboard(current_recruiter: dict = Depends(get_current_recruiter)):
    """
    Sample recruiter-only endpoint.
    
    Requires verified recruiter role.
    """
    return {
        "message": "Welcome to recruiter dashboard",
        "recruiter": {
            "id": str(current_recruiter["_id"]),
            "email": current_recruiter["email"],
            "name": current_recruiter["name"]
        }
    }