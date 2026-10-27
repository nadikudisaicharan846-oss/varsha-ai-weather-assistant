from datetime import datetime

from pydantic import BaseModel, Field


class SavedLocationIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    admin1: str | None = Field(None, max_length=120)
    country: str | None = Field(None, max_length=120)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class SavedLocationOut(SavedLocationIn):
    id: int
    created_at: datetime


class SavedAnalysisIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    location: str = Field(..., max_length=160)
    parameter: str = Field(..., max_length=20)
    years: int = Field(..., ge=1, le=60)
    summary: dict


class SavedAnalysisOut(SavedAnalysisIn):
    id: int
    created_at: datetime


class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    intent: str | None = None
    created_at: datetime


class AlertRecordOut(BaseModel):
    id: int
    location: str
    alert_type: str
    level: str
    title: str
    date: str
    created_at: datetime
