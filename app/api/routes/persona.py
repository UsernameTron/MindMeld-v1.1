"""
Persona API routes module for the MindMeld backend.

This module defines FastAPI routes for persona management,
including listing available personas and retrieving persona details.
"""

from app.models.persona.persona import PersonaDefinition, PersonaListResponse
from app.services.errors import ResourceNotFoundError
from app.services.persona.persona_service import persona_service
from fastapi import APIRouter, HTTPException

router = APIRouter(
    tags=["personas"],
)


@router.get(
    "",
    response_model=PersonaListResponse,
    summary="List all available personas",
    description="Returns a list of all available content rewriting personas",
)
async def list_personas() -> PersonaListResponse:
    """
    List all available personas.

    Returns:
        PersonaListResponse containing all loaded personas
    """
    return persona_service.get_all_personas()


@router.get(
    "/{persona_id}",
    response_model=PersonaDefinition,
    summary="Get persona details",
    description="Returns details about a specific persona",
)
async def get_persona(persona_id: str) -> PersonaDefinition:
    """
    Get details about a specific persona.

    Args:
        persona_id: ID of the persona to retrieve

    Returns:
        PersonaDefinition for the requested persona

    Raises:
        HTTPException: If persona is not found (404)
    """
    try:
        return persona_service.get_persona(persona_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
