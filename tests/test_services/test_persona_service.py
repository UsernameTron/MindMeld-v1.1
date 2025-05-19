import os

import pytest
from app.services.errors import ResourceNotFoundError
from app.services.persona.persona_service import PersonaService


@pytest.fixture
def tmp_persona_dir(tmp_path):
    persona_yaml = tmp_path / "cynical_humorist.yaml"
    persona_yaml.write_text(
        """
id: cynical-humorist
name: Cynical Humorist
archetype: Satirist
description: Test
tone_instructions: Test
system_prompt: Test
examples: []
"""
    )
    return str(tmp_path)


def test_load_and_get_persona(tmp_persona_dir):
    service = PersonaService(personas_dir=tmp_persona_dir)
    persona = service.get_persona("cynical-humorist")
    assert persona.name == "Cynical Humorist"
    assert service.get_all_personas().personas[0].id == "cynical-humorist"


def test_missing_persona_raises(tmp_persona_dir):
    service = PersonaService(personas_dir=tmp_persona_dir)
    with pytest.raises(ResourceNotFoundError):
        service.get_persona("not-found")


def test_malformed_persona_file(tmp_path):
    # Write an invalid YAML file
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text(
        """
id: bad
name: Bad Persona
archetype: Test
: this is not valid yaml
"""
    )
    # Should not raise, but should not load the persona
    service = PersonaService(personas_dir=str(tmp_path))
    with pytest.raises(ResourceNotFoundError):
        service.get_persona("bad")


def test_persona_examples_varied(tmp_path):
    # Write a persona with missing output in examples and include all required fields
    persona_yaml = tmp_path / "varied.yaml"
    persona_yaml.write_text(
        """
id: varied
name: Varied
archetype: Example
description: A test persona with varied examples
tone_instructions: Use a varied tone for examples
examples:
  - input: "A"
    output: "B"
  - input: "C"
"""
    )
    service = PersonaService(personas_dir=str(tmp_path))
    persona = service.get_persona("varied")
    assert persona.examples[0].input == "A"
    assert persona.examples[0].output == "B"
    assert persona.examples[1].input == "C"
    assert (
        persona.examples[1].output is None
    )  # Verify output is None for incomplete example


def test_persona_service_empty_dir(tmp_path):
    # Should not raise, just return empty list
    service = PersonaService(personas_dir=str(tmp_path))
    assert service.get_all_personas().personas == []


def test_persona_file_missing_required_fields(tmp_path):
    """Test that a persona file missing required fields is not loaded and raises ResourceNotFoundError."""
    persona_yaml = tmp_path / "incomplete.yaml"
    persona_yaml.write_text(
        """
id: incomplete
name: Incomplete
archetype: Example
"""
    )  # Missing description and tone_instructions
    service = PersonaService(personas_dir=str(tmp_path))
    with pytest.raises(ResourceNotFoundError):
        service.get_persona("incomplete")


@pytest.mark.asyncio
async def test_rewrite_invalid_persona_id():
    """Test that rewrite service raises OpenAIServiceError for invalid persona_id."""
    from app.models.rewrite.rewrite import RewriteRequest
    from app.services.errors import OpenAIServiceError
    from app.services.rewrite.rewrite_service import RewriteService

    service = RewriteService()
    request = RewriteRequest(content="Test", persona_id="does-not-exist")

    with pytest.raises(OpenAIServiceError):
        await service.rewrite_content(request)
