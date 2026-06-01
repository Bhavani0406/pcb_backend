import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.session_manager import session_manager
from app.agents.orchestrator.orchestrator import OrchestratorAgent
from app.core.dependencies import get_orchestrator
from app.core.logger.logging import logger

router = APIRouter(prefix="/websocket", tags=["Voice WebSocket"])

# Dependency Helper for WebSocket since standard Depends doesn't automatically resolve agents directly in websocket routes easily without using FastAPI's routing
# We can resolve it by getting dependencies from a global/factory context, or invoking get_orchestrator manually inside the loop using standard FastAPI structure.
# Even simpler: we can just call the dependencies directly by instantiating the agents or calling the factory!
# Let's instantiate it in the route easily or use the factory to resolve the orchestrator directly!
# Yes! LLMProviderFactory makes it extremely easy to get the orchestrator directly without complex Dependency injection inside websockets.
# Let's write a quick inline resolver:
def get_websocket_orchestrator() -> OrchestratorAgent:
    from app.core.dependencies import get_llm_provider, get_question_agent, get_validation_agent, get_feedback_agent, get_scoring_agent, get_speech_agent
    llm = get_llm_provider()
    q_agent = get_question_agent(llm)
    v_agent = get_validation_agent(llm)
    f_agent = get_feedback_agent()
    score_agent = get_scoring_agent(f_agent)
    speech_agent = get_speech_agent()
    return OrchestratorAgent(q_agent, v_agent, score_agent, speech_agent)

@router.websocket("/voice/{session_id}")
async def websocket_voice_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")
    
    orchestrator = get_websocket_orchestrator()
    
    try:
        # Verify session exists
        session = await session_manager.get_session(session_id)
        logger.info(f"WebSocket session verified: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket session check failed: {str(e)}")
        await websocket.send_json({"error": "Session not found or expired."})
        await websocket.close()
        return

    try:
        while True:
            # Wait for message from candidate
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            event = data.get("event")
            logger.info(f"WebSocket received event: {event} for session: {session_id}")
            
            if event == "submit_answer":
                transcribed_text = data.get("transcribed_text", "").strip()
                
                # Retrieve active question from state
                session = await session_manager.get_session(session_id)
                current_question = getattr(session, "active_question", "")
                
                if not current_question:
                    # Fallback if somehow not set
                    current_question = "Please describe your experience with high speed board design."
                
                if not transcribed_text:
                    await websocket.send_json({
                        "event": "error",
                        "message": "Answer transcript cannot be empty."
                    })
                    continue
                
                # Notify client that evaluation is running (loading state)
                await websocket.send_json({
                    "event": "processing_started"
                })
                
                # Process answer, adjust difficulty, generate next question + audio
                evaluation, next_question, next_audio_base64 = await orchestrator.submit_voice_answer(
                    session_id=session_id,
                    current_question=current_question,
                    transcribed_answer=transcribed_text
                )
                
                # Save new active question in session cache
                session = await session_manager.get_session(session_id)
                setattr(session, "active_question", next_question)
                await session_manager.save_session(session_id, session)
                
                # Send evaluation and next question back
                await websocket.send_json({
                    "event": "evaluation_result",
                    "evaluation": evaluation.model_dump(),
                    "next_question": {
                        "question_text": next_question,
                        "audio_base64": next_audio_base64
                    }
                })
                
            elif event == "ping":
                await websocket.send_json({"event": "pong"})
                
            else:
                logger.warning(f"Unrecognized WebSocket event: {event}")
                await websocket.send_json({
                    "event": "error",
                    "message": f"Unrecognized event '{event}'"
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.exception(f"Unexpected error in WebSocket session {session_id}")
        try:
            await websocket.send_json({
                "event": "error",
                "message": f"An internal server error occurred: {str(e)}"
            })
        except Exception:
            pass
