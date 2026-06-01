import time
import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.mcq import MCQQuestion, MCQAnswerResponse
from app.schemas.voice import VoiceEvaluation
from app.core.exceptions.handler import SessionNotFoundException
from app.core.logger.logging import logger

class SessionState(BaseModel):
    session_id: str
    session_type: str = Field(..., description="mcq | voice")
    difficulty: str = Field("medium", description="easy | medium | hard")
    topic: str
    style: str
    questions: List[MCQQuestion] = Field(default_factory=list)
    current_question_index: int = 0
    active_question: str = Field(default="", description="The active verbal question being asked")
    mcq_answers: Dict[str, MCQAnswerResponse] = Field(default_factory=dict)
    voice_evaluations: List[VoiceEvaluation] = Field(default_factory=list)
    active_difficulty_weight: int = 5
    last_activity: float = Field(default_factory=time.time)

    def touch(self):
        self.last_activity = time.time()

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}
        self._lock = asyncio.Lock()
        
    async def create_session(
        self, 
        session_id: str, 
        session_type: str, 
        difficulty: str, 
        topic: str, 
        style: str
    ) -> SessionState:
        async with self._lock:
            state = SessionState(
                session_id=session_id,
                session_type=session_type,
                difficulty=difficulty,
                topic=topic,
                style=style,
                active_difficulty_weight=5 if difficulty == "medium" else (3 if difficulty == "easy" else 8)
            )
            self._sessions[session_id] = state
            logger.info(f"Session {session_id} [{session_type}] created in-memory.")
            return state

    async def get_session(self, session_id: str) -> SessionState:
        async with self._lock:
            state = self._sessions.get(session_id)
            if not state:
                logger.warning(f"Attempted to access non-existent session: {session_id}")
                raise SessionNotFoundException(session_id)
            state.touch()
            return state

    async def save_session(self, session_id: str, state: SessionState) -> None:
        async with self._lock:
            state.touch()
            self._sessions[session_id] = state

    async def delete_session(self, session_id: str) -> None:
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"Session {session_id} deleted.")

    async def cleanup_expired_sessions(self, max_idle_seconds: int = 7200) -> int:
        """
        Cleans up idle sessions. Default is 2 hours.
        """
        async with self._lock:
            now = time.time()
            expired_ids = [
                sid for sid, s in self._sessions.items()
                if now - s.last_activity > max_idle_seconds
            ]
            for sid in expired_ids:
                del self._sessions[sid]
                logger.info(f"Auto-cleaned expired session {sid}")
            return len(expired_ids)

# Global singleton session manager
session_manager = SessionManager()

# Background task runner
async def session_cleanup_task(interval_seconds: int = 600):
    logger.info("Starting background session cleanup task")
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            cleaned = await session_manager.cleanup_expired_sessions()
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired sessions.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in session cleanup task: {str(e)}")
