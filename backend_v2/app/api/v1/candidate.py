# backend_v2/app/api/v1/candidate.py
from fastapi import (
    APIRouter, Depends, HTTPException, status, 
    WebSocket, WebSocketDisconnect
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

from app.core.auth_dependency import DbDep, CurrentUserDep, allow_candidate
from app.models.test_template import TestTemplate
from app.models.session import (
    AssessmentSession, LiveQuestion, PromptRecord, SessionStatus
)
from app.schemas.assessment import (
    AssessmentStartResponse, AssessmentQuestion, SubmitAnswerRequest,
    LLMPromptRequest, LLMPromptResponse
)
from app.models.session import FinalScores
from app.services import llm_gatekeeper, websocket_manager, scoring_engine

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"],
    dependencies=[allow_candidate] # Protects all routes in this router
)

# Global connection manager for websockets
ws_manager = websocket_manager.ConnectionManager()


@router.post(
    "/session/start/{template_id}",
    response_model=AssessmentStartResponse,
    summary="Start a new assessment session"
)
async def start_assessment_session(
    template_id: str,
    db: DbDep,
    current_user: CurrentUserDep
):
    """
    Start a new assessment session from a template. (Candidate only)
    
    Matches API contract for: POST /api/v1/candidate/session/start/{template_id}
    """
    try:
        template_obj_id = ObjectId(template_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid template ID format")

    template_doc = await db["test_templates"].find_one({"_id": template_obj_id})
    if not template_doc:
        raise HTTPException(status_code=404, detail="Test template not found")

    template = TestTemplate(**template_doc)

    # Create snapshot of live questions
    live_questions = [
        LiveQuestion(
            question_id=q.id,
            original_prompt=q.prompt
            # candidate_answer remains default ""
        ) for q in template.questions
    ]
    
    # Create the new session
    new_session = AssessmentSession(
        candidate_id=current_user.id,
        test_template_id=template.id,
        # CRITICAL: Snapshot the weights
        test_weights_snapshot=template.weights, 
        prompt_budget=template.default_prompt_budget,
        live_questions=live_questions
        # Status defaults to IN_PROGRESS
    )

    result = await db["assessment_sessions"].insert_one(
        new_session.model_dump(by_alias=True, exclude=["id"])
    )
    
    # Prepare response questions (simplified view)
    response_questions = [
        AssessmentQuestion(
            id=q.id,
            prompt=q.prompt,
            context=q.context
        ) for q in template.questions
    ]

    # Return response matching API contract
    return AssessmentStartResponse(
        session_id=result.inserted_id,
        start_time=new_session.start_time,
        prompt_budget=new_session.prompt_budget,
        questions=response_questions
    )

@router.post(
    "/session/submit-answer/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Submit an answer for a question"
)
async def submit_answer(
    session_id: str,
    payload: SubmitAnswerRequest,
    db: DbDep,
    current_user: CurrentUserDep
):
    """
    Submit an answer for a specific question in the session. (Candidate only)
    
    Matches API contract for: POST /api/v1/candidate/session/submit-answer/{session_id}
    """
    try:
        session_obj_id = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Atomically find and update the specific question in the live_questions array
    query = {
        "_id": session_obj_id,
        "candidate_id": current_user.id,
        "live_questions.question_id": payload.question_id
    }
    update = {
        "$set": {
            "live_questions.$.candidate_answer": payload.answer,
            "live_questions.$.submitted_at": datetime.now(timezone.utc)
        }
    }
    
    result = await db["assessment_sessions"].update_one(query, update)

    if result.matched_count == 0:
        # This could be due to invalid session_id, wrong user, or invalid question_id
        raise HTTPException(
            status_code=404,
            detail="Session not found or question ID is invalid for this session."
        )

    return {"message": "Answer submitted successfully"}

@router.post(
    "/llm-prompt/{session_id}",
    response_model=LLMPromptResponse,
    summary="Use an LLM prompt hint"
)
async def use_llm_prompt(
    session_id: str,
    payload: LLMPromptRequest,
    db: DbDep,
    current_user: CurrentUserDep
):
    """
    Use one LLM prompt from the budget. (Candidate only)
    
    Matches API contract for: POST /api/v1/candidate/llm-prompt/{session_id}
    """
    try:
        session_obj_id = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Get the session
    session_doc = await db["assessment_sessions"].find_one({
        "_id": session_obj_id,
        "candidate_id": current_user.id
    })

    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = AssessmentSession(**session_doc)

    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="This session is already completed.")

    # Check budget
    if session.used_prompts >= session.prompt_budget:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Prompt budget exceeded."
        )

    # Call the gatekeeper service
    response, was_blocked = await llm_gatekeeper.get_llm_assistance(payload.prompt)
    
    # Create the new record
    new_record = PromptRecord(
        candidate_prompt=payload.prompt,
        llm_response=response,
        was_blocked=was_blocked,
        wellness_score=0.0 if was_blocked else 1.0 # Simple wellness score
    )

    # Atomically update the session
    update_result = await db["assessment_sessions"].update_one(
        {"_id": session.id},
        {
            "$push": {"llm_history": new_record.model_dump()},
            "$inc": {"used_prompts": 1}
        }
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update session prompt history.")
    
    current_used_prompts = session.used_prompts + 1
    
    # Return response matching API contract
    return LLMPromptResponse(
        response=response,
        was_blocked=was_blocked,
        used_prompts=current_used_prompts,
        prompt_budget=session.prompt_budget
    )

@router.post(
    "/session/end/{session_id}",
    response_model=FinalScores,
    summary="End the session and get scores"
)
async def end_session(
    session_id: str,
    db: DbDep,
    current_user: CurrentUserDep
):
    """
    End the session and trigger final scoring. (Candidate only)
    
    Matches API contract for: POST /api/v1/candidate/session/end/{session_id}
    """
    try:
        session_obj_id = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Get the session
    session_doc = await db["assessment_sessions"].find_one({
        "_id": session_obj_id,
        "candidate_id": current_user.id
    })
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")

    session = AssessmentSession(**session_doc)
    
    if session.status == SessionStatus.COMPLETED:
        # If already completed, just return the scores
        if session.final_scores:
            return session.final_scores
        else:
            # This case shouldn't happen, but good to handle
            raise HTTPException(status_code=400, detail="Session completed but no scores found.")
    
    session.end_time = datetime.now(timezone.utc)
    session.status = SessionStatus.COMPLETED

    # Calculate final scores
    final_scores = await scoring_engine.calculate_final_score(session, db)
    
    # Update the session in the database
    await db["assessment_sessions"].update_one(
        {"_id": session.id},
        {
            "$set": {
                "status": session.status,
                "end_time": session.end_time,
                "final_scores": final_scores.model_dump()
            }
        }
    )
    
    return final_scores


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: DbDep
):
    """
    WebSocket endpoint for real-time chat with the "interviewer".
    
    Note: Standard auth dependencies don't work on WebSockets.
    A production app would pass the token in the query params or as
    the first message, then validate it.
    """
    
    # TODO: Add WebSocket-based authentication
    # Example:
    # token = websocket.query_params.get("token")
    # try:
    #     user = await get_current_user(token, db)
    #     if user.role != UserRole.CANDIDATE:
    #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #         return
    # except:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     return
    
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Save candidate message and broadcast
            await websocket_manager.save_and_broadcast_message(
                db=db,
                session_id=session_id,
                speaker="candidate",
                message=data,
                manager=ws_manager
            )

            # Get and broadcast chatbot response
            chatbot_response = await websocket_manager.get_chatbot_response(data)
            await websocket_manager.save_and_broadcast_message(
                db=db,
                session_id=session_id,
                speaker="interviewer",
                message=chatbot_response,
                manager=ws_manager
            )

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        ws_manager.disconnect(websocket)

