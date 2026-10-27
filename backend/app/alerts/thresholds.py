import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from app.config import get_settings


class Rain(BaseModel):
    info_mm: float = 15.6      # IMD "moderate" lower bound
    info_prob: int = 50
    advisory_mm: float = 35
    advisory_prob: int = 60
    warning_mm: float = 64.5   # IMD "heavy" lower bound (24 h)
    severe_mm: float = 115.6   # IMD "very heavy" lower bound


class Heat(BaseModel):
    info_c: float = 38
    advisory_c: float = 40
    warning_c: float = 43
    severe_c: float = 45


class Thunder(BaseModel):
    warning_code: int = 95
    severe_codes: list[int] = [96, 99]
    advisory_if_prob_below: int = 40


class Wind(BaseModel):
    advisory_gust_kmh: float = 40
    warning_gust_kmh: float = 60
    severe_gust_kmh: float = 90


class Flood(BaseModel):
    advisory_3day_mm: float = 100
    warning_3day_mm: float = 150
    severe_3day_mm: float = 250


class Fog(BaseModel):
    advisory_visibility_km: float = 1.0
    warning_visibility_km: float = 0.2


class Thresholds(BaseModel):
    rain: Rain = Rain()
    heat: Heat = Heat()
    thunderstorm: Thunder = Thunder()
    wind: Wind = Wind()
    flood: Flood = Flood()
    fog: Fog = Fog()


@lru_cache
def load_thresholds() -> Thresholds:
    """Thresholds live in a JSON file (override path with ALERT_THRESHOLDS_FILE) — never hard-coded in logic."""
    path = get_settings().alert_thresholds_file or str(Path(__file__).with_name("thresholds.json"))
    try:
        return Thresholds(**json.loads(Path(path).read_text()))
    except (OSError, ValueError):
        return Thresholds()
