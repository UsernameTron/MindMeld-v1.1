import asyncio
import os
import tempfile
import uuid
from io import BytesIO

import httpx
from app.core.config import get_settings
from app.core.errors import ServiceError


async def generate_speech(text: str, voice: str = "nova", model: str = "tts-1", speed: float = 1.0) -> BytesIO:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "input": text,
                    "voice": voice,
                    "speed": speed,
                    "response_format": "mp3"
                }
            )
            if response.status_code != 200:
                raise ServiceError(f"OpenAI TTS API error: {response.text}")
            audio_data = BytesIO(response.content)
            audio_data.seek(0)
            return audio_data
    except Exception as e:
        raise ServiceError(f"TTS error: {str(e)}")

async def save_audio_file(audio_data: BytesIO) -> tuple[str, str]:
    settings = get_settings()
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.mp3"
    os.makedirs(settings.audio_storage_path, exist_ok=True)
    file_path = os.path.join(settings.audio_storage_path, file_name)
    with open(file_path, "wb") as f:
        f.write(audio_data.getvalue())
    base_url = settings.api_base_url.rstrip("/")
    return file_path, f"{base_url}/audio/{file_name}"
