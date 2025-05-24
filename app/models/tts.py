from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., description="The text to convert to speech")
    voice: str = Field("nova", description="Voice to use for TTS")
    model: str = Field("tts-1", description="TTS model to use")
    speed: float = Field(1.0, description="Speech speed multiplier", ge=0.25, le=4.0)


class TTSResponse(BaseModel):
    audio_url: str = Field(..., description="URL to the generated audio file")
    duration: float = Field(..., description="Duration of the audio in seconds")
    character_count: int = Field(
        ..., description="Number of characters in the original text"
    )
