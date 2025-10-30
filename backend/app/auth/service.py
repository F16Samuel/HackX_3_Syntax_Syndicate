"""
Authentication service layer containing business logic.
Handles user registration, login, token management, OAuth integration.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from bson import ObjectId
import secrets
import bcrypt
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config import settings
from ..models import UserDocument, RefreshTokenDocument, RecruiterInviteDocument
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # Password hashing
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    # JWT operations
    
    def create_access_token(self, user_id: str, roles: list[str]) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT access token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    # Refresh token operations
    
    async def create_refresh_token(
        self,
        user_id: ObjectId,
        device_info: Optional[dict] = None
    ) -> str:
        """Create and store refresh token in database."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_doc = RefreshTokenDocument(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_info=device_info
        )
        
        await self.db.refresh_tokens.insert_one(refresh_doc.dict(by_alias=True))
        return token
    
    async def verify_refresh_token(self, token: str) -> Optional[ObjectId]:
        """Verify refresh token and return user_id if valid."""
        refresh_doc = await self.db.refresh_tokens.find_one({
            "token": token,
            "revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not refresh_doc:
            return None
        
        return refresh_doc["user_id"]
    
    async def rotate_refresh_token(
        self,
        old_token: str,
        device_info: Optional[dict] = None
    ) -> Optional[Tuple[str, ObjectId]]:
        """
        Rotate refresh token: revoke old, issue new.
        Returns (new_token, user_id) or None if old token invalid.
        """
        user_id = await self.verify_refresh_token(old_token)
        if not user_id:
            return None
        
        # Revoke old token
        await self.db.refresh_tokens.update_one(
            {"token": old_token},
            {"$set": {"revoked": True}}
        )
        
        # Create new token
        new_token = await self.create_refresh_token(user_id, device_info)
        return new_token, user_id
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a refresh token."""
        result = await self.db.refresh_tokens.update_one(
            {"token": token},
            {"$set": {"revoked": True}}
        )
        return result.modified_count > 0
    
    async def revoke_all_user_tokens(self, user_id: ObjectId) -> int:
        """Revoke all refresh tokens for a user."""
        result = await self.db.refresh_tokens.update_many(
            {"user_id": user_id, "revoked": False},
            {"$set": {"revoked": True}}
        )
        return result.modified_count
    
    # User operations
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user document by email."""
        return await self.db.users.find_one({"email": email.lower()})
    
    async def get_user_by_id(self, user_id: ObjectId) -> Optional[dict]:
        """Get user document by ID."""
        return await self.db.users.find_one({"_id": user_id})
    
    async def create_user(
        self,
        email: str,
        name: str,
        password: Optional[str] = None,
        roles: Optional[list[str]] = None,
        is_recruiter_verified: bool = False,
        oauth_data: Optional[dict] = None
    ) -> dict:
        """Create a new user."""
        user_doc = {
            "email": email.lower(),
            "name": name,
            "password_hash": self.hash_password(password) if password else None,
            "roles": roles or ["candidate"],
            "is_recruiter_verified": is_recruiter_verified,
            "oauth": oauth_data,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return user_doc
    
    # Recruiter invite operations
    
    async def verify_invite_code(self, email: str, invite_code: str) -> bool:
        """
        Verify that an invite code is valid for the given email.
        Returns True if valid and not expired.
        """
        invite = await self.db.recruiter_invites.find_one({
            "email": email.lower(),
            "invite_code": invite_code,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        return invite is not None
    
    async def consume_invite_code(self, email: str, invite_code: str) -> bool:
        """
        Mark an invite code as used by deleting it.
        Returns True if successfully consumed.
        """
        result = await self.db.recruiter_invites.delete_one({
            "email": email.lower(),
            "invite_code": invite_code
        })
        return result.deleted_count > 0
    
    # Registration flows
    
    async def register_candidate(
        self,
        email: str,
        password: str,
        name: str
    ) -> Tuple[dict, str, str]:
        """
        Register a new candidate user.
        Returns (user_doc, access_token, refresh_token).
        """
        # Check if user exists
        existing = await self.get_user_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = await self.create_user(
            email=email,
            name=name,
            password=password,
            roles=["candidate"]
        )
        
        # Generate tokens
        access_token = self.create_access_token(str(user["_id"]), user["roles"])
        refresh_token = await self.create_refresh_token(user["_id"])
        
        return user, access_token, refresh_token
    
    async def register_recruiter(
        self,
        email: str,
        password: str,
        name: str,
        invite_code: str
    ) -> Tuple[dict, str, str]:
        """
        Register a new recruiter user with invite code.
        Returns (user_doc, access_token, refresh_token).
        """
        # Check if user exists
        existing = await self.get_user_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")
        
        # Verify invite code
        if not await self.verify_invite_code(email, invite_code):
            raise ValueError("Invalid or expired invite code")
        
        # Create recruiter user (verified)
        user = await self.create_user(
            email=email,
            name=name,
            password=password,
            roles=["recruiter"],
            is_recruiter_verified=True
        )
        
        # Consume invite code
        await self.consume_invite_code(email, invite_code)
        
        # Generate tokens
        access_token = self.create_access_token(str(user["_id"]), user["roles"])
        refresh_token = await self.create_refresh_token(user["_id"])
        
        return user, access_token, refresh_token
    
    # Login flows
    
    async def login_candidate(
        self,
        email: str,
        password: str
    ) -> Tuple[dict, str, str]:
        """
        Authenticate candidate user.
        Returns (user_doc, access_token, refresh_token).
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not user.get("password_hash"):
            raise ValueError("Password login not available for this account")
        
        if not self.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        
        # Check if user is candidate or has no explicit role
        if "candidate" not in user["roles"] and user["roles"]:
            raise ValueError("Invalid credentials")
        
        # Generate tokens
        access_token = self.create_access_token(str(user["_id"]), user["roles"])
        refresh_token = await self.create_refresh_token(user["_id"])
        
        return user, access_token, refresh_token
    
    async def login_recruiter(
        self,
        email: str,
        password: str,
        invite_code: Optional[str] = None
    ) -> Tuple[dict, str, str]:
        """
        Authenticate recruiter user with verification checks.
        Returns (user_doc, access_token, refresh_token).
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not user.get("password_hash"):
            raise ValueError("Password login not available for this account")
        
        if not self.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        
        # Check if user has recruiter role
        if "recruiter" not in user["roles"]:
            raise ValueError("Invalid credentials")
        
        # Check verification status
        if not user.get("is_recruiter_verified", False):
            # If invite code provided, try to verify
            if invite_code and await self.verify_invite_code(email, invite_code):
                await self.db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"is_recruiter_verified": True}}
                )
                await self.consume_invite_code(email, invite_code)
                user["is_recruiter_verified"] = True
            else:
                raise PermissionError("Recruiter pending verification")
        
        # Generate tokens
        access_token = self.create_access_token(str(user["_id"]), user["roles"])
        refresh_token = await self.create_refresh_token(user["_id"])
        
        return user, access_token, refresh_token
    
    # Google OAuth operations
    
    async def get_or_create_oauth_user(
        self,
        google_sub: str,
        email: str,
        name: str,
        picture: Optional[str] = None,
        role: str = "candidate",
        invite_code: Optional[str] = None
    ) -> Tuple[dict, bool]:
        """
        Get existing user by Google sub or create new OAuth user.
        Returns (user_doc, is_new_user).
        
        Security considerations:
        - For recruiter role: requires valid invite code
        - Updates last_login timestamp
        - Respects recruiter verification rules
        """
        # Try to find by Google sub
        user = await self.db.users.find_one({"oauth.google.sub": google_sub})
        
        if user:
            # Update last login
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"oauth.google.last_login": datetime.utcnow()}}
            )
            return user, False
        
        # Try to find by email (link existing account)
        user = await self.get_user_by_email(email)
        
        if user:
            # Link Google OAuth to existing account
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "oauth.google": {
                        "sub": google_sub,
                        "email": email,
                        "picture": picture,
                        "last_login": datetime.utcnow()
                    }
                }}
            )
            user["oauth"] = {
                "google": {
                    "sub": google_sub,
                    "email": email,
                    "picture": picture,
                    "last_login": datetime.utcnow()
                }
            }
            return user, False
        
        # Create new user
        roles = ["candidate"]
        is_verified = False
        
        # Handle recruiter role with invite
        if role == "recruiter":
            if invite_code and await self.verify_invite_code(email, invite_code):
                roles = ["recruiter"]
                is_verified = True
                await self.consume_invite_code(email, invite_code)
            else:
                # Default to candidate if no valid invite
                roles = ["candidate"]
        
        user = await self.create_user(
            email=email,
            name=name,
            password=None,  # OAuth user, no password
            roles=roles,
            is_recruiter_verified=is_verified,
            oauth_data={
                "google": {
                    "sub": google_sub,
                    "email": email,
                    "picture": picture,
                    "last_login": datetime.utcnow()
                }
            }
        )
        
        return user, True
    
    async def verify_recruiter_by_email(self, email: str, verified: bool = True) -> bool:
        """
        Admin operation to manually verify a recruiter.
        Returns True if user found and updated.
        """
        result = await self.db.users.update_one(
            {"email": email.lower(), "recruiter" : {"$in": ["roles"]}},
            {"$set": {"is_recruiter_verified": verified}}
        )
        return result.modified_count > 0