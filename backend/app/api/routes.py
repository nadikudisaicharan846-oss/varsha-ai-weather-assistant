import json
import logging

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.ai.service import get_ai
from app.alerts.service import alerts_response
from app.alerts.thresholds import load_thresholds
from app.api.deps import Place, client_id, get_chat, get_decision, get_lang, place, require_client_id
from app.climate.analysis import PARAMS
from app.climate.service import climate_report
from app.config import get_settings
from app.database import repo, session as db
from app.decision.advisor import SECTORS, DecisionService
from app.exceptions import AIUnavailable, BadRequest
from app.i18n.messages import LANGS
from app.schemas.alerts import AlertsResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.climate import ClimateReport
from app.schemas.decision import DecisionReport
from app.schemas.storage import (AlertRecordOut, MessageOut, SavedAnalysisIn, SavedAnalysisOut, SavedLocationIn,
                                 SavedLocationOut)
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse, MarineResponse
from app.services.weather_service import WeatherService, get_weather_service
from app.voice import service as voice

log = logging.getLogger("varsha.api")
router = APIRouter(prefix="/api")


# ------------------------------------------------------------------ system
@router.get("/health", tags=["system"])
async def health():
    s = get_settings()
    return {"status": "ok", "service": s.app_name, "weather_provider": s.weather_provider,
            "ai": {"enabled": s.ai_enabled, "provider": s.ai_provider if s.ai_enabled else "none"},
            "database": db.available, "voice_provider": s.voice_provider, "languages": LANGS}


# ------------------------------------------------------------------ weather
@router.get("/weather/current", response_model=CurrentWeatherResponse, tags=["weather"])
async def current_weather(p: Place = Depends(place), ws: WeatherService = Depends(get_weather_service)):
    """Current conditions. Provide `city` OR both `lat` and `lon`."""
    return await ws.current(p.city, p.lat, p.lon)


@router.get("/weather/forecast", response_model=ForecastResponse, tags=["weather"])
async def forecast(p: Place = Depends(place), ws: WeatherService = Depends(get_weather_service)):
    """72 hourly points + 7 daily points."""
    return await ws.forecast(p.city, p.lat, p.lon)


@router.get("/weather/marine", response_model=MarineResponse, tags=["weather"])
async def marine(p: Place = Depends(place), ws: WeatherService = Depends(get_weather_service)):
    """Wave data for coastal points (available=false inland)."""
    return await ws.marine(p.city, p.lat, p.lon)


# ------------------------------------------------------------------ alerts
@router.get("/alerts", response_model=AlertsResponse, tags=["alerts"])
async def alerts(p: Place = Depends(place), lang: str = Depends(get_lang), cid: str | None = Depends(client_id),
                 ws: WeatherService = Depends(get_weather_service)):
    fc = await ws.forecast(p.city, p.lat, p.lon)
    resp = alerts_response(fc, lang)
    if cid and db.available and resp.alerts and not fc.source.is_mock:
        try:
            await run_in_threadpool(repo.record_alerts, cid, resp.alerts)
        except Exception:  # history is a convenience; never fail the request
            log.warning("could not record alert history")
    return resp


@router.get("/alerts/thresholds", tags=["alerts"])
async def thresholds():
    """The active, configurable alert thresholds."""
    return load_thresholds()


@router.get("/alerts/history", response_model=list[AlertRecordOut], tags=["alerts"])
def alert_history(cid: str = Depends(require_client_id)):
    return repo.list_alert_history(cid)


# ------------------------------------------------------------------ climate
@router.get("/climate/history", response_model=ClimateReport, tags=["climate"])
async def climate_history(p: Place = Depends(place), parameter: str = Query("rainfall", pattern="^(rainfall|temperature|humidity)$"),
                          years: int = Query(10, ge=3, le=30), lang: str = Depends(get_lang), ai: bool = False,
                          ws: WeatherService = Depends(get_weather_service)):
    """Observed (ERA5 reanalysis) history, statistics and a linear trend. `ai=true` adds a separate AI interpretation."""
    loc = await ws.resolve(p.city, p.lat, p.lon)
    rep = await climate_report(ws, loc, parameter, years, lang)
    llm = get_ai()
    if ai and llm:
        try:
            rep.ai_interpretation = await llm.interpret_climate(
                {"parameter": parameter, "unit": rep.unit, "period": f"{rep.start_year}-{rep.end_year}", "stats": rep.stats,
                 "trend": rep.trend.model_dump(exclude={"line"}) if rep.trend else None}, lang)
        except AIUnavailable:
            pass
    return rep


# ------------------------------------------------------------------ decision support
@router.get("/decision/{sector}", response_model=DecisionReport, tags=["decision"])
async def decision(sector: str, p: Place = Depends(place), day: int = Query(0, ge=0, le=6),
                   lang: str = Depends(get_lang), svc: DecisionService = Depends(get_decision)):
    if sector not in SECTORS:
        raise BadRequest(f"Unknown sector. Choose one of: {', '.join(SECTORS)}.")
    return await svc.report(sector, p.city, p.lat, p.lon, day, lang)


# ------------------------------------------------------------------ chat
@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(req: ChatRequest, cid: str | None = Depends(client_id), svc=Depends(get_chat)):
    resp = await svc.handle(req)
    if cid and db.available:
        try:
            await run_in_threadpool(repo.save_messages, cid, resp.session_id,
                                    [("user", req.message, resp.intent), ("assistant", resp.reply, resp.intent)])
        except Exception:
            log.warning("could not store conversation")
    return resp


# ------------------------------------------------------------------ voice
@router.post("/voice/transcribe", tags=["voice"])
async def voice_transcribe(audio: UploadFile = File(...), language: str = Form("en")):
    if language not in LANGS:
        from app.exceptions import UnsupportedLanguage
        raise UnsupportedLanguage()
    data = await audio.read()
    if len(data) > 10_000_000:
        raise BadRequest("Audio file too large (max 10 MB).")
    return {"text": await voice.transcribe(data, audio.filename or "audio.webm", audio.content_type or "", language)}


class SpeakIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=1500)
    language: str = "en"




@router.post("/voice/speak", tags=["voice"])
async def voice_speak(body: SpeakIn):
    if body.language == "te":
        from app.voice.telugu_tts import generate_telugu_audio

        audio = await run_in_threadpool(
            generate_telugu_audio, body.text
        )
        return Response(
            content=audio,
            media_type="audio/wav",
        )

    return Response(
        content=await voice.speak(body.text),
        media_type="audio/mpeg",
    )




# ------------------------------------------------------------------ saved data (optional DB)
@router.get("/locations", response_model=list[SavedLocationOut], tags=["saved"])
def get_locations(cid: str = Depends(require_client_id)):
    return repo.list_locations(cid)


@router.post("/locations", response_model=SavedLocationOut, tags=["saved"])
def save_location(body: SavedLocationIn, cid: str = Depends(require_client_id)):
    return repo.add_location(cid, body.model_dump())


@router.delete("/locations/{lid}", tags=["saved"])
def remove_location(lid: int, cid: str = Depends(require_client_id)):
    return {"deleted": repo.delete_location(cid, lid)}


@router.get("/analyses", response_model=list[SavedAnalysisOut], tags=["saved"])
def get_analyses(cid: str = Depends(require_client_id)):
    return [SavedAnalysisOut(id=r.id, title=r.title, location=r.location, parameter=r.parameter, years=r.years,
                             summary=json.loads(r.summary_json), created_at=r.created_at) for r in repo.list_analyses(cid)]


@router.post("/analyses", response_model=SavedAnalysisOut, tags=["saved"])
def save_analysis(body: SavedAnalysisIn, cid: str = Depends(require_client_id)):
    r = repo.add_analysis(cid, body.model_dump())
    return SavedAnalysisOut(id=r.id, title=r.title, location=r.location, parameter=r.parameter, years=r.years,
                            summary=body.summary, created_at=r.created_at)


@router.delete("/analyses/{aid}", tags=["saved"])
def remove_analysis(aid: int, cid: str = Depends(require_client_id)):
    return {"deleted": repo.delete_analysis(cid, aid)}


@router.get("/history/conversations", response_model=list[MessageOut], tags=["saved"])
def conversations(cid: str = Depends(require_client_id)):
    return repo.list_messages(cid)
