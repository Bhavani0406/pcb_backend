import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.voice import VoiceSessionInit, VoiceQuestionResponse, VoiceSessionSummary
from app.agents.orchestrator.orchestrator import OrchestratorAgent
from app.services.session_manager import session_manager
from app.core.dependencies import get_orchestrator, get_scoring_agent
from app.agents.scoring_agent.scoring import ScoringAgent
from app.core.logger.logging import logger

router = APIRouter(prefix="/interview", tags=["Voice Interview"])

@router.post("/voice/init", response_model=VoiceQuestionResponse)
async def init_voice_session(
    payload: VoiceSessionInit,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    session_id = f"voice-{uuid.uuid4()}"
    logger.info(f"Initializing voice session: {session_id}")
    
    question_text, audio_base64 = await orchestrator.initialize_voice_session(
        session_id=session_id,
        difficulty=payload.difficulty,
        topic=payload.topic,
        style=payload.style
    )
    
    # Save the currently active question text in session cache.
    # We will need this to evaluate the user's upcoming answer.
    # To keep SessionState lightweight, we can just save it. Wait, the state doesn't have an 'active_question' field, 
    # but we can write one or just use session cache. Let's see: we can set a custom dynamic property on SessionState
    # or let's check what fields we have on SessionState:
    # We have mcq_answers, voice_evaluations, and we can just add a temporary field, or since it's a dynamic Python object
    # we can do `session.questions` or append a mock evaluation. Wait, let's look at SessionState fields:
    # questions is a List[MCQQuestion]. In python, we can set arbitrary dynamic properties on Pydantic models in memory,
    # or even better, we can put a simple mapping in memory, or since SessionState inherits from BaseModel, we can just
    # set `session.last_activity` or we can just append the question text to a list, or we can just add `active_question: str = ""` 
    # to SessionState! Adding a dedicated `active_question` field to SessionState makes it extremely clean, safe, and robust!
    
    # Let's read SessionState in session_manager.py. Yes! It has:
    # questions: List[MCQQuestion]
    # We can add `active_question: str = ""` to SessionState. Let's do that! That is much more elegant!
    
    # First, let's write the route.
    session = await session_manager.get_session(session_id)
    # We will update session_manager SessionState to include active_question shortly.
    setattr(session, "active_question", question_text)
    await session_manager.save_session(session_id, session)
    
    return VoiceQuestionResponse(
        session_id=session_id,
        question_id=str(uuid.uuid4()),
        question_text=question_text,
        audio_base64=audio_base64
    )

@router.get("/voice/summary/{session_id}", response_model=VoiceSessionSummary)
async def get_voice_summary(
    session_id: str,
    scoring_agent: ScoringAgent = Depends(get_scoring_agent)
):
    session = await session_manager.get_session(session_id)
    
    summary = scoring_agent.generate_session_summary(
        session_id=session_id,
        evaluations=session.voice_evaluations
    )
    
    return summary
