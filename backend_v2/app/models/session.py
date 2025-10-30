# backend_v2/app/models/session.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from app.models.pyobjectid import PyObjectId
from app.models.test_template import ScoringWeights

class SessionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"

class PromptRecord(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    candidate_prompt: str
    llm_response: str
    was_blocked: bool
    wellness_score: float = Field(default=0.0, description="Score for this specific prompt (0-1)")

class ChatMessage(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    speaker: str  # "candidate", "interviewer"
    message: str

class LiveQuestion(BaseModel):
    question_id: str
    original_prompt: str
    candidate_answer: str = Field(default="")
    submitted_at: datetime | None = None
    accuracy_score: float = Field(default=0.0, description="Score for this question (0-1)")

class FinalScores(BaseModel):
    accuracy: float = Field(default=0.0, description="Final score (0-100)")
    speed_efficiency: float = Field(default=0.0, description="Final score (0-100)")
    prompt_wellness: float = Field(default=0.0, description="Final score (0-100)")
    total_score: float = Field(default=0.0, description="Final weighted score (0-100)")

class AssessmentSession(BaseModel):
    """
    The main document representing a candidate's test session.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    candidate_id: PyObjectId
    test_template_id: PyObjectId

    # Snapshot of the template weights at session creation time
    test_weights_snapshot: ScoringWeights = Field(..., description="Snapshot of TestTemplate.weights")

    status: SessionStatus = Field(default=SessionStatus.IN_PROGRESS)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = None

    prompt_budget: int
    used_prompts: int = Field(default=0)

    live_questions: list[LiveQuestion]
    llm_history: list[PromptRecord] = Field(default_factory=list)
    interviewer_chat: list[ChatMessage] = Field(default_factory=list)

    final_scores: FinalScores | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )

