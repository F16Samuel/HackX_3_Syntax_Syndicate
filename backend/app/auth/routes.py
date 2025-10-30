"""
Authentication route handlers.
Implements all auth endpoints: register, login, refresh, logout, OAuth.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db import get_database
from .schemas import (
    RegisterRequest,
    RecruiterRegisterRequest,
    LoginRequest,
    RecruiterLoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    TokenResponse,
    UserResponse,
    MessageResponse
)
from .service import AuthService
from .deps import get_auth_service, get_current_user
from .oauth import google_oauth_handler
from ..config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================

@router.post("/register/candidate", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new candidate user.
    
    - **email**: Valid email address (will be lowercased)
    - **password**: Minimum 8 characters, must include uppercase, lowercase, and digit
    - **name**: User's full name
    
    Returns access token (15 min) and refresh token (7 days).
    """
    try:
        user, access_token, refresh_token = await auth_service.register_candidate(
            email=data.email,
            password=data.password,
            name=data.name
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/register/recruiter", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_recruiter(
    data: RecruiterRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new recruiter user with invite code.
    
    - **email**: Valid email address (must match invite)
    - **password**: Minimum 8 characters, must include uppercase, lowercase, and digit
    - **name**: User's full name
    - **invite_code**: Valid invite code (issued by admin)
    
    Recruiter will be automatically verified if invite code is valid.
    Returns access token (15 min) and refresh token (7 days).
    """
    try:
        user, access_token, refresh_token = await auth_service.register_recruiter(
            email=data.email,
            password=data.password,
            name=data.name,
            invite_code=data.invite_code
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Recruiter registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post("/login/candidate", response_model=TokenResponse)
async def login_candidate(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Candidate login with email and password.
    
    Returns access token (15 min) and refresh token (7 days).
    """
    try:
        user, access_token, refresh_token = await auth_service.login_candidate(
            email=data.email,
            password=data.password
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Candidate login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login/recruiter", response_model=TokenResponse)
async def login_recruiter(
    data: RecruiterLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Recruiter login with email, password, and optional invite code.
    
    - **email**: Recruiter email
    - **password**: Recruiter password
    - **invite_code**: Optional invite code for on-the-fly verification
    
    Recruiter must be verified to login. If not verified but valid invite_code
    is provided, account will be verified during login.
    
    Returns access token (15 min) and refresh token (7 days).
    
    Errors:
    - 401: Invalid credentials
    - 403: Recruiter pending verification (no valid invite provided)
    """
    try:
        user, access_token, refresh_token = await auth_service.login_recruiter(
            email=data.email,
            password=data.password,
            invite_code=data.invite_code
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Recruiter login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


# ============================================================================
# GOOGLE OAUTH ENDPOINTS
# ============================================================================

@router.get("/google/login")
async def google_login(
    request: Request,
    role: str = "candidate",
    invite_code: str = None
):
    """
    Initiate Google OAuth login flow.
    
    Query parameters:
    - **role**: "candidate" (default) or "recruiter"
    - **invite_code**: Required if role=recruiter for new users
    
    Redirects to Google consent screen. After user approves,
    Google will redirect to /api/auth/google/callback.
    
    Security note: role and invite_code are encoded in OAuth state parameter
    and will be validated on callback.
    """
    try:
        # Generate authorization URL with state
        auth_url = await google_oauth_handler.get_authorization_url(
            request,
            role=role if role in ["candidate", "recruiter"] else "candidate",
            invite_code=invite_code
        )
        return RedirectResponse(auth_url)
    except Exception as e:
        logger.error(f"Google OAuth initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Google OAuth callback handler.
    
    This endpoint is called by Google after user approves OAuth consent.
    
    Flow:
    1. Exchange authorization code for tokens
    2. Verify ID token and extract user info
    3. Get or create user in database
    4. Apply recruiter verification rules if applicable
    5. Issue access and refresh tokens
    6. Redirect to frontend with tokens (or return JSON for testing)
    
    Security checks:
    - Email must be verified by Google
    - Recruiter role requires valid invite code
    - Existing recruiters must be verified or have valid invite
    """
    try:
        # Handle OAuth callback
        oauth_data = await google_oauth_handler.handle_callback(request)
        
        # Extract state data
        state = oauth_data.get("state", {})
        role = state.get("role", "candidate")
        invite_code = state.get("invite_code")
        
        # Get or create user
        user, is_new = await auth_service.get_or_create_oauth_user(
            google_sub=oauth_data["sub"],
            email=oauth_data["email"],
            name=oauth_data["name"],
            picture=oauth_data.get("picture"),
            role=role,
            invite_code=invite_code
        )
        
        # Check recruiter verification for existing users
        if not is_new and "recruiter" in user.get("roles", []):
            if not user.get("is_recruiter_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiter pending verification. Please contact admin."
                )
        
        # Generate tokens
        access_token = auth_service.create_access_token(
            str(user["_id"]),
            user["roles"]
        )
        refresh_token = await auth_service.create_refresh_token(user["_id"])
        
        # In production, redirect to frontend with tokens
        # For now, return JSON response for testing
        # Recommended: redirect to frontend URL with tokens in query params or POST to frontend
        # Example: return RedirectResponse(f"https://yourfrontend.com/auth/callback?access_token={access_token}&refresh_token={refresh_token}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "name": user["name"],
                "roles": user["roles"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )


# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token.
    
    Implements token rotation for security:
    - Old refresh token is revoked
    - New refresh token is issued
    - New access token is issued
    
    This prevents refresh token reuse attacks.
    
    **Cookie-based alternative:**
    To use HTTP-only cookies instead of JSON body, modify this endpoint to:
    1. Read refresh_token from cookies: `request.cookies.get("refresh_token")`
    2. Set new refresh_token in Set-Cookie header on response
    3. Configure cookie options: httpOnly=True, secure=True (HTTPS), sameSite="lax"
    """
    try:
        # Rotate refresh token (revoke old, issue new)
        result = await auth_service.rotate_refresh_token(data.refresh_token)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        new_refresh_token, user_id = result
        
        # Get user for roles
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new access token
        access_token = auth_service.create_access_token(
            str(user["_id"]),
            user["roles"]
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: LogoutRequest = None,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by revoking refresh token.
    
    Options:
    1. Revoke specific token (provide refresh_token in body)
    2. Revoke all tokens for user (no refresh_token provided)
    
    For cookie-based refresh tokens, read from cookies instead of body.
    """
    try:
        if data and data.refresh_token:
            # Revoke specific token
            revoked = await auth_service.revoke_refresh_token(data.refresh_token)
            if revoked:
                return MessageResponse(message="Logged out successfully")
            else:
                return MessageResponse(message="Token already revoked or not found")
        else:
            # Revoke all user tokens
            count = await auth_service.revoke_all_user_tokens(current_user["_id"])
            return MessageResponse(message=f"Logged out from {count} device(s)")
            
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


