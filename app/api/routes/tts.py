from fastapi import APIRouter, Depends, HTTPException
from app.core.auth_middleware import require_auth
from app.models.tts import TTSRequest, TTSResponse
from app.models.common import ErrorResponse
from app.services.tts.tts_service import generate_speech, save_audio_file
from mutagen.mp3 import MP3

router = APIRouter(prefix="/tts", tags=["text-to-speech"])

@router.post("", response_model=TTSResponse, responses={401: {"model": ErrorResponse}})
async def text_to_speech(request: TTSRequest, auth_data=Depends(require_auth)):
    try:
        audio_data = await generate_speech(
            text=request.text,
            voice=request.voice,
            model=request.model,
            speed=request.speed
        )
        file_path, audio_url = await save_audio_file(audio_data)
        duration = MP3(file_path).info.length
        return TTSResponse(audio_url=audio_url, duration=duration, character_count=len(request.text))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
