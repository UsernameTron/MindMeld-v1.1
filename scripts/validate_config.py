import os

from app.core.config import settings


def validate_config():
    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "DEFAULT_MODEL_NAME",
        "HUGGINGFACE_KEY",
        "REDIS_URL",
    ]
    missing = [var for var in required_vars if not getattr(settings, var, None)]
    if missing:
        print(f"❌ Missing required config: {missing}")
    else:
        print("✅ All required config present")
    # Check tier configuration
    if not hasattr(settings, "TIERS") or not settings.TIERS:
        print("⚠️ No tier configuration found")


if __name__ == "__main__":
    validate_config()
