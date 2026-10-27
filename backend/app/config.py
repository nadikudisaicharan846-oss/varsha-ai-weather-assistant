from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _real(v: str) -> bool:
    return bool(v) and not v.startswith("your_")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Varsha AI"
    cors_origins: str = "http://localhost:5173"
    rate_limit_per_minute: int = 60
    default_city: str = "Hyderabad"

    weather_provider: str = "open-meteo"
    weather_api_key: str = ""
    allow_mock_fallback: bool = True
    cache_ttl_seconds: int = 600
    http_timeout_seconds: float = 15.0
    alert_thresholds_file: str = ""

    ai_provider: str = "none"
    ai_api_key: str = ""
    ai_model: str = ""
    ai_base_url: str = ""
    ai_timeout_seconds: float = 30.0

    voice_provider: str = "browser"
    voice_stt_model: str = "whisper-1"
    voice_tts_model: str = "tts-1"
    voice_tts_voice: str = "alloy"

    database_url: str = "sqlite:///./varsha.db"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ai_enabled(self) -> bool:
        return self.ai_provider in ("openai", "anthropic") and _real(self.ai_api_key)

    @property
    def db_url(self) -> str:
        return self.database_url if _real(self.database_url) else "sqlite:///./varsha.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
