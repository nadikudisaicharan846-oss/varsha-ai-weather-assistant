from typing import Any

from pydantic import BaseModel, Field

from app.schemas.weather import DataSource, Location


class LocationHint(BaseModel):
    city: str | None = Field(None, max_length=80)
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: str | None = Field(None, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    language: str = Field("en", max_length=5)  # UI language preference
    location: LocationHint | None = None  # user's current/selected location


class Card(BaseModel):
    type: str  # current | daily | hourly | alerts | decision | climate
    data: Any


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    language: str
    intent: str
    location: Location | None = None
    date_label: str | None = None
    cards: list[Card] = []
    sources: list[DataSource] = []
    ai_mode: str  # llm | rule_based | llm_error_fallback
    parsed: dict[str, Any] = {}
    disclaimer: str
