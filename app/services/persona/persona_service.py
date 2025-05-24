import json
import logging
import os
from typing import Dict

import yaml

from app.models.persona.persona import PersonaDefinition, PersonaListResponse
from app.services.errors import ResourceNotFoundError

logger = logging.getLogger(__name__)


class PersonaService:
    """Service for managing content personas."""

    def __init__(self, personas_dir: str = "prompts/personas"):
        self.personas_dir = personas_dir
        self.personas_cache: Dict[str, PersonaDefinition] = {}
        self._load_personas()

    def _load_personas(self) -> None:
        if not os.path.exists(self.personas_dir):
            logger.warning(f"Personas directory not found: {self.personas_dir}")
            os.makedirs(self.personas_dir, exist_ok=True)
            return
        for filename in os.listdir(self.personas_dir):
            if filename.endswith((".yaml", ".yml", ".json")):
                filepath = os.path.join(self.personas_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        if filename.endswith((".yaml", ".yml")):
                            persona_data = yaml.safe_load(f)
                        else:
                            persona_data = json.load(f)
                    persona = PersonaDefinition(**persona_data)
                    self.personas_cache[persona.id] = persona
                    logger.info(f"Loaded persona: {persona.id} from {filepath}")
                except Exception as e:
                    logger.error(f"Error loading persona from {filepath}: {str(e)}")

    def get_all_personas(self) -> PersonaListResponse:
        return PersonaListResponse(personas=list(self.personas_cache.values()))

    def get_persona(self, persona_id: str) -> PersonaDefinition:
        if persona_id not in self.personas_cache:
            raise ResourceNotFoundError(f"Persona not found: {persona_id}")
        return self.personas_cache[persona_id]


# Create service instance
persona_service = PersonaService()
