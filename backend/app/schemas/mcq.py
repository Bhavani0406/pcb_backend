from pydantic import BaseModel, Field
from typing import List, Optional

class MCQOption(BaseModel):
    id: str = Field(..., description="Option identifier e.g., A, B, C, D")
    text: str = Field(..., description="Option text content")

class MCQQuestion(BaseModel):
    id: str = Field(..., description="Unique question UUID")
    question: str = Field(..., description="Technical MCQ question stem")
    difficulty: str = Field(..., description="easy, medium, hard")
    topic: str = Field(..., description="High-level engineering topic")
    options: List[MCQOption] = Field(..., description="List of four options")
    correct_answer: str = Field(..., description="Correct option identifier, e.g. A")
    explanation: str = Field(..., description="Explanatory detail of correct answer")
    engineering_reasoning: str = Field(..., description="In-depth technical reasoning for design validation")
    difficulty_weight: int = Field(default=5, description="Difficulty weight from 1 to 10")
    tags: List[str] = Field(default_factory=list, description="Subtopics/tags")

class MCQSessionInit(BaseModel):
    difficulty: str = Field("medium", description="easy, medium, hard")
    topic: str = Field("General", description="Topic focus area")
    style: str = Field("General Panel", description="Interview style e.g., Nvidia, Qualcomm, TI")

class MCQSessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique in-memory session ID")
    questions: List[MCQQuestion] = Field(..., description="Pre-generated randomized pool of questions")

class MCQAnswerSubmit(BaseModel):
    session_id: str = Field(..., description="The active session ID")
    question_id: str = Field(..., description="ID of the question answered")
    selected_option: str = Field(..., description="Option selected by user (A, B, C, or D)")

class MCQAnswerResponse(BaseModel):
    question_id: str = Field(..., description="Question UUID")
    selected_option: str = Field(..., description="User selected option")
    correct_option: str = Field(..., description="Correct option ID")
    is_correct: bool = Field(..., description="True if selected matches correct")
    explanation: str = Field(..., description="Basic explanatory detail")
    engineering_reasoning: str = Field(..., description="Advanced electrical engineering design reasoning")

class MCQSessionSummary(BaseModel):
    session_id: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    analytics: dict = Field(..., description="Topic-wise strengths and weaknesses breakdown")
