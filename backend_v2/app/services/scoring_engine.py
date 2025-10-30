# backend_v2/app/services/scoring_engine.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.session import AssessmentSession, FinalScores
from app.models.test_template import ScoringWeights

async def _calculate_accuracy(session: AssessmentSession, db: AsyncIOMotorDatabase) -> float:
    """
    Mock accuracy calculation.
    Returns a score between 0.0 and 1.0.
    """
    # In a real app, you'd fetch test cases from the template:
    # template_doc = await db["test_templates"].find_one({"_id": session.test_template_id})
    # Then iterate session.live_questions, find matching test cases, 
    # and run the `candidate_answer` against them.
    
    # Mock logic: 
    # Give 0.75 (75%) accuracy for each question that has any answer.
    if not session.live_questions:
        return 0.0
        
    total_answered = sum(1 for q in session.live_questions if q.candidate_answer)
    if total_answered == 0:
        return 0.0
        
    mock_score = total_answered * 0.75
    return mock_score / len(session.live_questions)

async def _calculate_speed_score(session: AssessmentSession) -> float:
    """
    Calculates speed score based on duration.
    Returns a score between 0.0 and 1.0.
    """
    if not session.end_time or not session.start_time:
        return 0.0
        
    duration_seconds = (session.end_time - session.start_time).total_seconds()
    duration_minutes = duration_seconds / 60
    
    # Full score if < 30 mins
    if duration_minutes < 30:
        return 1.0
    # Half score if < 60 mins
    elif duration_minutes < 60:
        return 0.5
    # Low score otherwise
    else:
        return 0.1

async def _calculate_prompt_wellness(session: AssessmentSession) -> float:
    """
    Calculates prompt wellness score based on LLM history.
    Returns a score between 0.0 and 1.0.
    """
    if not session.llm_history:
        return 1.0  # Full score if no prompts were used

    total_prompts = len(session.llm_history)
    blocked_prompts = sum(1 for record in session.llm_history if record.was_blocked)
    
    # Simple ratio: (total - blocked) / total
    wellness_score = (total_prompts - blocked_prompts) / total_prompts
    return wellness_score

async def calculate_final_score(session: AssessmentSession, db: AsyncIOMotorDatabase) -> FinalScores:
    """
    Orchestrates the calculation of all final scores for a session.
    """
    # Retrieve the scoring weights from the session snapshot
    try:
        weights = session.test_weights_snapshot
    except Exception:
        # Fallback if snapshot is missing/invalid
        weights = ScoringWeights() 

    # Calculate individual scores (0.0 to 1.0)
    accuracy = await _calculate_accuracy(session, db)
    speed = await _calculate_speed_score(session)
    wellness = await _calculate_prompt_wellness(session)

    # Apply weights
    total_score_factor = (
        (accuracy * weights.accuracy) +
        (speed * weights.speed_efficiency) +
        (wellness * weights.prompt_wellness)
    )
    
    # Ensure total score is between 0 and 1
    total_score_factor = max(0, min(1, total_score_factor))

    # Return as percentages (0-100)
    return FinalScores(
        accuracy=round(accuracy * 100, 2),
        speed_efficiency=round(speed * 100, 2),
        prompt_wellness=round(wellness * 100, 2),
        total_score=round(total_score_factor * 100, 2)
    )

