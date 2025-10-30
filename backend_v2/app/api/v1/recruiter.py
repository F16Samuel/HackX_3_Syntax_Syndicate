# backend_v2/app/api/v1/recruiter.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List
from app.core.auth_dependency import DbDep, CurrentUserDep, allow_recruiter

from app.models.test_template import TestTemplate, Question, ScoringWeights
from app.models.session import AssessmentSession, SessionStatus
from app.schemas.assessment import TestTemplateCreate

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"],
    dependencies=[allow_recruiter] # Protects all routes in this router
)

@router.post(
    "/test-template",
    response_model=TestTemplate,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new test template"
)
async def create_test_template(
    template_data: TestTemplateCreate,
    db: DbDep,
    current_user: CurrentUserDep
):
    """
    Create a new test template. (Recruiter only)
    
    Matches API contract for: POST /api/v1/recruiter/test-template
    """
    
    # Convert schema models to DB models
    questions = [Question(**q.model_dump()) for q in template_data.questions]
    weights = ScoringWeights(**template_data.weights.model_dump())
    
    new_template = TestTemplate(
        title=template_data.title,
        default_prompt_budget=template_data.default_prompt_budget,
        weights=weights,
        questions=questions,
        created_by=current_user.id
    )

    result = await db["test_templates"].insert_one(
        new_template.model_dump(by_alias=True, exclude=["id"])
    )
    
    created_template = await db["test_templates"].find_one(
        {"_id": result.inserted_id}
    )
    
    if created_template is None:
        raise HTTPException(status_code=500, detail="Failed to create test template")
        
    return TestTemplate(**created_template)

@router.get(
    "/results",
    response_model=List[AssessmentSession],
    summary="Get all completed session results"
)
async def get_all_completed_sessions(db: DbDep):
    """
    Get all assessment sessions that are marked 'completed'. (Recruiter only)
    """
    sessions_cursor = db["assessment_sessions"].find(
        {"status": SessionStatus.COMPLETED}
    )
    # Limit to 100 for performance, add pagination in a real app
    sessions = await sessions_cursor.to_list(length=100) 
    return [AssessmentSession(**s) for s in sessions]

@router.get(
    "/result/{session_id}",
    response_model=AssessmentSession,
    summary="Get a single session result by ID"
)
async def get_session_result(
    session_id: str,
    db: DbDep
):
    """
    Get the detailed result for a specific session by its ID. (Recruiter only)
    
    Matches API contract for: GET /api/v1/recruiter/result/{session_id}
    """
    try:
        obj_id = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    session = await db["assessment_sessions"].find_one({"_id": obj_id})
    
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment session not found."
        )
    
    return AssessmentSession(**session)

