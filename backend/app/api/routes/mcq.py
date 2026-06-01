import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.mcq import (
    MCQSessionInit, 
    MCQSessionResponse, 
    MCQAnswerSubmit, 
    MCQAnswerResponse,
    MCQSessionSummary,
    MCQQuestion
)
from app.agents.orchestrator.orchestrator import OrchestratorAgent
from app.services.session_manager import session_manager
from app.core.dependencies import get_orchestrator
from app.core.logger.logging import logger

router = APIRouter(prefix="/mcq", tags=["MCQ Interview"])

@router.post("/init", response_model=MCQSessionResponse)
async def init_mcq_session(
    payload: MCQSessionInit,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    session_id = f"mcq-{uuid.uuid4()}"
    logger.info(f"Initializing MCQ session: {session_id}")
    
    # Initialize session state & pre-generate 20 questions
    session = await orchestrator.initialize_mcq_session(
        session_id=session_id,
        difficulty=payload.difficulty,
        topic=payload.topic,
        style=payload.style
    )
    
    # Security/Cheat protection: Strip correct answers, explanations, and engineering reasoning!
    secure_questions = []
    for q in session.questions:
        secure_questions.append(
            MCQQuestion(
                id=q.id,
                question=q.question,
                difficulty=q.difficulty,
                topic=q.topic,
                options=q.options,
                correct_answer="", # Mask
                explanation="",    # Mask
                engineering_reasoning="", # Mask
                difficulty_weight=q.difficulty_weight,
                tags=q.tags
            )
        )
        
    return MCQSessionResponse(
        session_id=session_id,
        questions=secure_questions
    )

@router.post("/submit", response_model=MCQAnswerResponse)
async def submit_mcq_answer(
    payload: MCQAnswerSubmit,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    try:
        response = await orchestrator.process_mcq_answer(
            session_id=payload.session_id,
            question_id=payload.question_id,
            selected_option=payload.selected_option
        )
        return response
    except Exception as e:
        logger.error(f"Error submitting MCQ answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/summary/{session_id}", response_model=MCQSessionSummary)
async def get_mcq_summary(session_id: str):
    session = await session_manager.get_session(session_id)
    
    total = len(session.questions)
    answered = len(session.mcq_answers)
    
    if answered == 0:
        return MCQSessionSummary(
            session_id=session_id,
            total_questions=total,
            correct_answers=0,
            score_percentage=0.0,
            analytics={
                "strengths": ["None compiled"],
                "weaknesses": ["Interview incomplete"],
                "feedback": "Please complete the questions before requesting a summary."
            }
        )
        
    correct_count = sum(1 for ans in session.mcq_answers.values() if ans.is_correct)
    percentage = round((correct_count / answered) * 100, 1)
    
    # Calculate simple topic diagnostics
    topic_correct: dict[str, list[bool]] = {}
    for q in session.questions:
        ans = session.mcq_answers.get(q.id)
        if ans:
            if q.topic not in topic_correct:
                topic_correct[q.topic] = []
            topic_correct[q.topic].append(ans.is_correct)
            
    strengths = []
    weaknesses = []
    
    for topic, results in topic_correct.items():
        success_rate = sum(1 for r in results if r) / len(results)
        if success_rate >= 0.7:
            strengths.append(f"{topic} ({int(success_rate*100)}% accuracy)")
        elif success_rate < 0.5:
            weaknesses.append(f"{topic} ({int(success_rate*100)}% accuracy)")
            
    if not strengths:
        strengths.append("Foundations established; keep practicing high-frequency board rules.")
    if not weaknesses:
        weaknesses.append("Solid overall showing; dive deeper into advanced thermal dissipation.")
        
    feedback = (
        f"You answered {correct_count} of {answered} questions correctly. "
        f"This yields a score of {percentage}%. "
        f"To improve, focus on resolving design challenges in: {', '.join(weaknesses)}."
    )
    
    analytics = {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback
    }
    
    return MCQSessionSummary(
        session_id=session_id,
        total_questions=answered,
        correct_answers=correct_count,
        score_percentage=percentage,
        analytics=analytics
    )
