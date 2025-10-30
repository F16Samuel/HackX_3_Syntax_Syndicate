"""
Admin endpoints for recruiter management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db import get_database
from ..auth.schemas import VerifyRecruiterRequest, MessageResponse
from ..auth.service import AuthService
from ..auth.deps import get_auth_service, get_current_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/recruiter", tags=["Admin"])


@router.post("/verify", response_model=MessageResponse)
async def verify_recruiter(
    data: VerifyRecruiterRequest,
    current_admin: dict = Depends(get_current_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Admin endpoint to verify or unverify a recruiter.
    
    Requires admin role.
    
    - **email**: Recruiter email to verify
    - **verified**: True to verify, False to unverify
    
    This allows admins to manually approve recruiter accounts without invite codes.
    """
    try:
        updated = await auth_service.verify_recruiter_by_email(
            email=data.email,
            verified=data.verified
        )
        
        if updated:
            action = "verified" if data.verified else "unverified"
            return MessageResponse(
                message=f"Recruiter {data.email} has been {action}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recruiter not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recruiter verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )