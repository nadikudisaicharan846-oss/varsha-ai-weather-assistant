import asyncio
from collections import defaultdict

import httpx

from app.exceptions import LocationNotFound, ProviderUnavailable, RateLimited
from app.schemas.weather import CurrentWeather, DailyPoint, HourlyPoint, Location, MarinePoint
from app.weather.base import WeatherProvider
from app.weather.weather_codes import condition_key, describe

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

CURRENT_VARS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,cloud_cover,"
    "surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,is_day"
)
DAILY_CUR = "temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,sunrise,sunset"
HOURLY_FC = (
    "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,"
    "wind_speed_10m,wind_gusts_10m,visibility,cloud_cover"
)
DAILY_FC = (
    "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,"
    "wind_speed_10m_max,wind_gusts_10m_max,uv_index_max,sunrise,sunset"
)


def _at(arr, i):
    try:
        return arr[i]
    except (IndexError, TypeError):
        return None


class OpenMeteoProvider(WeatherProvider):
    name = "Open-Meteo"
    url = "https://open-meteo.com"

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def _get(self, url: str, params: dict, *, allow_400: bool = False) -> dict | None:
        try:
            resp = await self.client.get(url, params=params)
        except httpx.HTTPError:
            raise ProviderUnavailable() from None
        if resp.status_code == 429:
            raise RateLimited()
        if resp.status_code == 400 and allow_400:
            return None
        if resp.status_code >= 400:
            raise ProviderUnavailable()
        try:
            return resp.json()
        except ValueError:
            raise ProviderUnavailable() from None

    async def geocode(self, query: str) -> Location:
        data = await self._get(GEOCODE_URL, {"name": query, "count": 10, "language": "en", "format": "json"})
        results = (data or {}).get("results") or []
        if not results:
            raise LocationNotFound(query)
        indian = [r for r in results if r.get("country_code") == "IN"]  # India-first
        r = (indian or results)[0]
        return Location(
            name=r["name"], admin1=r.get("admin1"), country=r.get("country"),
            latitude=r["latitude"], longitude=r["longitude"], timezone=r.get("timezone"),
            is_region=str(r.get("feature_code", "")).startswith("ADM1"),
        )

    async def _air_quality(self, loc: Location) -> tuple[int | None, float | None]:
        try:
            d = await self._get(AQ_URL, {"latitude": loc.latitude, "longitude": loc.longitude,
                                         "current": "us_aqi,pm2_5", "timezone": "auto"})
            cur = (d or {}).get("current") or {}
            aqi = cur.get("us_aqi")
            return (round(aqi) if aqi is not None else None), cur.get("pm2_5")
        except Exception:  # air quality is optional; never fail the main request
            return None, None

    async def current(self, location: Location) -> CurrentWeather:
        main, aq = await asyncio.gather(
            self._get(FORECAST_URL, {
                "latitude": location.latitude, "longitude": location.longitude,
                "current": CURRENT_VARS, "daily": DAILY_CUR, "hourly": "visibility",
                "timezone": "auto", "forecast_days": 1}),
            self._air_quality(location),
        )
        try:
            cur, daily = main["current"], main["daily"]

            def today(key):
                return _at(daily.get(key) or [], 0)

            vis = None
            hourly = main.get("hourly") or {}
            hk = cur["time"][:13] + ":00"
            if hk in (hourly.get("time") or []):
                v = hourly["visibility"][hourly["time"].index(hk)]
                vis = round(v / 1000, 1) if v is not None else None
            code = int(cur["weather_code"])
            return CurrentWeather(
                observed_at=cur["time"], temperature_c=round(cur["temperature_2m"], 1),
                feels_like_c=round(cur["apparent_temperature"], 1),
                humidity_pct=round(cur["relative_humidity_2m"]),
                wind_speed_kmh=round(cur["wind_speed_10m"], 1), wind_gusts_kmh=cur.get("wind_gusts_10m"),
                wind_direction_deg=cur.get("wind_direction_10m"),
                precipitation_mm=cur.get("precipitation") or 0.0,
                rain_probability_pct=today("precipitation_probability_max"),
                uv_index=today("uv_index_max"), visibility_km=vis,
                pressure_hpa=cur.get("surface_pressure"), cloud_cover_pct=cur.get("cloud_cover"),
                aqi_us=aq[0], pm25=aq[1],
                condition=describe(code), condition_key=condition_key(code), weather_code=code,
                is_day=bool(cur.get("is_day", 1)),
                temp_max_c=today("temperature_2m_max"), temp_min_c=today("temperature_2m_min"),
                sunrise=today("sunrise"), sunset=today("sunset"),
            )
        except (KeyError, TypeError, ValueError, IndexError):
            raise ProviderUnavailable("The weather service returned data we couldn't read. Please try again.") from None

    async def forecast(self, location: Location):
        d = await self._get(FORECAST_URL, {
            "latitude": location.latitude, "longitude": location.longitude,
            "current": "temperature_2m", "hourly": HOURLY_FC, "daily": DAILY_FC,
            "timezone": "auto", "forecast_days": 7})
        try:
            now_hour = d["current"]["time"][:13] + ":00"
            h = d["hourly"]
            times = h["time"]
            start = times.index(now_hour) if now_hour in times else 0
            hourly = []
            for i in range(start, min(start + 72, len(times))):
                code = int(_at(h["weather_code"], i) or 0)
                vis = _at(h["visibility"], i)
                hourly.append(HourlyPoint(
                    time=times[i], temperature_c=_at(h["temperature_2m"], i),
                    humidity_pct=_at(h["relative_humidity_2m"], i),
                    rain_probability_pct=_at(h["precipitation_probability"], i),
                    precipitation_mm=_at(h["precipitation"], i) or 0.0,
                    wind_speed_kmh=_at(h["wind_speed_10m"], i), wind_gusts_kmh=_at(h["wind_gusts_10m"], i),
                    visibility_km=round(vis / 1000, 1) if vis is not None else None,
                    cloud_cover_pct=_at(h["cloud_cover"], i), weather_code=code, condition_key=condition_key(code)))
            dd = d["daily"]
            daily = []
            for i, day in enumerate(dd["time"]):
                code = int(_at(dd["weather_code"], i) or 0)
                daily.append(DailyPoint(
                    date=day, weather_code=code, condition_key=condition_key(code),
                    temp_max_c=_at(dd["temperature_2m_max"], i), temp_min_c=_at(dd["temperature_2m_min"], i),
                    precipitation_sum_mm=_at(dd["precipitation_sum"], i) or 0.0,
                    rain_probability_pct=_at(dd["precipitation_probability_max"], i),
                    wind_max_kmh=_at(dd["wind_speed_10m_max"], i), wind_gusts_max_kmh=_at(dd["wind_gusts_10m_max"], i),
                    uv_index=_at(dd["uv_index_max"], i), sunrise=_at(dd["sunrise"], i), sunset=_at(dd["sunset"], i)))
            return hourly, daily
        except (KeyError, TypeError, ValueError):
            raise ProviderUnavailable("The weather service returned data we couldn't read. Please try again.") from None

    async def marine(self, location: Location) -> list[MarinePoint]:
        d = await self._get(MARINE_URL, {
            "latitude": location.latitude, "longitude": location.longitude,
            "hourly": "wave_height,wave_period", "timezone": "auto", "forecast_days": 3}, allow_400=True)
        if not d or "hourly" not in d:
            return []
        h = d["hourly"]
        pts = [MarinePoint(time=tm, wave_height_m=_at(h.get("wave_height"), i), wave_period_s=_at(h.get("wave_period"), i))
               for i, tm in enumerate(h.get("time", []))]
        return pts if any(p.wave_height_m is not None for p in pts) else []

    async def history(self, location, start, end, parameter):
        base = {"latitude": location.latitude, "longitude": location.longitude,
                "start_date": start, "end_date": end, "timezone": "auto"}
        if parameter == "humidity":  # no daily humidity in the archive API: average hourly values per day
            d = await self._get(ARCHIVE_URL, {**base, "hourly": "relative_humidity_2m"})
            h = (d or {}).get("hourly") or {}
            buckets: dict[str, list[float]] = defaultdict(list)
            for tm, v in zip(h.get("time", []), h.get("relative_humidity_2m", [])):
                if v is not None:
                    buckets[tm[:10]].append(v)
            return [(day, sum(v) / len(v)) for day, v in sorted(buckets.items())]
        var = "precipitation_sum" if parameter == "rainfall" else "temperature_2m_mean"
        d = await self._get(ARCHIVE_URL, {**base, "daily": var})
        dd = (d or {}).get("daily") or {}
        return list(zip(dd.get("time", []), dd.get(var, [])))
