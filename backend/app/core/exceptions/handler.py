from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logger.logging import logger

class PCBInterviewException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class SessionNotFoundException(PCBInterviewException):
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session with ID {session_id} not found or expired.",
            code="SESSION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

class LLMProviderException(PCBInterviewException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="LLM_PROVIDER_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY
        )

class AudioProcessingException(PCBInterviewException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="AUDIO_PROCESSING_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, PCBInterviewException):
        logger.error(f"PCBInterviewException: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}}
        )
    
    logger.exception(f"Unhandled server error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred on the server."}}
    )
