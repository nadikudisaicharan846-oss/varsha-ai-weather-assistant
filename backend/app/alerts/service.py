from datetime import datetime, timezone

from app.alerts.engine import LEVEL_BY_RANK, evaluate, localize
from app.alerts.thresholds import load_thresholds
from app.i18n.messages import t
from app.schemas.alerts import Alert, AlertsResponse
from app.schemas.weather import ForecastResponse


def build_alerts(fc: ForecastResponse, lang: str) -> list[Alert]:
    place = fc.location.name
    return [localize(r, place, lang, place) for r in evaluate(fc, load_thresholds())]


def alerts_response(fc: ForecastResponse, lang: str) -> AlertsResponse:
    alerts = build_alerts(fc, lang)
    top = max((a.level_rank for a in alerts), default=0)
    return AlertsResponse(
        location=fc.location, language=lang, alerts=alerts, highest_level=LEVEL_BY_RANK.get(top),
        disclaimer=t("alert.disclaimer", lang, provider=fc.source.provider), limitations=t("alert.limits", lang),
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), source=fc.source)
