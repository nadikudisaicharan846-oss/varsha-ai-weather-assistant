import re
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Header, Query

from app.chat.service import ChatService
from app.config import get_settings
from app.decision.advisor import DecisionService
from app.exceptions import BadRequest, UnsupportedLanguage
from app.i18n.messages import LANGS
from app.services.weather_service import WeatherService, get_weather_service

_CID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def get_lang(lang: str = Query("en", max_length=5)) -> str:
    if lang not in LANGS:
        raise UnsupportedLanguage()
    return lang


def client_id(x_client_id: str | None = Header(None)) -> str | None:
    return x_client_id if x_client_id and _CID.match(x_client_id) else None


def require_client_id(x_client_id: str | None = Header(None)) -> str:
    if not x_client_id or not _CID.match(x_client_id):
        raise BadRequest("Missing or invalid X-Client-Id header.")
    return x_client_id


@dataclass
class Place:
    city: str | None
    lat: float | None
    lon: float | None


def place(city: str | None = Query(None, min_length=2, max_length=80, description="City / district / state name"),
          lat: float | None = Query(None, ge=-90, le=90), lon: float | None = Query(None, ge=-180, le=180)) -> Place:
    if not city and (lat is None or lon is None):
        raise BadRequest("Provide a city, or both lat and lon.")
    return Place(city.strip() if city else None, lat, lon)


@lru_cache
def get_decision() -> DecisionService:
    return DecisionService(get_weather_service())


@lru_cache
def get_chat() -> ChatService:
    return ChatService(get_weather_service(), get_decision(), get_settings().default_city)
