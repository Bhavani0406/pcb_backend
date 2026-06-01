from typing import List, Dict
from app.schemas.voice import VoiceEvaluation, VoiceSessionSummary
from app.agents.feedback_agent.feedback import FeedbackAgent
from app.core.logger.logging import logger

class ScoringAgent:
    def __init__(self, feedback_agent: FeedbackAgent):
        self.feedback_agent = feedback_agent

    def generate_session_summary(
        self, 
        session_id: str, 
        evaluations: List[VoiceEvaluation],
        topics_by_question_id: Dict[str, str] = None
    ) -> VoiceSessionSummary:
        logger.info(f"ScoringAgent is generating session summary for {session_id}")
        if not evaluations:
            return VoiceSessionSummary(
                session_id=session_id,
                total_questions=0,
                overall_score=0.0,
                technical_depth_avg=0.0,
                problem_solving_avg=0.0,
                communication_avg=0.0,
                practical_understanding_avg=0.0,
                topic_scores={},
                feedback_summary="No data compiled.",
                recommendations=["No questions answered."]
            )

        total_questions = len(evaluations)
        
        # Calculate metric sums
        score_sum = sum(ev.score for ev in evaluations)
        correctness_sum = sum(ev.technical_analysis.correctness for ev in evaluations)
        depth_sum = sum(ev.technical_analysis.technical_depth for ev in evaluations)
        problem_solving_sum = sum(ev.technical_analysis.problem_solving for ev in evaluations)
        communication_sum = sum(ev.technical_analysis.communication for ev in evaluations)
        practical_sum = sum(ev.technical_analysis.practical_understanding for ev in evaluations)

        # Topic wise scores
        topic_scores_sum: Dict[str, List[int]] = {}
        for ev in evaluations:
            # Try to associate a topic
            topic = "General"
            # In voice evaluation, we can infer topic from the question content or mapping
            if "impedance" in ev.question.lower() or "stripline" in ev.question.lower() or "microstrip" in ev.question.lower():
                topic = "Signal Integrity"
            elif "emi" in ev.question.lower() or "emc" in ev.question.lower() or "shield" in ev.question.lower():
                topic = "EMI / EMC Compliance"
            elif "buck" in ev.question.lower() or "converter" in ev.question.lower() or "power" in ev.question.lower():
                topic = "Power Electronics"
            elif "spi" in ev.question.lower() or "i2c" in ev.question.lower() or "mcu" in ev.question.lower() or "embedded" in ev.question.lower():
                topic = "Embedded Systems"
            
            if topic not in topic_scores_sum:
                topic_scores_sum[topic] = []
            topic_scores_sum[topic].append(ev.score)

        topic_scores: Dict[str, float] = {}
        for topic, scores in topic_scores_sum.items():
            topic_scores[topic] = round(sum(scores) / len(scores), 1)

        # Generate detailed feedback summary using FeedbackAgent
        feedback_report = self.feedback_agent.compile_voice_feedback_summary(evaluations)

        return VoiceSessionSummary(
            session_id=session_id,
            total_questions=total_questions,
            overall_score=round(score_sum / total_questions, 1),
            technical_depth_avg=round(depth_sum / total_questions, 1),
            problem_solving_avg=round(problem_solving_sum / total_questions, 1),
            communication_avg=round(communication_sum / total_questions, 1),
            practical_understanding_avg=round(practical_sum / total_questions, 1),
            topic_scores=topic_scores,
            feedback_summary=feedback_report["feedback_summary"],
            recommendations=feedback_report["recommendations"]
        )
