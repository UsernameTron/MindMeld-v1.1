from fastapi import APIRouter, HTTPException

from app.models.chat.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat.chat_service import chat_service
from app.services.errors import OpenAIServiceError

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.get("/health")
async def chat_health():
    """Test endpoint to verify chat router is working"""
    return {"status": "chat router healthy"}


@router.post(
    "/completion",
    response_model=ChatCompletionResponse,
    summary="Generate a chat completion",
    description="Send a conversation to OpenAI and get a response from the model",
)
async def create_chat_completion(
    request: ChatCompletionRequest,
) -> ChatCompletionResponse:
    try:
        response = await chat_service.generate_completion(request)
        return response
    except OpenAIServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
