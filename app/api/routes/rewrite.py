"""
Rewrite API routes module for the MindMeld backend.

This module defines FastAPI routes for content rewriting,
providing endpoints to transform content using personas.
"""

from app.models.rewrite.rewrite import RewriteRequest, RewriteResponse
from app.services.errors import OpenAIServiceError, ResourceNotFoundError
from app.services.rewrite.rewrite_service import rewrite_service
from fastapi import APIRouter, HTTPException

router = APIRouter(
    tags=["rewrite"],
)


@router.post(
    "",
    response_model=RewriteResponse,
    summary="Rewrite content using a persona",
    description="Transforms input content using the selected persona's tone and style",
)
async def rewrite_content(request: RewriteRequest) -> RewriteResponse:
    """
    Rewrite content using a persona.

    Takes input content and transforms it according to the
    specified persona's tone, style, and characteristics.

    Args:
        request: RewriteRequest containing content and persona ID

    Returns:
        RewriteResponse with original and transformed content

    Raises:
        HTTPException: If persona is not found (404) or if there's an API error (500)
    """
    try:
        return await rewrite_service.rewrite_content(request)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OpenAIServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
