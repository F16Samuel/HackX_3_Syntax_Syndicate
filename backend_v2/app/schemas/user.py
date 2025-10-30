# backend_v2/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.pyobjectid import PyObjectId
from app.models.user import UserRole

class UserPublic(BaseModel):
    """
    Public-facing user schema.
    Matches API contract for /me and register responses.
    """
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )

