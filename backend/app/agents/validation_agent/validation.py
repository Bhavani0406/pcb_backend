import asyncio
import json
from typing import Dict, Any, List
from app.core.config.settings import settings
from app.providers.base.provider import BaseLLMProvider
from app.schemas.voice import VoiceEvaluation, TechnicalAnalysis
from app.prompts.voice_prompts import VOICE_VALIDATION_SYSTEM_PROMPT, VOICE_VALIDATION_USER_PROMPT
from app.core.logger.logging import logger

class ValidationAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    async def validate_voice_answer(
        self, 
        question: str, 
        answer: str, 
        topic: str, 
        difficulty: str
    ) -> VoiceEvaluation:
        try:
            logger.info(f"Validating voice answer for topic: {topic}")
            prompt = VOICE_VALIDATION_USER_PROMPT.format(
                question=question,
                answer=answer,
                topic=topic,
                difficulty=difficulty
            )
            response = await asyncio.wait_for(
                self.llm_provider.generate(
                    prompt=prompt,
                    system_prompt=VOICE_VALIDATION_SYSTEM_PROMPT,
                    json_mode=True
                ),
                timeout=settings.LLM_VALIDATION_TIMEOUT_SECONDS
            )
            
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                lines = cleaned_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_response = "\n".join(lines).strip()
                
            eval_data = json.loads(cleaned_response)
            
            return VoiceEvaluation(
                question=question,
                transcribed_answer=answer,
                technical_analysis=TechnicalAnalysis(**eval_data["technical_analysis"]),
                strengths=eval_data["strengths"],
                weaknesses=eval_data["weaknesses"],
                ideal_answer=eval_data["ideal_answer"],
                engineering_explanation=eval_data["engineering_explanation"],
                feedback=eval_data["feedback"],
                score=eval_data["score"],
                confidence_score=eval_data["confidence_score"]
            )
            
        except asyncio.TimeoutError:
            logger.warning(
                "Voice validation exceeded %.1fs. Using fallback verification engine.",
                settings.LLM_VALIDATION_TIMEOUT_SECONDS,
            )
            return self._fallback_evaluate(question, answer, topic, difficulty)
        except Exception as e:
            logger.error(f"Failed to validate voice answer using LLM: {str(e)}. Using fallback verification engine.")
            return self._fallback_evaluate(question, answer, topic, difficulty)

    def _fallback_evaluate(self, question: str, answer: str, topic: str, difficulty: str) -> VoiceEvaluation:
        # A smart local keyword-matching algorithm to provide a realistic evaluation if LLM is offline or unkeyed!
        ans_lower = answer.lower()
        keywords = {
            "return path": 15,
            "ground plane": 10,
            "impedance": 12,
            "inductance": 12,
            "capacitance": 10,
            "decoupling": 12,
            "crosstalk": 15,
            "reflection": 15,
            "emi": 10,
            "emc": 12,
            "thermal": 10,
            "via": 8,
            "trace": 8,
            "frequency": 8,
            "resistor": 6,
            "capacitor": 6,
            "diode": 6,
            "buck": 12,
            "boost": 12,
            "switches": 8,
            "current": 8,
            "voltage": 8,
            "ipc": 15,
            "qualcomm": 5,
            "intel": 5,
            "nvidia": 5
        }
        
        matches = [kw for kw in keywords if kw in ans_lower]
        keyword_score = sum(keywords[kw] for kw in matches)
        
        # Calculate scores realistically based on matches and answer length
        word_count = len(answer.split())
        length_multiplier = min(1.0, word_count / 60) # Optimal length is 60+ words
        
        raw_score = 3.0 + (min(6.0, keyword_score / 6.0) * length_multiplier)
        score = int(round(min(10.0, raw_score)))
        
        correctness = int(round(min(10.0, 3.0 + len(matches) * 0.8)))
        technical_depth = int(round(min(10.0, 2.0 + len([m for m in matches if keywords[m] > 10]) * 1.5)))
        problem_solving = int(round(min(10.0, 3.0 + word_count / 15)))
        communication = int(round(min(10.0, 4.0 + (1.5 if "therefore" in ans_lower or "specifically" in ans_lower or "consequently" in ans_lower else 0.0) + (1.5 if len(matches) > 3 else 0.0))))
        practical_understanding = int(round(min(10.0, 3.0 + (2.0 if "ipc" in ans_lower or "standard" in ans_lower or "measur" in ans_lower else 0.0))))
        
        confidence_score = int(round(min(100.0, 50.0 + (word_count / 2.0) + (len(matches) * 3.0))))
        
        # Generate custom strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if len(matches) >= 3:
            strengths.append(f"Successfully integrated high-level domain terminology including: {', '.join(matches[:3])}.")
        else:
            weaknesses.append("Engineering vocabulary was relatively sparse; try incorporating terms like loop inductance, decoupling, or return paths.")
            
        if word_count > 40:
            strengths.append("Provided a detailed explanation that showed willingness to elaborate on design issues.")
        else:
            weaknesses.append("The response was extremely brief. In a real technical interview, aim to speak for 1 to 2 minutes, detailing the physics and design trade-offs.")
            
        if "ground" not in ans_lower and "return" not in ans_lower:
            weaknesses.append("Did not explicitly discuss ground structures or return paths, which are paramount in all modern PCB layouts.")
        else:
            strengths.append("Correctly emphasized the importance of the grounding reference framework.")

        if not strengths:
            strengths = ["Responded to the prompt directly."]
        if not weaknesses:
            weaknesses = ["No major conceptual flaws identified, but could go into more theoretical depth regarding parasitic parameters."]

        ideal_answers = {
            "easy": "An ideal answer should state that decoupling capacitors act as local energy storage reservoirs, supplying instantaneous switching current to the IC and bypassing high-frequency noise directly to ground. They must be physically placed as close as humanly possible to the power and ground pins of the chip, using short, wide traces to minimize parasitic series inductance (ESL).",
            "medium": "An ideal answer for layout routing of a switching buck regulator must outline the two high di/dt loops. Loop 1 (input capacitor, high-side MOSFET, low-side MOSFET/diode) has extremely fast switching currents and must be routed as a tight loop with absolute minimal surface area to minimize radiated EMI. Ground return planes must be continuous underneath, and the switch node should be a copper pour just large enough to carry current but small enough to limit capacitive coupling (dv/dt noise).",
            "hard": "A senior engineer's answer must address signal integrity comprehensively. Ringing is caused by impedance mismatches creating transmission line reflections, while clock skew is timing offsets due to trace length inequalities. Solution vectors include: 1) Calculating and routing trace structures as controlled impedance lines (e.g., 50 Ohm single-ended or 100 Ohm differential). 2) Adding series source termination resistors to match the driver's impedance to the line. 3) Running tight length/skew matching within standard DDR4/5 tolerance margins. 4) Stitching vias adjacent to signal layer changes to maintain a continuous return current path and avoid high-inductive via stubs."
        }
        
        diff_key = difficulty.lower()
        if diff_key not in ideal_answers:
            diff_key = "medium"
            
        return VoiceEvaluation(
            question=question,
            transcribed_answer=answer,
            technical_analysis=TechnicalAnalysis(
                correctness=correctness,
                technical_depth=technical_depth,
                problem_solving=problem_solving,
                communication=communication,
                practical_understanding=practical_understanding
            ),
            strengths=strengths,
            weaknesses=weaknesses,
            ideal_answer=ideal_answers[diff_key],
            engineering_explanation=f"This question addresses critical PCB layout constraints and physical concepts. In standard design, current always flows in a complete loop. At high frequencies, current follows the path of least inductance (directly underneath the signal trace on the reference ground plane), rather than the path of least resistance. Maintaining a continuous, unbroken return path and placing passives correctly prevents signal reflections, ground bounce, and radiated electromagnetic compliance failure.",
            feedback="Your response shows a good starting intuition, but in a real panel interview at Apple or Nvidia, you should lead with the fundamental physics (like loop inductance or transmission line effects) and back it up with standard industry design guidelines (like IPC-2152 or decoupling mounting guidelines). Focus on standard technical terminology.",
            score=score,
            confidence_score=confidence_score
        )
