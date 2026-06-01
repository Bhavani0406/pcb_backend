from fastapi import Depends
from app.providers.factory import LLMProviderFactory
from app.providers.base.provider import BaseLLMProvider
from app.agents.question_agent.question import QuestionAgent
from app.agents.validation_agent.validation import ValidationAgent
from app.agents.feedback_agent.feedback import FeedbackAgent
from app.agents.scoring_agent.scoring import ScoringAgent
from app.agents.speech_agent.speech import SpeechAgent
from app.agents.orchestrator.orchestrator import OrchestratorAgent

def get_llm_provider() -> BaseLLMProvider:
    return LLMProviderFactory.get_provider()

def get_question_agent(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider)
) -> QuestionAgent:
    return QuestionAgent(llm_provider)

def get_validation_agent(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider)
) -> ValidationAgent:
    return ValidationAgent(llm_provider)

def get_feedback_agent() -> FeedbackAgent:
    return FeedbackAgent()

def get_scoring_agent(
    feedback_agent: FeedbackAgent = Depends(get_feedback_agent)
) -> ScoringAgent:
    return ScoringAgent(feedback_agent)

def get_speech_agent() -> SpeechAgent:
    return SpeechAgent()

def get_orchestrator(
    question_agent: QuestionAgent = Depends(get_question_agent),
    validation_agent: ValidationAgent = Depends(get_validation_agent),
    scoring_agent: ScoringAgent = Depends(get_scoring_agent),
    speech_agent: SpeechAgent = Depends(get_speech_agent)
) -> OrchestratorAgent:
    return OrchestratorAgent(
        question_agent=question_agent,
        validation_agent=validation_agent,
        scoring_agent=scoring_agent,
        speech_agent=speech_agent
    )
