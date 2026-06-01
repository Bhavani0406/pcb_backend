from typing import Dict, Any, List, Tuple, Optional
from app.agents.question_agent.question import QuestionAgent
from app.agents.validation_agent.validation import ValidationAgent
from app.agents.scoring_agent.scoring import ScoringAgent
from app.agents.speech_agent.speech import SpeechAgent
from app.services.session_manager import SessionState, session_manager
from app.schemas.mcq import MCQQuestion, MCQAnswerResponse
from app.schemas.voice import VoiceEvaluation, VoiceQuestionResponse
from app.core.logger.logging import logger

class OrchestratorAgent:
    def __init__(
        self,
        question_agent: QuestionAgent,
        validation_agent: ValidationAgent,
        scoring_agent: ScoringAgent,
        speech_agent: SpeechAgent
    ):
        self.question_agent = question_agent
        self.validation_agent = validation_agent
        self.scoring_agent = scoring_agent
        self.speech_agent = speech_agent

    async def initialize_mcq_session(
        self, 
        session_id: str, 
        difficulty: str, 
        topic: str, 
        style: str
    ) -> SessionState:
        logger.info(f"Orchestrator initializing MCQ session: {session_id}")
        
        # 1. Create stateless session
        session = await session_manager.create_session(
            session_id=session_id,
            session_type="mcq",
            difficulty=difficulty,
            topic=topic,
            style=style
        )
        
        # 2. Pre-generate question pool (minimum 20 questions)
        questions = await self.question_agent.generate_mcqs(
            difficulty=difficulty,
            topic=topic,
            style=style,
            count=20
        )
        
        session.questions = questions
        await session_manager.save_session(session_id, session)
        return session

    async def process_mcq_answer(
        self, 
        session_id: str, 
        question_id: str, 
        selected_option: str
    ) -> MCQAnswerResponse:
        logger.info(f"Orchestrator processing MCQ submission for session {session_id}")
        session = await session_manager.get_session(session_id)
        
        # Locate question in pool
        question = next((q for q in session.questions if q.id == question_id), None)
        if not question:
            raise ValueError(f"Question with ID {question_id} not found in this session.")

        is_correct = question.correct_answer.upper() == selected_option.upper()
        
        response = MCQAnswerResponse(
            question_id=question_id,
            selected_option=selected_option,
            correct_option=question.correct_answer,
            is_correct=is_correct,
            explanation=question.explanation,
            engineering_reasoning=question.engineering_reasoning
        )
        
        # Cache answer in session
        session.mcq_answers[question_id] = response
        await session_manager.save_session(session_id, session)
        return response

    async def initialize_voice_session(
        self,
        session_id: str,
        difficulty: str,
        topic: str,
        style: str
    ) -> Tuple[str, Optional[str]]:
        """
        Sets up the voice interview and generates the first question + audio.
        """
        logger.info(f"Orchestrator initializing Voice session: {session_id}")
        
        # 1. Create stateless session
        session = await session_manager.create_session(
            session_id=session_id,
            session_type="voice",
            difficulty=difficulty,
            topic=topic,
            style=style
        )
        
        # 2. Generate initial question
        first_question = await self.question_agent.generate_voice_question(
            difficulty=difficulty,
            topic=topic,
            style=style,
            history=[]
        )
        
        # Cache question text as pending first question
        # We model history as a list of dicts: {"question": str, "answer": str, "score": int}
        # To avoid duplicates, we save the active question in session state metadata or via logs.
        # We will utilize the last evaluation as a marker, or store the active question text directly.
        # We can dynamically pass the active question context.
        
        # 3. Text-to-Speech
        audio_base64 = self.speech_agent.text_to_speech_base64(first_question)
        
        return first_question, audio_base64

    async def submit_voice_answer(
        self,
        session_id: str,
        current_question: str,
        transcribed_answer: str
    ) -> Tuple[VoiceEvaluation, str, Optional[str]]:
        """
        Submits candidate's transcript, evaluates it, adjusts difficulty adaptively,
        and generates the next question + audio.
        """
        logger.info(f"Orchestrator processing voice answer submission for session: {session_id}")
        session = await session_manager.get_session(session_id)
        
        # 1. Validate and score answer
        evaluation = await self.validation_agent.validate_voice_answer(
            question=current_question,
            answer=transcribed_answer,
            topic=session.topic,
            difficulty=session.difficulty
        )
        
        # 2. Store evaluation in history
        session.voice_evaluations.append(evaluation)
        
        # 3. Adaptive difficulty logic:
        # Easy: weight 2-4, Medium: weight 5-7, Hard: weight 8-10.
        # If user scores >= 8, increase weight. If <= 5, decrease weight.
        prev_weight = session.active_difficulty_weight
        if evaluation.score >= 8:
            session.active_difficulty_weight = min(10, session.active_difficulty_weight + 1)
        elif evaluation.score <= 5:
            session.active_difficulty_weight = max(2, session.active_difficulty_weight - 1)
            
        logger.info(f"Adapted difficulty weight: {prev_weight} -> {session.active_difficulty_weight}")
        
        # Determine verbal difficulty level for the next question based on current weight
        next_difficulty = "easy"
        if session.active_difficulty_weight >= 8:
            next_difficulty = "hard"
        elif session.active_difficulty_weight >= 5:
            next_difficulty = "medium"
            
        # 4. Compile history format for LLM question prompt
        history_list = []
        for ev in session.voice_evaluations:
            history_list.append({
                "question": ev.question,
                "answer": ev.transcribed_answer,
                "score": ev.score
            })
            
        # 5. Generate next question
        next_question = await self.question_agent.generate_voice_question(
            difficulty=next_difficulty,
            topic=session.topic,
            style=session.style,
            history=history_list
        )
        
        # 6. Generate speech audio for next question
        next_audio_base64 = self.speech_agent.text_to_speech_base64(next_question)
        
        await session_manager.save_session(session_id, session)
        
        return evaluation, next_question, next_audio_base64
