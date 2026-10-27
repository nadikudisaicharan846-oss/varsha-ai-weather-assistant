"""Server-side speech (optional). By default the browser's Web Speech API does STT/TTS (works offline of this
server, supports en-IN / te-IN / hi-IN where the OS provides voices). Set VOICE_PROVIDER=openai to enable these
endpoints against an OpenAI-compatible speech API."""
import httpx

from app.config import get_settings
from app.exceptions import AIUnavailable, VoiceNotConfigured

LANG_CODES = {"en": "en", "te": "te", "hi": "hi"}


def _cfg():
    s = get_settings()
    if s.voice_provider != "openai" or not s.ai_api_key or s.ai_api_key.startswith("your_"):
        raise VoiceNotConfigured()
    return s, (s.ai_base_url or "https://api.openai.com/v1").rstrip("/")


async def transcribe(audio: bytes, filename: str, content_type: str, language: str) -> str:
    s, base = _cfg()
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{base}/audio/transcriptions", headers={"Authorization": f"Bearer {s.ai_api_key}"},
                             data={"model": s.voice_stt_model, "language": LANG_CODES.get(language, "en")},
                             files={"file": (filename or "audio.webm", audio, content_type or "audio/webm")})
            r.raise_for_status()
            return r.json()["text"].strip()
    except (httpx.HTTPError, KeyError, ValueError):
        raise AIUnavailable("Speech recognition is unavailable right now.") from None


async def speak(text: str) -> bytes:
    s, base = _cfg()
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{base}/audio/speech", headers={"Authorization": f"Bearer {s.ai_api_key}"},
                             json={"model": s.voice_tts_model, "voice": s.voice_tts_voice, "input": text[:1500]})
            r.raise_for_status()
            return r.content
    except httpx.HTTPError:
        raise AIUnavailable("Speech synthesis is unavailable right now.") from None
