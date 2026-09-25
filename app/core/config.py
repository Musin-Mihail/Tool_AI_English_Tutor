from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.paths import PROJECT_ROOT


class Settings(BaseSettings):
    PROJECT_NAME: str = "English Tutor AI"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:4200"]

    CURSOR_API_KEY: Optional[str] = None
    CURSOR_MODEL: str = "composer-2.5"

    # Optional: Hugging Face Hub (higher rate limits for model downloads)
    HF_TOKEN: Optional[str] = None

    WHISPER_MODEL: str = "large-v3"
    ASR_DEVICE: str = "auto"
    ASR_COMPUTE_TYPE: str = "auto"
    # Локальный каталог для весов Whisper (None → app/data/whisper_models)
    ASR_DOWNLOAD_ROOT: Optional[str] = None
    ASR_PRELOAD: bool = True
    ASR_BEAM_SIZE: int = 1
    ASR_CONDITION_ON_PREVIOUS_TEXT: bool = False
    ASR_LOW_CONFIDENCE: float = 0.45

    ACOUSTIC_ASR: bool = True
    ACOUSTIC_ASR_MODEL: str = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
    ACOUSTIC_ASR_DEVICE: str = "auto"

    TTS_ENABLED: bool = True
    TTS_VOICE: str = "af_heart"
    TTS_PRELOAD: bool = True
    TTS_SPEED: float = 1.0

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_provider_keys(self) -> "Settings":
        if not self.CURSOR_API_KEY:
            raise ValueError(
                "CURSOR_API_KEY is required. "
                "Dashboard → API & SSH Keys → Add: https://cursor.com/dashboard"
            )
        return self


settings = Settings()
