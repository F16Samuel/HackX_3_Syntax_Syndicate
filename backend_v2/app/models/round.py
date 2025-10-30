# backend_v2/app/models/round.py
from pydantic import BaseModel, Field, ConfigDict
from app.models.pyobjectid import PyObjectId

class RoundBase(BaseModel):
    """
    Base schema for a Round, shared by create and DB models.
    Based on your teammate's model.py.
    """
    title: str
    subtitle: str
    thumbnailUrl: str
    role: str
    whoCanPlay: str
    dateTBA: bool
    startDateTime: str
    endDateTime: str
    displayStartDate: str
    displayStartTime: str
    displayEndDate: str
    displayEndTime: str

class RoundInDB(RoundBase):
    """
    Round model as stored in the MongoDB database.
    It inherits the base fields and adds our standard PyObjectId.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )
