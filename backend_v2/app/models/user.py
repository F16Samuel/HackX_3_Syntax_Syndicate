# backend_v2/app/models/user.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from app.models.pyobjectid import PyObjectId

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"

class UserInDB(BaseModel):
    """
    User model as stored in the MongoDB database.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(..., unique=True)
    hashed_password: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str},
        json_schema_extra={
            "example": {
                "id": "60d0fe4f5311236168a109ca",
                "email": "user@example.com",
                "role": "candidate",
                "created_at": "2023-01-01T00:00:00"
            }
        }
    )

