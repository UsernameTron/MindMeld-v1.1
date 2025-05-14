"""
Main application entry point for the MindMeld backend.

This module initializes the FastAPI application, configures middleware,
and registers API routes and exception handlers.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles

from app.api.routes import analyze, auth, persona, rewrite, data, tts, sentiment
from app.api.routes.chat import router as chat_router
from app.core.auth_middleware import APIKeyMiddleware
from app.core.errors import register_exception_handlers
from app.core.logging import get_logger
from app.core.middleware import RateLimitHeaderMiddleware, RequestIdMiddleware
from app.core.config import get_settings
from app.services.errors import ModelLoadError

import os

# Get the logger
log = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifecycle context manager for application startup and shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Indicates the application is running.
    """
    log.info("Application starting up")
    yield
    log.info("Application shutting down")


app = FastAPI(
    title="MindMeld Modular LLM Backend",
    version="0.1.0",
    description="Extensible LLM API backend",
    lifespan=lifespan,
)
app.router.redirect_slashes = True  # Allow both /route and /route/

# Add middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RateLimitHeaderMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Get settings
settings = get_settings()

# Create audio directory if it doesn't exist
os.makedirs(settings.audio_storage_path, exist_ok=True)

# Mount the audio directory to serve files
app.mount("/audio", StaticFiles(directory=settings.audio_storage_path), name="audio")

# Create versioned API router
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(analyze.router, prefix="/analyze", tags=["Analyze"])
v1_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
v1_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])

# Include versioned router in main app
app.include_router(v1_router)

# Optionally, keep original routes for backward compatibility
app.include_router(analyze.router, prefix="/analyze", tags=["Analyze-Legacy"])
app.include_router(chat_router, prefix="/chat", tags=["Chat-Legacy"])

# Include routers
app.include_router(persona.router, prefix="/personas")
app.include_router(rewrite.router, prefix="/rewrite")
app.include_router(auth.router, prefix="/auth")
app.include_router(data.data_router, prefix="/data", tags=["Data"])
app.include_router(tts.router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify application status.

    Returns:
        dict[str, str]: A dictionary indicating the application is healthy.
    """
    log.debug("Health check endpoint called")
    return {"status": "healthy"}


@app.get("/test/model-load-error")
async def test_model_load_error() -> None:
    """
    Test endpoint to simulate a model load error.

    Raises:
        ModelLoadError: Simulated model load error for testing purposes.
    """
    raise ModelLoadError("test-model", details={"model_name": "test-model"})
