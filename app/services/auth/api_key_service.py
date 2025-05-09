import secrets
import time
from typing import Dict, List, Optional

from pydantic import BaseModel

# In production, use a database for API keys
api_keys_db: Dict[str, Dict] = {}


def generate_api_key() -> str:
    """Generate a new API key."""
    return secrets.token_urlsafe(32)


def create_api_key(client_id: str, scopes: List[str]) -> str:
    """Create API key for a client with scopes."""
    api_key = generate_api_key()
    api_keys_db[api_key] = {
        "client_id": client_id,
        "scopes": scopes,
        "created_at": time.time(),
    }
    return api_key


def validate_api_key(key: str, required_scope: Optional[str] = None) -> bool:
    """Check if API key is valid and has required scope."""
    entry = api_keys_db.get(key)
    if not entry or (required_scope and required_scope not in entry["scopes"]):
        return False
    return True


def get_api_key_info(api_key: str) -> Optional[Dict]:
    """Get information about an API key."""
    return api_keys_db.get(api_key)


def revoke_api_key(api_key: str) -> bool:
    """Revoke an API key."""
    if api_key in api_keys_db:
        del api_keys_db[api_key]
        return True
    return False
