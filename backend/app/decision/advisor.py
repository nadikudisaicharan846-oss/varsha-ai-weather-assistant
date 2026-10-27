"""Rule-based decision support. All numbers come from the weather data; thresholds are general guidance."""
from app.alerts.service import build_alerts
from app.climate.service import climate_report
from app.i18n.messages import t
from app.schemas.alerts import Alert
from app.schemas.decision import Check, DecisionReport
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse, MarineResponse
from app.services.weather_service import WeatherService

SECTORS = ["agriculture", "disaster", "aviation", "marine", "urban"]
ORDER = {"na": 0, "info": 0, "good": 1, "caution": 2, "avoid": 3}


def day_label(offset: int, fc: ForecastResponse, lang: str) -> str:
    keys = {0: "day.today", 1: "day.tomorrow", 2: "day.day_after"}
    if offset in keys:
        return t(keys[offset], lang)
    from app.alerts.engine import fmt_date
    return fmt_date(fc.daily[offset].date)


def window(fc: ForecastResponse, offset: int, start_h: int = 0, end_h: int = 23) -> dict:
    """Aggregate hourly data for one day (falls back to daily values beyond the 72 h hourly range)."""
    d = fc.daily[offset]
    hrs = [h for h in fc.hourly if h.time[:10] == d.date and start_h <= int(h.time[11:13]) <= end_h]

    def mx(vals):
        vals = [v for v in vals if v is not None]
        return max(vals) if vals else None

    if hrs:
        hum = [h.humidity_pct for h in hrs if h.humidity_pct is not None]
        vis = [h.visibility_km for h in hrs if h.visibility_km is not None]
        cl = [h.cloud_cover_pct for h in hrs if h.cloud_cover_pct is not None]
        return {
            "prob": mx(h.rain_probability_pct for h in hrs) or 0, "mm": round(sum(h.precipitation_mm for h in hrs), 1),
            "wind": mx(h.wind_speed_kmh for h in hrs), "gust": mx(h.wind_gusts_kmh for h in hrs),
            "temp": mx(h.temperature_c for h in hrs), "hum": round(sum(hum) / len(hum)) if hum else None,
            "vis": min(vis) if vis else None, "cloud": round(sum(cl) / len(cl)) if cl else None,
            "thunder": any(h.weather_code >= 95 for h in hrs), "hourly": True}
    return {"prob": d.rain_probability_pct or 0, "mm": d.precipitation_sum_mm, "wind": d.wind_max_kmh,
            "gust": d.wind_gusts_max_kmh, "temp": d.temp_max_c, "hum": None, "vis": None, "cloud": None,
            "thunder": d.weather_code >= 95, "hourly": False}


def _chk(key: str, lang: str, value: str, status: str) -> Check:
    return Check(key=key, label=t(f"check.{key}", lang), value=value, status=status)


def _band(v, good, caution):
    if v is None:
        return "na"
    return "good" if v <= good else "caution" if v <= caution else "avoid"


def _fmt(v, unit, nd=0):
    return t("val.na", "en") if v is None else f"{round(v, nd) if nd else round(v)} {unit}".strip()


def worst(checks: list[Check]) -> str:
    return max((c.status for c in checks), key=lambda s: ORDER[s], default="info") if checks else "info"


class DecisionService:
    def __init__(self, ws: WeatherService):
        self.ws = ws

    async def report(self, sector: str, city=None, lat=None, lon=None, day: int = 0, lang: str = "en") -> DecisionReport:
        loc = await self.ws.resolve(city, lat, lon)
        cur, fc = await self._bundle(loc)
        day = max(0, min(day, len(fc.daily) - 1))
        fn = getattr(self, f"_{sector}")
        return await fn(loc, cur, fc, day, lang)

    async def _bundle(self, loc):
        import asyncio
        cur, fc = await asyncio.gather(self.ws._cur_for(loc), self.ws.forecast(loc=loc))
        return cur, fc

    # ---------------- agriculture ----------------
    async def _agriculture(self, loc, cur, fc, day, lang):
        w = window(fc, day, 6, 18)
        checks = [
            _chk("rain", lang, f"{w['prob']}%", _band(w["prob"], 30, 59)),
            _chk("rain_mm", lang, _fmt(w["mm"], "mm", 1), "info"),
            _chk("wind", lang, _fmt(w["wind"], "km/h"), _band(w["wind"], 15, 25)),
            _chk("temp", lang, _fmt(w["temp"], "°C"), _band(w["temp"], 32, 38)),
        ]
        hum = w["hum"]
        checks.append(_chk("humidity", lang, _fmt(hum, "%"),
                           "na" if hum is None else "good" if 40 <= hum <= 85 else "caution"))
        verdict = worst(checks)
        verdict = "good" if verdict in ("info", "na") else verdict
        recs = []
        s = {c.key: c.status for c in checks}
        for key, rk in (("rain", "rain"), ("wind", "wind"), ("temp", "temp"), ("humidity", "humidity")):
            if s.get(key) in ("caution", "avoid"):
                recs.append(t(f"rec.agri.{rk}", lang))
        if verdict == "good":
            recs.append(t("rec.agri.good", lang))
        if fc.daily[day].precipitation_sum_mm >= 10:
            recs.append(t("rec.agri.irrigation", lang))
        return self._wrap("agriculture", loc, fc, day, lang, verdict, t(f"verdict.agri.{verdict}", lang), checks, recs, "disclaimer.agri")

    # ---------------- aviation ----------------
    async def _aviation(self, loc, cur, fc, day, lang):
        w = window(fc, day)
        checks = [
            _chk("wind", lang, _fmt(w["wind"], "km/h"), _band(w["wind"], 25, 37)),
            _chk("gust", lang, _fmt(w["gust"], "km/h"), _band(w["gust"], 35, 50)),
            _chk("vis", lang, _fmt(w["vis"], "km", 1),
                 "na" if w["vis"] is None else "good" if w["vis"] >= 5 else "caution" if w["vis"] >= 1.5 else "avoid"),
            _chk("thunder", lang, t("val.possible" if w["thunder"] else "val.none", lang), "avoid" if w["thunder"] else "good"),
            _chk("cloud", lang, _fmt(w["cloud"], "%"), "info" if w["cloud"] is not None else "na"),
            _chk("rain", lang, f"{w['prob']}%", "info"),
        ]
        s = {c.key: c.status for c in checks}
        recs = []
        if s["thunder"] == "avoid":
            recs.append(t("rec.aviation.thunder", lang))
        if s["vis"] in ("caution", "avoid"):
            recs.append(t("rec.aviation.vis", lang))
        if s["wind"] in ("caution", "avoid") or s["gust"] in ("caution", "avoid"):
            recs.append(t("rec.aviation.wind", lang))
        verdict = worst(checks)
        verdict = "good" if verdict in ("info", "na") else verdict
        if not recs:
            recs.append(t("rec.aviation.good", lang))
        return self._wrap("aviation", loc, fc, day, lang, verdict, t(f"verdict.{verdict}", lang), checks, recs, "disclaimer.aviation")

    # ---------------- marine ----------------
    async def _marine(self, loc, cur, fc, day, lang):
        w = window(fc, day)
        mar: MarineResponse = await self.ws.marine(loc=loc)
        date = fc.daily[day].date
        waves = [p.wave_height_m for p in mar.hourly if p.time[:10] == date and p.wave_height_m is not None]
        wmax = max(waves) if waves else None
        checks = [
            _chk("wind", lang, _fmt(w["wind"], "km/h"), _band(w["wind"], 25, 40)),
            _chk("gust", lang, _fmt(w["gust"], "km/h"), _band(w["gust"], 35, 55)),
            _chk("rain", lang, f"{w['prob']}%", "info"),
            _chk("thunder", lang, t("val.possible" if w["thunder"] else "val.none", lang), "avoid" if w["thunder"] else "good"),
            _chk("waves", lang, _fmt(wmax, "m", 1), _band(wmax, 1.5, 2.5)),
        ]
        s = {c.key: c.status for c in checks}
        recs = []
        if s["wind"] in ("caution", "avoid") or s["gust"] == "avoid":
            recs.append(t("rec.marine.wind", lang))
        if s["waves"] in ("caution", "avoid"):
            recs.append(t("rec.marine.waves", lang))
        if s["thunder"] == "avoid":
            recs.append(t("rec.marine.thunder", lang))
        if w["prob"] >= 70 and w["mm"] >= 10:
            recs.append(t("rec.marine.rain", lang))
        verdict = worst(checks)
        verdict = "good" if verdict in ("info", "na") else verdict
        if not recs:
            recs.append(t("rec.marine.good", lang))
        rep = self._wrap("marine", loc, fc, day, lang, verdict, t(f"verdict.{verdict}", lang), checks, recs, "disclaimer.marine")
        if not mar.available:
            rep.source = mar.source if mar.source.is_mock else rep.source
        return rep

    # ---------------- disaster management ----------------
    async def _disaster(self, loc, cur, fc, day, lang):
        alerts: list[Alert] = build_alerts(fc, lang)
        h24, h72 = fc.hourly[:24], fc.hourly[:72]
        rain24 = round(sum(h.precipitation_mm for h in h24), 1)
        rain72 = round(sum(d.precipitation_sum_mm for d in fc.daily[:3]), 1)
        gust = max([h.wind_gusts_kmh or 0 for h in h72] or [0])
        tmax = max([d.temp_max_c or 0 for d in fc.daily[:3]] or [0])
        top = max((a.level_rank for a in alerts), default=0)
        checks = [
            _chk("rain24", lang, f"{rain24} mm", "avoid" if rain24 >= 64.5 else "caution" if rain24 >= 15.6 else "good"),
            _chk("rain72", lang, f"{rain72} mm", "avoid" if rain72 >= 150 else "caution" if rain72 >= 100 else "good"),
            _chk("gust", lang, f"{round(gust)} km/h", _band(gust, 39, 59)),
            _chk("temp", lang, f"{round(tmax)} °C", _band(tmax, 39, 42)),
            _chk("alerts", lang, str(len(alerts)), "avoid" if top >= 3 else "caution" if top == 2 else "good" if not alerts else "info"),
        ]
        verdict = "avoid" if top >= 3 else "caution" if top == 2 else worst(checks)
        verdict = "good" if verdict in ("info", "na") else verdict
        recs, seen = [], set()
        for a in alerts:
            if a.type not in seen:
                seen.add(a.type)
                recs.extend(a.advice[:2])
        recs.append(t("rec.disaster.general", lang) if alerts else t("rec.disaster.none", lang))
        rep = self._wrap("disaster", loc, fc, day, lang, verdict, t(f"verdict.{verdict}", lang), checks, recs, "disclaimer.disaster")
        rep.alerts_summary = [f"{a.icon} {a.level_label}: {a.title} — {a.summary}" for a in alerts]
        return rep

    # ---------------- urban planning ----------------
    async def _urban(self, loc, cur, fc, day, lang):
        checks, recs = [], []
        rain_up = heat_up = False
        src = fc.source
        for param, key in (("rainfall", "rain_trend"), ("temperature", "heat_trend")):
            try:
                rep = await climate_report(self.ws, loc, param, 10, lang)
                tr = rep.trend
                if tr:
                    up = tr.direction == "increasing"
                    val = f"{'+' if tr.slope_per_decade >= 0 else ''}{tr.slope_per_decade} {rep.unit}/decade" + (" ✓" if tr.significant else "")
                    checks.append(_chk(key, lang, val, "caution" if up else "info"))
                    rain_up |= up and param == "rainfall"
                    heat_up |= up and param == "temperature"
                else:
                    checks.append(_chk(key, lang, t("val.na", lang), "na"))
            except Exception:  # historical data is optional here
                checks.append(_chk(key, lang, t("val.na", lang), "na"))
        rain72 = round(sum(d.precipitation_sum_mm for d in fc.daily[:3]), 1)
        tmax = max([d.temp_max_c or 0 for d in fc.daily[:3]] or [0])
        checks.append(_chk("rain72", lang, f"{rain72} mm", "avoid" if rain72 >= 150 else "caution" if rain72 >= 64.5 else "good"))
        checks.append(_chk("temp", lang, f"{round(tmax)} °C", _band(tmax, 39, 42)))
        if rain_up:
            recs.append(t("rec.urban.rain_up", lang))
        if heat_up:
            recs.append(t("rec.urban.heat_up", lang))
        if rain72 >= 64.5:
            recs.append(t("rec.urban.near_rain", lang))
        if not recs:
            recs.append(t("rec.urban.none", lang))
        verdict = worst(checks)
        verdict = "good" if verdict in ("info", "na") else verdict
        return self._wrap("urban", loc, fc, day, lang, verdict, t(f"verdict.{verdict}", lang), checks, recs, "disclaimer.urban")

    def _wrap(self, sector, loc, fc, day, lang, verdict, headline, checks, recs, disc):
        return DecisionReport(sector=sector, location=loc, period=day_label(day, fc, lang), date=fc.daily[day].date,
                              verdict=verdict, headline=headline, checks=checks, recommendations=recs,
                              disclaimer=t(disc, lang), language=lang, source=fc.source)
