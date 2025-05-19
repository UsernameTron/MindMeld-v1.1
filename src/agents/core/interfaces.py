from enum import Enum
from typing import Dict


class AgentInputType(Enum):
    """Enum defining the various input types an agent can accept.

    This helps specify what kind of data each agent expects to process.
    """

    TEXT = "text"
    CODE = "code"
    JSON = "json"
    # Add other types as needed


AGENT_INPUT_TYPES: Dict[str, AgentInputType] = {}
