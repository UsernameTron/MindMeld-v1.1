"""
API routes for chat completion endpoints in the MindMeld backend.

This module defines the FastAPI routes for chat-based interactions
and completions using LLMs.
"""

from app.core.middleware import RateLimiter
from app.models.chat.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat.chat_service import chat_service
from app.services.errors import OpenAIServiceError
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter(
    # Remove prefix here; it will be set in main.py
    tags=["chat"],
)


@router.get("/health")
async def chat_health() -> dict[str, str]:
    """
    Test endpoint to verify chat router is working.

    Returns:
        dict: A status message indicating the health of the chat router.
    """
    return {"status": "chat router healthy"}


def require_chat_auth(request: Request):
    from app.core.config import settings
    from app.services.auth.api_key_service import validate_api_key
    from app.services.auth.auth_service import (
        ALGORITHM,
        SECRET_KEY,
        fake_users_db,
        get_user,
        jwt,
    )

    if not settings.AUTH_ENABLED:
        return
    api_key = request.headers.get("X-API-Key")
    auth_header = request.headers.get("Authorization")
    required_scope = "chat"

    def validate_token(token):
        if api_key:
            if not validate_api_key(token, required_scope):
                raise HTTPException(
                    status_code=403, detail="Invalid or insufficient API key scope"
                )
            return
        # now handle JWT separately for proper 401 vs. 403
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            # bad signature, malformed, expired, etc.
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        # at this point the token was valid—now check scope
        username = payload.get("sub")
        scopes = payload.get("scopes", [])
        if required_scope not in scopes:
            # valid identity but missing permission
            raise HTTPException(status_code=403, detail="JWT missing required scope")
        user = get_user(fake_users_db, username)
        if not user:
            # token was valid but user lookup failed
            raise HTTPException(status_code=401, detail="User not found")

    token = api_key or (
        auth_header.split(" ", 1)[1]
        if auth_header and auth_header.startswith("Bearer ")
        else None
    )
    if not token:
        raise HTTPException(
            status_code=401, detail="Missing authentication credentials"
        )
    # Sanity check: always raise 403 if validate_api_key returns False
    if api_key and not validate_api_key(api_key, required_scope):
        raise HTTPException(
            status_code=403, detail="Invalid or insufficient API key scope"
        )
    validate_token(token)


@router.post(
    "",
    response_model=ChatCompletionResponse,
)
async def chat(
    request: ChatCompletionRequest,
    _auth: None = Depends(require_chat_auth),
    _rl: None = Depends(RateLimiter(requests=5, window=60)),
) -> ChatCompletionResponse:
    return await chat_service.generate_completion(request)


@router.post(
    "/completion/",
    response_model=ChatCompletionResponse,
)
async def chat_completion(
    request: ChatCompletionRequest,
    _auth: None = Depends(require_chat_auth),
    _rl: None = Depends(RateLimiter(requests=5, window=60)),
) -> ChatCompletionResponse:
    return await chat_service.generate_completion(request)
