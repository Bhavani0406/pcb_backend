import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import mcq, interview
from app.api.websocket import voice
from app.core.config.settings import settings
from app.core.exceptions.handler import global_exception_handler
from app.services.session_manager import session_cleanup_task
from app.core.logger.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("PCB Interview Platform Backend Starting Up")
    # Launch session cleanup in the background
    cleanup_task = asyncio.create_task(session_cleanup_task(interval_seconds=600))
    yield
    # Shutdown actions
    logger.info("PCB Interview Platform Backend Shutting Down")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="PCB & Hardware Engineering Interview AI Platform",
    description="Enterprise-Grade stateless real-time AI agents conducting professional hardware interviews.",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Enable CORS for React Dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Centralized Error Handler
app.add_exception_handler(Exception, global_exception_handler)

# Include Routers
app.include_router(mcq.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(voice.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Launching Uvicorn server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
