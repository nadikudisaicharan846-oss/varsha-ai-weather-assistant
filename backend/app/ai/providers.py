import httpx

from app.config import Settings
from app.exceptions import AIUnavailable
from app.ai.base import LLMProvider


class OpenAICompatible(LLMProvider):
    """Works with OpenAI and any OpenAI-compatible endpoint (e.g. Gemini's OpenAI-compat URL, Groq, Ollama)."""

    name = "openai-compatible"

    def __init__(self, s: Settings):
        self.key, self.model = s.ai_api_key, s.ai_model or "gpt-4o-mini"
        self.base = (s.ai_base_url or "https://api.openai.com/v1").rstrip("/")
        self.client = httpx.AsyncClient(timeout=s.ai_timeout_seconds)

    async def complete(self, system, messages, *, max_tokens=500):
        body = {"model": self.model, "max_tokens": max_tokens, "temperature": 0.2,
                "messages": [{"role": "system", "content": system}, *messages]}
        try:
            r = await self.client.post(f"{self.base}/chat/completions", json=body,
                                       headers={"Authorization": f"Bearer {self.key}"})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, IndexError, ValueError):
            raise AIUnavailable() from None  # never include request details (they contain the key)


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, s: Settings):
        self.key, self.model = s.ai_api_key, s.ai_model or "claude-sonnet-5-5"
        self.base = (s.ai_base_url or "https://api.anthropic.com").rstrip("/")
        self.client = httpx.AsyncClient(timeout=s.ai_timeout_seconds)

    async def complete(self, system, messages, *, max_tokens=500):
        body = {"model": self.model, "max_tokens": max_tokens, "system": system, "messages": messages}
        try:
            r = await self.client.post(f"{self.base}/v1/messages", json=body,
                                       headers={"x-api-key": self.key, "anthropic-version": "2023-06-01"})
            r.raise_for_status()
            return "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text").strip()
        except (httpx.HTTPError, KeyError, ValueError):
            raise AIUnavailable() from None
