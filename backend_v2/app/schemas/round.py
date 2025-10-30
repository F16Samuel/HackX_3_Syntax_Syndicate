# backend_v2/app/schemas/round.py
from pydantic import BaseModel, ConfigDict, Field
from app.models.pyobjectid import PyObjectId
from app.models.round import RoundBase

class RoundCreate(RoundBase):
    """
    Schema used for creating a new round via the API.
    Inherits all fields from RoundBase.
    """
    pass

class RoundPublic(RoundBase):
    """
    Schema for public-facing round data.
    Inherits base fields and includes the MongoDB ID.
    """
    id: PyObjectId = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )
