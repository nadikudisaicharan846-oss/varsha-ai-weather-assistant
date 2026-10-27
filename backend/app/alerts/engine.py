from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date as _date

from app.alerts.thresholds import Thresholds
from app.i18n.messages import M, t
from app.schemas.alerts import Alert
from app.schemas.weather import ForecastResponse

RANK = {"information": 1, "advisory": 2, "warning": 3, "severe_warning": 4}
LEVEL_BY_RANK = {v: k for k, v in RANK.items()}
ICON = {"rain": "⚠️", "heat": "🌡️", "thunderstorm": "⛈️", "wind": "💨", "flood": "🌊", "fog": "🌫️"}
UNIT = {"rain": "mm", "heat": "°C", "wind": "km/h", "flood": "mm", "fog": "km"}


@dataclass
class RawAlert:
    type: str
    rank: int
    date: str
    start: str | None = None
    end: str | None = None
    peak: float | None = None
    params: dict = field(default_factory=dict)
    summary_key: str | None = None


def fmt_date(iso: str) -> str:
    d = _date.fromisoformat(iso[:10])
    return f"{d.day:02d} {d.strftime('%b')}"


def _rank(value: float, steps: list[tuple[float, int]]) -> int:
    r = 0
    for threshold, rank in steps:
        if value >= threshold:
            r = max(r, rank)
    return r


def evaluate(fc: ForecastResponse, th: Thresholds) -> list[RawAlert]:
    by_day = defaultdict(list)
    for h in fc.hourly:
        by_day[h.time[:10]].append(h)
    out: list[RawAlert] = []

    for i, d in enumerate(fc.daily):
        hours = by_day.get(d.date, [])
        prob = d.rain_probability_pct or 0

        # --- heavy rain ---
        r, mm = th.rain, d.precipitation_sum_mm or 0
        rank = 4 if mm >= r.severe_mm else 3 if mm >= r.warning_mm else \
            2 if (mm >= r.advisory_mm and prob >= r.advisory_prob) else \
            1 if (mm >= r.info_mm and prob >= r.info_prob) else 0
        if rank:
            wet = [h.time[11:16] for h in hours if h.precipitation_mm >= 0.5]
            out.append(RawAlert("rain", rank, d.date, d.date + "T" + wet[0] if wet else None,
                                d.date + "T" + wet[-1] if wet else None, mm,
                                {"mm": round(mm), "prob": prob}))

        # --- heat ---
        if d.temp_max_c is not None:
            h_ = th.heat
            rank = _rank(d.temp_max_c, [(h_.info_c, 1), (h_.advisory_c, 2), (h_.warning_c, 3), (h_.severe_c, 4)])
            if rank:
                out.append(RawAlert("heat", rank, d.date, peak=d.temp_max_c, params={"temp": round(d.temp_max_c)}))

        # --- thunderstorm ---
        codes = [h.weather_code for h in hours] or [d.weather_code]
        if max(codes) >= th.thunderstorm.warning_code:
            hail = any(c in th.thunderstorm.severe_codes for c in codes)
            low_prob = prob < th.thunderstorm.advisory_if_prob_below
            rank = 4 if hail else 2 if low_prob else 3
            ts = [h.time[11:16] for h in hours if h.weather_code >= th.thunderstorm.warning_code]
            out.append(RawAlert("thunderstorm", rank, d.date, d.date + "T" + ts[0] if ts else None,
                                d.date + "T" + ts[-1] if ts else None, params={},
                                summary_key="summary_hail" if hail else "summary"))

        # --- strong wind ---
        gust = d.wind_gusts_max_kmh
        if gust is not None:
            w = th.wind
            rank = _rank(gust, [(w.advisory_gust_kmh, 2), (w.warning_gust_kmh, 3), (w.severe_gust_kmh, 4)])
            if rank:
                out.append(RawAlert("wind", rank, d.date, peak=gust, params={"gust": round(gust)}))

        # --- low visibility ---
        vis = [h.visibility_km for h in hours if h.visibility_km is not None]
        if vis:
            f = th.fog
            v = min(vis)
            rank = 3 if v < f.warning_visibility_km else 2 if v < f.advisory_visibility_km else 0
            if rank:
                out.append(RawAlert("fog", rank, d.date, peak=v, params={"vis": v}))

    # --- flood risk: rolling 3-day rainfall, keep local maxima only ---
    sums = [sum(x.precipitation_sum_mm or 0 for x in fc.daily[i:i + 3]) for i in range(len(fc.daily))]
    for i, s in enumerate(sums):
        f = th.flood
        rank = _rank(s, [(f.advisory_3day_mm, 2), (f.warning_3day_mm, 3), (f.severe_3day_mm, 4)])
        left = sums[i - 1] if i > 0 else -1
        right = sums[i + 1] if i + 1 < len(sums) else -1
        if rank and s >= left and s > right:
            out.append(RawAlert("flood", rank, fc.daily[i].date, peak=s, params={"mm": round(s)}))

    out.sort(key=lambda a: (-a.rank, a.date))
    return out


def localize(raw: RawAlert, place: str, lang: str, location_name: str) -> Alert:
    key = raw.summary_key or "summary"
    params = {"place": place, "date": fmt_date(raw.date), **raw.params}
    summary = t(f"alert.{raw.type}.{key}", lang, **params)
    if raw.start and raw.end and raw.start != raw.end:
        summary += " " + t("alert.period", lang, start=raw.start[11:16], end=raw.end[11:16])
    advice = [t(f"alert.{raw.type}.a{n}", lang) for n in (1, 2, 3)
              if f"alert.{raw.type}.a{n}" in M]
    level = LEVEL_BY_RANK[raw.rank]
    return Alert(
        id=f"{raw.type}-{raw.date}", type=raw.type, level=level, level_rank=raw.rank,
        level_label=t(f"level.{level}", lang), icon=ICON[raw.type], title=t(f"alert.{raw.type}.title", lang),
        summary=summary, advice=advice, starts_at=raw.start, ends_at=raw.end, date=raw.date,
        peak_value=round(raw.peak, 1) if raw.peak is not None else None, peak_unit=UNIT.get(raw.type),
        location_name=location_name)
