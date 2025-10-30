"""
Pydantic models for database documents.
These represent the structure of MongoDB documents.
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId
import typing
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler


class PyObjectId(ObjectId):
    """
    Custom type for MongoDB ObjectId, compatible with Pydantic v2.
    """
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: typing.Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Defines the validation logic for Pydantic v2.
        """
        
        # Validator function
        def validate_object_id(v: typing.Any) -> ObjectId:
            if isinstance(v, ObjectId):
                return v
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError('Invalid ObjectId')

        # This schema handles validation from Python code
        python_schema = core_schema.union_schema(
            [
                # Allow validation from an existing ObjectId instance
                core_schema.is_instance_schema(ObjectId),
                # Allow validation from a string or other valid types
                core_schema.no_info_plain_validator_function(validate_object_id),
            ],
            # This handles serialization (e.g., when returning to user as str)
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

        # This schema handles validation from JSON (which is always a string)
        json_schema = core_schema.no_info_plain_validator_function(
            validate_object_id,
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

        # Return the combined schema
        return core_schema.json_or_python_schema(
            json_schema=json_schema,
            python_schema=python_schema
        )


class GoogleOAuthData(BaseModel):
    """Google OAuth account data stored in user document."""
    sub: str  # Google user ID
    email: str
    picture: Optional[str] = None
    last_login: datetime = Field(default_factory=datetime.utcnow)


class OAuthAccounts(BaseModel):
    """Container for OAuth provider accounts."""
    google: Optional[GoogleOAuthData] = None


class UserDocument(BaseModel):
    """User document structure in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    name: str
    password_hash: Optional[str] = None  # None for OAuth-only users
    roles: List[str] = Field(default_factory=lambda: ["candidate"])
    is_recruiter_verified: bool = False
    oauth: Optional[OAuthAccounts] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class RefreshTokenDocument(BaseModel):
    """Refresh token document structure in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    token: str  # Opaque token string
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = False
    device_info: Optional[dict] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class RecruiterInviteDocument(BaseModel):
    """Recruiter invite document structure in MongoDB."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    invite_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    created_by: Optional[PyObjectId] = None  # Admin user who created invite
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )