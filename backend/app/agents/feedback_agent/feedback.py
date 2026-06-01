from typing import List, Dict, Any
from app.schemas.voice import VoiceEvaluation
from app.core.logger.logging import logger

class FeedbackAgent:
    def __init__(self):
        pass

    def compile_voice_feedback_summary(
        self, 
        evaluations: List[VoiceEvaluation]
    ) -> Dict[str, Any]:
        """
        Synthesizes the session history to construct an executive feedback summary.
        """
        logger.info("FeedbackAgent is compiling session feedback summary")
        if not evaluations:
            return {
                "feedback_summary": "No evaluation history available.",
                "recommendations": ["Complete at least one interview question to see insights."]
            }

        total_evals = len(evaluations)
        weaknesses_pool = []
        strengths_pool = []
        score_sum = 0

        for ev in evaluations:
            weaknesses_pool.extend(ev.weaknesses)
            strengths_pool.extend(ev.strengths)
            score_sum += ev.score

        avg_score = score_sum / total_evals
        
        # Select the most representative strengths/weaknesses (limit duplicates)
        unique_strengths = list(set(strengths_pool))[:3]
        unique_weaknesses = list(set(weaknesses_pool))[:3]

        # Generate actionable advice
        recommendations = []
        if avg_score < 6:
            recommendations.append("Invest time in reviewing basic circuit parameters: ESR in capacitors, saturation currents in power inductors, and loop inductances in high di/dt paths.")
            recommendations.append("Study the physical return current path at low frequencies (path of least resistance) vs. high frequencies (path of least inductance).")
        elif avg_score < 8:
            recommendations.append("Practice describing layout details using more precise terminology. Instead of 'noise reduction', refer to 'minimizing the common-mode radiated loop area'.")
            recommendations.append("Review IPC standards like IPC-2221 for track width and spacing guidelines and IPC-7351 for footprint specs.")
        else:
            recommendations.append("Excellent performance. To push your score even higher, investigate deep thermal simulation methodologies, high-density interconnect (HDI) blind/buried microvia aspect ratios, and gigabit-rate DDR5/PCIe Gen5 signal integrity challenges.")

        if unique_weaknesses:
            feedback_summary = (
                f"You demonstrated solid domain familiarity, averaging a technical rating of {avg_score:.1f}/10. "
                f"Your primary strengths included: {'; '.join(unique_strengths)}. "
                f"However, the panel noted some areas that need refinement, specifically: {'; '.join(unique_weaknesses)}."
            )
        else:
            feedback_summary = f"Exceptional interview performance with an overall rating of {avg_score:.1f}/10. You demonstrated masterful knowledge of circuit board design, electromagnetic compatibility, and layout practices."

        return {
            "feedback_summary": feedback_summary,
            "recommendations": recommendations
        }
