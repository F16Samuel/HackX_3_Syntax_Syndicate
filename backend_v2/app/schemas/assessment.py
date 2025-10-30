# backend_v2/app/schemas/assessment.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.pyobjectid import PyObjectId
from app.config import settings

# --- Schemas for Recruiter Endpoints ---

class QuestionSchema(BaseModel):
    """Schema for a question within a test template."""
    id: str
    type: str
    prompt: str
    context: str = ""
    test_cases: list[dict] = []

class ScoringWeightsSchema(BaseModel):
    """Schema for scoring weights within a test template."""
    accuracy: float = Field(default=0.4, ge=0, le=1)
    speed_efficiency: float = Field(default=0.3, ge=0, le=1)
    prompt_wellness: float = Field(default=0.3, ge=0, le=1)

class TestTemplateCreate(BaseModel):
    """
    Schema for creating a new TestTemplate.
    Matches API contract for POST /recruiter/test-template
    """
    title: str
    default_prompt_budget: int = Field(default=settings.DEFAULT_PROMPT_BUDGET, gt=0)
    weights: ScoringWeightsSchema
    questions: list[QuestionSchema]


# --- Schemas for Candidate Endpoints ---

class AssessmentQuestion(BaseModel):
    """A simplified question view for the candidate."""
    id: str
    prompt: str
    context: str

class AssessmentStartResponse(BaseModel):
    """
    Response when a candidate starts a new session.
    Matches API contract for POST /candidate/session/start/{template_id}
    """
    session_id: PyObjectId
    start_time: datetime
    prompt_budget: int
    questions: list[AssessmentQuestion]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )

class SubmitAnswerRequest(BaseModel):
    """
    Payload for submitting an answer to a question.
    Matches API contract for POST /candidate/session/submit-answer/{session_id}
    """
    question_id: str
    answer: str

class LLMPromptRequest(BaseModel):
    """
    Payload for making a request to the LLM assistant.
    Matches API contract for POST /candidate/llm-prompt/{session_id}
    """
    prompt: str

class LLMPromptResponse(BaseModel):
    """
    Response from the LLM assistant.
    Matches API contract for POST /candidate/llm-prompt/{session_id}
    """
    response: str
    was_blocked: bool
    used_prompts: int
    prompt_budget: int

