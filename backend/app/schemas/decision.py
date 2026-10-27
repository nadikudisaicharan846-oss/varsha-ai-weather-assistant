from pydantic import BaseModel

from app.schemas.weather import DataSource, Location


class Check(BaseModel):
    key: str
    label: str
    value: str
    status: str  # good | caution | avoid | info | na


class DecisionReport(BaseModel):
    sector: str
    location: Location
    period: str  # human label e.g. "Tomorrow"
    date: str
    verdict: str  # good | caution | avoid | info
    headline: str
    checks: list[Check]
    recommendations: list[str]
    alerts_summary: list[str] = []
    disclaimer: str
    language: str
    source: DataSource
