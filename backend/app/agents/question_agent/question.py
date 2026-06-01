import asyncio
import json
import random
import uuid
from typing import List, Optional
from app.core.config.settings import settings
from app.providers.base.provider import BaseLLMProvider
from app.schemas.mcq import MCQQuestion, MCQOption
from app.prompts.mcq_prompts import MCQ_GENERATION_SYSTEM_PROMPT, MCQ_GENERATION_USER_PROMPT
from app.prompts.voice_prompts import VOICE_QUESTION_SYSTEM_PROMPT, VOICE_QUESTION_USER_PROMPT
from app.core.logger.logging import logger

class QuestionAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider
        self._random = random.SystemRandom()

    def _shuffle_options(
        self,
        options: List[MCQOption],
        correct_answer: str,
        target_correct_id: str,
    ) -> tuple[List[MCQOption], str]:
        correct_option = next(
            (option for option in options if option.id.upper() == correct_answer.upper()),
            options[0],
        )
        option_ids = ["A", "B", "C", "D"]
        wrong_options = [option for option in options if option.text != correct_option.text]
        self._random.shuffle(wrong_options)

        normalized_options: list[MCQOption] = []
        wrong_index = 0
        for option_id in option_ids:
            if option_id == target_correct_id:
                normalized_options.append(MCQOption(id=option_id, text=correct_option.text))
            else:
                normalized_options.append(MCQOption(id=option_id, text=wrong_options[wrong_index].text))
                wrong_index += 1
        return normalized_options, target_correct_id

    def _target_correct_id(self, index: int) -> str:
        option_ids = ["A", "B", "C", "D"]
        return option_ids[index % len(option_ids)]

    async def generate_mcqs(
        self, 
        difficulty: str, 
        topic: str, 
        style: str, 
        count: int = 20
    ) -> List[MCQQuestion]:
        try:
            logger.info(f"Generating {count} MCQs via LLM. Topic: {topic}, Difficulty: {difficulty}")
            prompt = MCQ_GENERATION_USER_PROMPT.format(
                count=count,
                difficulty=difficulty,
                topic=topic,
                style=style
            )
            response = await asyncio.wait_for(
                self.llm_provider.generate(
                    prompt=prompt,
                    system_prompt=MCQ_GENERATION_SYSTEM_PROMPT,
                    json_mode=True
                ),
                timeout=settings.LLM_TIMEOUT_SECONDS
            )
            
            # Clean response from any markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # strip out the ```json and ``` wrapping
                lines = cleaned_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_response = "\n".join(lines).strip()
            
            questions_data = json.loads(cleaned_response)
            questions = []
            
            for item in questions_data:
                # Ensure each question has a valid UUID
                question_id = str(uuid.uuid4())
                options = [MCQOption(**opt) for opt in item["options"]]
                shuffled_options, correct_answer = self._shuffle_options(
                    options,
                    item["correct_answer"],
                    self._target_correct_id(len(questions)),
                )
                
                questions.append(
                    MCQQuestion(
                        id=question_id,
                        question=item["question"],
                        difficulty=item["difficulty"],
                        topic=item["topic"],
                        options=shuffled_options,
                        correct_answer=correct_answer,
                        explanation=item["explanation"],
                        engineering_reasoning=item["engineering_reasoning"],
                        difficulty_weight=item.get("difficulty_weight", 5),
                        tags=item.get("tags", [])
                    )
                )
            
            if len(questions) < 1:
                raise ValueError("LLM returned an empty list of questions")
                
            return questions[:count]
            
        except asyncio.TimeoutError:
            logger.warning(
                "MCQ generation exceeded %.1fs. Using local question pool for fast startup.",
                settings.LLM_TIMEOUT_SECONDS,
            )
            return self._get_fallback_mcqs(difficulty, topic, count)
        except Exception as e:
            logger.error(f"Failed to generate MCQs using LLM: {str(e)}. Utilizing high-fidelity local fallback pool.")
            return self._get_fallback_mcqs(difficulty, topic, count)

    async def generate_voice_question(
        self, 
        difficulty: str, 
        topic: str, 
        style: str, 
        history: List[dict]
    ) -> str:
        try:
            logger.info(f"Generating voice question. Topic: {topic}, Difficulty: {difficulty}")
            history_str = ""
            for h in history:
                history_str += f"Q: {h.get('question')}\nA: {h.get('answer')}\nScore: {h.get('score')}/10\n"
            
            prompt = VOICE_QUESTION_USER_PROMPT.format(
                topic=topic,
                difficulty=difficulty,
                style=style,
                history=history_str if history_str else "No history yet. Start the interview."
            )
            response = await asyncio.wait_for(
                self.llm_provider.generate(
                    prompt=prompt,
                    system_prompt=VOICE_QUESTION_SYSTEM_PROMPT,
                    json_mode=False
                ),
                timeout=settings.LLM_VOICE_TIMEOUT_SECONDS
            )
            return response.strip()
        except asyncio.TimeoutError:
            logger.warning(
                "Voice question generation exceeded %.1fs. Using fallback voice question.",
                settings.LLM_VOICE_TIMEOUT_SECONDS,
            )
            return self._get_fallback_voice_question(difficulty, topic, len(history))
        except Exception as e:
            logger.error(f"Failed to generate voice question using LLM: {str(e)}. Using fallback voice question.")
            return self._get_fallback_voice_question(difficulty, topic, len(history))

    def _get_fallback_mcqs(self, difficulty: str, topic: str, count: int) -> List[MCQQuestion]:
        # High fidelity pre-designed technical questions for PCB design & Hardware
        pool = [
            MCQQuestion(
                id="fb-q1",
                question="Why is a controlled impedance of 50 Ohms typically preferred for single-ended transmission lines in RF and high-speed digital board design?",
                difficulty="medium",
                topic="Advanced PCB Design",
                options=[
                    {"id": "A", "text": "It represents the exact geometric mean of standard coaxial cable impedance (75 Ohm) and wave impedance of free space (377 Ohm)."},
                    {"id": "B", "text": "It provides an optimal balance between maximum power handling capability (which occurs at 30 Ohms) and minimum signal attenuation (which occurs at 77 Ohms)."},
                    {"id": "C", "text": "It matches the natural input impedance of all silicon-based CMOS gates, preventing the need for series terminators."},
                    {"id": "D", "text": "FR4 substrates are physically incapable of supporting trace geometries with impedances higher than 60 Ohms."}
                ],
                correct_answer="B",
                explanation="50 Ohms is the industry standard balance point between low loss (77 Ohms) and high power (30 Ohms) for RF coax and trace geometry.",
                engineering_reasoning="Historically, RF engineers determined that for air-dielectric coaxial cables, minimum loss is achieved at approximately 77 Ohms, while maximum power transmission is achieved at approximately 30 Ohms. 50 Ohms is the geometric compromise. For modern PCB manufacturing, a 50 Ohm microstrip on standard FR-4 dielectric results in trace widths that are easy to manufacture (typically 5 to 10 mils) while maintaining a reasonable thickness.",
                difficulty_weight=6,
                tags=["RF", "Impedance", "High-speed"]
            ),
            MCQQuestion(
                id="fb-q2",
                question="What is the primary physical mechanism behind 'Ground Bounce' in high-speed digital integrated circuits?",
                difficulty="hard",
                topic="Advanced PCB Design",
                options=[
                    {"id": "A", "text": "Excessive capacitive coupling between adjacent signal lines and the ground plane."},
                    {"id": "B", "text": "The finite DC resistance of the ground plane causing static IR drops during logic state transitions."},
                    {"id": "C", "text": "Transient current flowing through the parasitic inductance of the IC package lead frame and bond wires (V = L * di/dt)."},
                    {"id": "D", "text": "Dielectric breakdown of the FR4 prepreg under high clock frequency resonance."}
                ],
                correct_answer="C",
                explanation="Ground bounce is caused by fast transient currents (di/dt) flowing through the parasitic lead frame/bond wire inductance (L) of the chip ground connection.",
                engineering_reasoning="Ground bounce is a transient voltage fluctuation at the local ground of the silicon die relative to the system PCB board ground. When multiple digital outputs switch simultaneously from High to Low, they discharge charge-storage nodes. The sudden surge of current flowing through the package ground pin's parasitic inductance (L) creates a voltage drop given by V = L * (di/dt). This shifts the internal ground reference, potentially triggering false logic switches on quiet pins.",
                difficulty_weight=8,
                tags=["Signal Integrity", "Ground Bounce", "Parasitics"]
            ),
            MCQQuestion(
                id="fb-q3",
                question="When routing a differential pair on a high-speed PCB, why is tight coupling between the two traces generally recommended?",
                difficulty="hard",
                topic="Advanced PCB Design",
                options=[
                    {"id": "A", "text": "Tight coupling maximizes the common-mode noise impedance, completely eliminating the need for terminal resistors."},
                    {"id": "B", "text": "It ensures that return currents do not flow through the reference ground plane, allowing routing over split planes."},
                    {"id": "C", "text": "It keeps the differential impedance exactly constant and increases susceptibility to ambient EMI."},
                    {"id": "D", "text": "It ensures that external noise couples equally to both traces as common-mode, allowing the receiver's differential amplifier to reject it."}
                ],
                correct_answer="D",
                explanation="Tight coupling ensures that environmental noise affects both traces equally, maximizing the common-mode rejection ratio (CMRR) at the receiver.",
                engineering_reasoning="Differential pairs function by measuring the voltage difference between two complementary lines. If external EMI or crosstalk from an adjacent signal couples into the differential pair, tight physical proximity ensures that both lines receive identical noise voltages. The receiver's differential receiver computes V+ minus V-, thereby canceling the common-mode noise. Tight coupling also reduces the radiated loop area, which reduces electromagnetic emissions.",
                difficulty_weight=9,
                tags=["Signal Integrity", "Differential Pairs", "EMI/EMC"]
            ),
            MCQQuestion(
                id="fb-q4",
                question="In power electronics, what is the primary purpose of a snubber circuit across a MOSFET in a Buck converter?",
                difficulty="medium",
                topic="Power Electronics",
                options=[
                    {"id": "A", "text": "To increase the gate drive current and accelerate the turn-on transitions."},
                    {"id": "B", "text": "To absorb high-frequency voltage spikes and damp resonant ringing caused by parasitic inductances and output capacitance during switching transitions."},
                    {"id": "C", "text": "To act as an auxiliary DC-DC booster to supply the gate driver circuitry."},
                    {"id": "D", "text": "To regulate the output voltage directly during light load conditions."}
                ],
                correct_answer="B",
                explanation="A snubber circuit (typically RC or RCD) absorbs high-voltage ringing spikes generated by parasitic inductance and capacitance during switching transitions.",
                engineering_reasoning="During the turn-off phase of the power MOSFET, the rapid change in current (di/dt) interacts with parasitic circuit inductances (trace inductance, package pins) and the MOSFET's junction capacitance (Coss). This creates a high-frequency resonant LC tank, resulting in severe voltage spikes that can exceed the MOSFET's drain-source breakdown voltage (Vdss) and radiate high-frequency EMI. An RC snubber dissipates this resonant energy as heat, protecting the transistor and reducing noise.",
                difficulty_weight=7,
                tags=["Power Electronics", "Buck Converter", "EMI/EMC"]
            ),
            MCQQuestion(
                id="fb-q5",
                question="Which IPC standard provides the definitive guidelines for rigid printed board design, outlining trace width calculations, current capacity, and clearance requirements?",
                difficulty="easy",
                topic="Industry Standards",
                options=[
                    {"id": "A", "text": "IPC-A-610"},
                    {"id": "B", "text": "IPC-7351"},
                    {"id": "C", "text": "IPC-2221"},
                    {"id": "D", "text": "IPC-6012"}
                ],
                correct_answer="C",
                explanation="IPC-2221 is the generic standard for printed board design, covering electrical clearance, current capacity vs. trace thickness, and layer properties.",
                engineering_reasoning="IPC-2221 ('Generic Standard on Printed Board Design') contains the fundamental design criteria for PCB layouts, including the famous charts relating trace cross-sectional area, current flow, and temperature rise (which are now updated in IPC-2152). IPC-A-610 covers board acceptability, IPC-7351 is for SMD footprint land patterns, and IPC-6012 covers qualification and performance specs for rigid boards.",
                difficulty_weight=4,
                tags=["Standards", "Safety"]
            )
        ]
        
        # Filter by difficulty if needed, and duplicate to match count if necessary
        results = [q for q in pool if q.difficulty == difficulty or q.difficulty == "medium"]
        if not results:
            results = pool
            
        # Ensure we return the requested count by recycling
        final_questions = []
        for i in range(count):
            q_template = results[i % len(results)]
            shuffled_options, correct_answer = self._shuffle_options(
                q_template.options,
                q_template.correct_answer,
                self._target_correct_id(i),
            )
            # Clone with a new UUID to prevent duplicates
            new_q = MCQQuestion(
                id=f"fb-q-{i}-{uuid.uuid4().hex[:6]}",
                question=q_template.question,
                difficulty=q_template.difficulty,
                topic=q_template.topic,
                options=shuffled_options,
                correct_answer=correct_answer,
                explanation=q_template.explanation,
                engineering_reasoning=q_template.engineering_reasoning,
                difficulty_weight=q_template.difficulty_weight,
                tags=q_template.tags
            )
            final_questions.append(new_q)
            
        return final_questions

    def _get_fallback_voice_question(self, difficulty: str, topic: str, index: int) -> str:
        easy_questions = [
            "Could you explain the primary differences between active and passive electronic components and give three common examples of each?",
            "What is the function of a bypass or decoupling capacitor on a PCB, and how should it be physically placed relative to the IC pin it is protecting?",
            "Can you explain Ohm's Law and describe how you would calculate the trace resistance of a simple copper trace if you know its length, width, and copper weight?"
        ]
        medium_questions = [
            "Describe your typical layout strategy for a DC-DC Buck converter. What are the critical current loops, and how do you arrange the switch, inductor, diode, and capacitors to minimize EMI?",
            "Explain the difference between SPI and I2C buses. What are their pin configurations, speed capabilities, and why are pull-up resistors required on an I2C bus?",
            "How do you determine the trace width for a high-current power rail on a 4-layer PCB? What standards do you consult, and what thermal trade-offs must you consider?"
        ]
        hard_questions = [
            "We are experiencing signal integrity failures on a DDR4 routing interface with significant ringing and clock skew. How would you diagnose these issues, and what structural layout changes (such as length matching, terminations, and via stubs) would you recommend?",
            "Explain the concept of controlled differential impedance. If we need to route a 100-Ohm PCIe differential pair, what geometric factors in the trace stackup affect this impedance, and how does the return path geometry play a role?",
            "How do you design a Power Distribution Network (PDN) to achieve a low target impedance across a wide frequency range (from DC up to several GHz)? How do decoupling capacitor values, mounting inductances, and plane-to-plane capacitances fit into this impedance curve?"
        ]
        
        pool = medium_questions
        if difficulty == "easy":
            pool = easy_questions
        elif difficulty == "hard":
            pool = hard_questions
            
        return pool[index % len(pool)]
