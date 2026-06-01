from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class TechnicalAnalysis(BaseModel):
    correctness: int = Field(..., description="Technical correctness score (1-10)")
    technical_depth: int = Field(..., description="Understanding of underlying physics/theory (1-10)")
    problem_solving: int = Field(..., description="Debugging/troubleshooting capability (1-10)")
    communication: int = Field(..., description="Clarity and professionalism of engineering vocabulary (1-10)")
    practical_understanding: int = Field(..., description="Familiarity with industry standards, manufacturing and tools (1-10)")

class VoiceEvaluation(BaseModel):
    question: str = Field(..., description="The questions asked by the AI")
    transcribed_answer: str = Field(..., description="Transcribed audio answer")
    technical_analysis: TechnicalAnalysis = Field(..., description="Detailed technical breakdown ratings")
    strengths: List[str] = Field(..., description="Key areas where user's response was strong")
    weaknesses: List[str] = Field(..., description="Conceptual gaps or engineering oversights identified")
    ideal_answer: str = Field(..., description="The highly technical reference answer matching a Senior Engineer level")
    engineering_explanation: str = Field(..., description="Teachable explanation of the design concepts involved")
    feedback: str = Field(..., description="Constructive feedback for interview performance improvement")
    score: int = Field(..., description="Consolidated overall score (1-10)")
    confidence_score: int = Field(..., description="Percentage indicating candidate's vocal/logical confidence (1-100)")

class VoiceSessionInit(BaseModel):
    difficulty: str = Field("medium", description="easy, medium, hard")
    topic: str = Field("General Hardware Design", description="Core topic area")
    style: str = Field("General Panel", description="Intel, Qualcomm, Nvidia, TI, Automotive, Embedded")

class VoiceQuestionResponse(BaseModel):
    session_id: str
    question_id: str
    question_text: str
    audio_base64: Optional[str] = Field(None, description="Optional Base64 audio stream of the question")

class VoiceSessionSummary(BaseModel):
    session_id: str
    total_questions: int
    overall_score: float
    technical_depth_avg: float
    problem_solving_avg: float
    communication_avg: float
    practical_understanding_avg: float
    topic_scores: Dict[str, float] = Field(default_factory=dict)
    feedback_summary: str
    recommendations: List[str] = Field(default_factory=list)
