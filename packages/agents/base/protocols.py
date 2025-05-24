"""
Standardized protocols for MindMeld agent architecture.

This module defines the core interfaces that all agents must implement,
ensuring consistency across different agent implementations and enabling
interoperability between agent components.
"""

from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class AgentProtocol(Protocol):
    """Standardized protocol for all agent implementations.

    This protocol defines the core interface that all agents must implement,
    providing a consistent way to interact with different agent types.

    Implementations should handle:
    - Input validation and normalization
    - Processing logic specific to the agent's purpose
    - Structured output that follows a consistent schema
    - Error handling and reporting
    """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Primary interface for agent processing.

        Args:
            input_data: Dictionary containing parameters required by the agent.
                The exact schema depends on the agent implementation.

        Returns:
            Dictionary containing the agent's response with standardized structure.
            Should include at minimum:
            - success: Boolean indicating if processing was successful
            - message: Human-readable message about the result
            - data: Any output data produced by the agent

        Raises:
            ValueError: If input validation fails
            NotImplementedError: If the agent doesn't support the requested operation
        """

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data structure.

        Args:
            input_data: Dictionary containing parameters to validate.

        Returns:
            Boolean indicating if the input is valid.

        Raises:
            ValueError: With detailed explanation if validation fails.
        """

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and requirements.

        Provides metadata about what the agent can do and what inputs it expects.

        Returns:
            Dictionary containing:
            - name: Agent name
            - description: Human-readable description
            - version: Agent version
            - required_inputs: List of required input fields
            - optional_inputs: List of optional input fields with defaults
            - output_schema: Description of the output format
            - examples: Sample inputs and outputs
        """
