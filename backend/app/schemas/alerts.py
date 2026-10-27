from pydantic import BaseModel

from app.schemas.weather import DataSource, Location

LEVELS = ["information", "advisory", "warning", "severe_warning"]


class Alert(BaseModel):
    id: str
    type: str  # rain | heat | thunderstorm | wind | flood | fog
    level: str
    level_rank: int  # 1..4
    level_label: str
    icon: str
    title: str
    summary: str
    advice: list[str]
    starts_at: str | None = None
    ends_at: str | None = None
    date: str
    peak_value: float | None = None
    peak_unit: str | None = None
    location_name: str
    forecast_based: bool = True


class AlertsResponse(BaseModel):
    location: Location
    language: str
    alerts: list[Alert]
    highest_level: str | None
    disclaimer: str
    limitations: str
    generated_at: str
    source: DataSource
