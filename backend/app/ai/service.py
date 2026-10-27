import json
import re
from functools import lru_cache

from app.ai.base import LLMProvider
from app.ai.providers import AnthropicProvider, OpenAICompatible
from app.config import get_settings
from app.i18n.messages import LANGS

LANG_NAMES = {"en": "English", "te": "Telugu", "hi": "Hindi"}

SYSTEM_REPLY = """You are Varsha AI, a weather and climate assistant for India.
STRICT RULES:
- Use ONLY the values in FACTS. Never invent or change numbers, dates, places, alerts or warnings. If something is not in FACTS, say it is not available.
- Forecasts are uncertain: use words like "expected" or "likely", never "guaranteed".
- You are NOT an official government warning source. For severe weather, advise following IMD and local authorities.
- Reply in {language}. Keep all numbers, units, percentages and dates exactly as in FACTS (do not convert digits or units).
- Audience: {persona}. Give clear, practical, safe advice in simple language. Maximum ~110 words. No markdown headings.
You are given the user's question, FACTS (JSON) and a BASELINE answer generated from the data. Improve the baseline's clarity and advice without adding any new data."""

SYSTEM_PARSE = """You extract structured intent from a weather question (any language). Reply with ONLY a JSON object:
{"intent": one of ["weather","rain","temperature","wind","humidity","forecast_range","alerts","travel","safety_advice","climate_trend","agriculture","disaster","aviation","marine","urban","other"],
 "location": place name in English or null,
 "date_start": integer days from today (0=today) or null, "date_end": integer or null,
 "parameter": "rainfall"|"temperature"|"humidity"|null, "years": integer or null,
 "reply_language": "en"|"te"|"hi"|null}
Do not answer the question."""

SYSTEM_CLIMATE = """You are a careful climate data explainer. Using ONLY the statistics given, write 2-3 plain sentences in {language}.
Clearly separate what was observed from what the statistics suggest. Do not claim causes, and do not claim that a short single-location record proves climate change. Keep numbers exactly."""


class AIService:
    def __init__(self, provider: LLMProvider):
        self.p = provider

    async def parse_query(self, message: str, context: dict) -> dict | None:
        raw = await self.p.complete(SYSTEM_PARSE, [{"role": "user", "content": json.dumps(
            {"message": message, "context": context}, ensure_ascii=False)}], max_tokens=200)
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except ValueError:
            return None

    async def compose_reply(self, question, facts, baseline, lang, persona, history) -> str:
        system = SYSTEM_REPLY.format(language=LANG_NAMES.get(lang, "English"), persona=persona)
        user = json.dumps({"question": question, "FACTS": facts, "BASELINE": baseline}, ensure_ascii=False)
        return await self.p.complete(system, [*history[-4:], {"role": "user", "content": user}], max_tokens=450)

    async def interpret_climate(self, stats: dict, lang: str) -> str:
        system = SYSTEM_CLIMATE.format(language=LANG_NAMES.get(lang, "English"))
        return await self.p.complete(system, [{"role": "user", "content": json.dumps(stats, ensure_ascii=False)}], max_tokens=300)


@lru_cache
def get_ai() -> AIService | None:
    s = get_settings()
    if not s.ai_enabled:
        return None
    return AIService(AnthropicProvider(s) if s.ai_provider == "anthropic" else OpenAICompatible(s))
