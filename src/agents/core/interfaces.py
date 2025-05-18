from enum import Enum
from typing import Dict


class AgentInputType(Enum):
    TEXT = "text"
    CODE = "code"
    JSON = "json"
    # Add other types as needed


AGENT_INPUT_TYPES: Dict[str, AgentInputType] = {}
