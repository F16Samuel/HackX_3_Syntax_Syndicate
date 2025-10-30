# backend_v2/app/models/test_template.py
from pydantic import BaseModel, Field, ConfigDict
from app.models.pyobjectid import PyObjectId
from app.config import settings

class Question(BaseModel):
    id: str = Field(..., description="Unique identifier for the question (e.g., 'q1', 'q2')")
    type: str = Field(..., description="Type of question, e.g., 'coding', 'theory'")
    prompt: str = Field(..., description="The main question prompt")
    context: str = Field(default="", description="Optional context or starter code")
    test_cases: list[dict] = Field(default_factory=list, description="List of test cases for coding questions")

class ScoringWeights(BaseModel):
    accuracy: float = Field(default=0.4, ge=0, le=1)
    speed_efficiency: float = Field(default=0.3, ge=0, le=1)
    prompt_wellness: float = Field(default=0.3, ge=0, le=1)

class TestTemplate(BaseModel):
    """
    Model for a test template created by a recruiter.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    created_by: PyObjectId  # References a UserInDB (recruiter)
    questions: list[Question]
    weights: ScoringWeights
    default_prompt_budget: int = Field(default=settings.DEFAULT_PROMPT_BUDGET, gt=0)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )

