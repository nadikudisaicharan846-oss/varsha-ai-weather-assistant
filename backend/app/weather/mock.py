import math
from datetime import date, datetime, timedelta

from app.exceptions import LocationNotFound
from app.schemas.weather import CurrentWeather, DailyPoint, HourlyPoint, Location, MarinePoint
from app.weather.base import WeatherProvider
from app.weather.weather_codes import condition_key, describe

# key -> (display name, state, lat, lon, is_region, coastal)
_PLACES = {
    "hyderabad": ("Hyderabad", "Telangana", 17.385, 78.4867, False, False),
    "nalgonda": ("Nalgonda", "Telangana", 17.05, 79.27, False, False),
    "warangal": ("Warangal", "Telangana", 17.9689, 79.5941, False, False),
    "vijayawada": ("Vijayawada", "Andhra Pradesh", 16.5062, 80.648, False, False),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185, False, True),
    "mumbai": ("Mumbai", "Maharashtra", 19.076, 72.8777, False, True),
    "chennai": ("Chennai", "Tamil Nadu", 13.0827, 80.2707, False, True),
    "delhi": ("Delhi", "Delhi", 28.6139, 77.209, False, False),
    "bengaluru": ("Bengaluru", "Karnataka", 12.9716, 77.5946, False, False),
    "bangalore": ("Bengaluru", "Karnataka", 12.9716, 77.5946, False, False),
    "telangana": ("Telangana", "Telangana", 17.9, 79.0, True, False),
    "andhra pradesh": ("Andhra Pradesh", "Andhra Pradesh", 15.9, 79.7, True, True),
}


def _noise(seed: str) -> float:  # deterministic pseudo-random in [-1, 1]
    return (hash_str(seed) % 2000) / 1000 - 1


def hash_str(s: str) -> int:
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) % 1_000_003
    return h


class MockProvider(WeatherProvider):
    """SAMPLE DATA ONLY. Always labelled is_mock=True; never presented as real-time."""

    name = "Sample data (not real-time)"
    url = ""
    is_mock = True

    async def geocode(self, query: str) -> Location:
        e = _PLACES.get(query.strip().lower())
        if not e:
            raise LocationNotFound(query)
        name, state, lat, lon, region, _ = e
        return Location(name=name, admin1=state, country="India", latitude=lat, longitude=lon,
                        timezone="Asia/Kolkata", is_region=region)

    async def current(self, location: Location) -> CurrentWeather:
        now = datetime.now().replace(second=0, microsecond=0)
        day = now.strftime("%Y-%m-%d")
        return CurrentWeather(
            observed_at=now.strftime("%Y-%m-%dT%H:%M"), temperature_c=29.0, feels_like_c=32.5, humidity_pct=68,
            wind_speed_kmh=12.0, wind_gusts_kmh=21.0, wind_direction_deg=240, precipitation_mm=0.0,
            rain_probability_pct=40, uv_index=7.0, visibility_km=9.0, pressure_hpa=1008.0, cloud_cover_pct=55,
            aqi_us=82, pm25=24.0, condition=describe(2), condition_key=condition_key(2), weather_code=2,
            is_day=True, temp_max_c=33.0, temp_min_c=24.0, sunrise=f"{day}T06:05", sunset=f"{day}T18:10")

    async def forecast(self, location: Location):
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        hourly = []
        for i in range(72):
            tm = now + timedelta(hours=i)
            d = i // 24
            heavy = d == 2 and 14 <= tm.hour <= 20  # demo: heavy-rain afternoon on day 3
            rainy = d == 1 and 15 <= tm.hour <= 18
            code = 95 if (heavy and tm.hour in (16, 17)) else 65 if heavy else 61 if rainy else 2
            hourly.append(HourlyPoint(
                time=tm.strftime("%Y-%m-%dT%H:00"), temperature_c=round(28 + 5 * math.sin((tm.hour - 9) / 24 * 2 * math.pi), 1),
                humidity_pct=70 - int(15 * math.sin((tm.hour - 9) / 24 * 2 * math.pi)),
                rain_probability_pct=90 if heavy else 55 if rainy else 20,
                precipitation_mm=8.0 if heavy else 1.5 if rainy else 0.0,
                wind_speed_kmh=12.0 + (10 if heavy else 0), wind_gusts_kmh=22.0 + (25 if heavy else 0),
                visibility_km=4.0 if heavy else 9.0, cloud_cover_pct=90 if heavy else 50,
                weather_code=code, condition_key=condition_key(code)))
        today = date.today()
        specs = [(2, 33, 24, 0.5, 30), (61, 32, 24, 6.0, 65), (65, 29, 23, 72.0, 90), (3, 30, 23, 14.0, 60),
                 (2, 33, 24, 1.0, 25), (1, 34, 24, 0.0, 10), (0, 35, 25, 0.0, 5)]
        daily = []
        for i, (code, tmax, tmin, mm, prob) in enumerate(specs):
            day = (today + timedelta(days=i)).isoformat()
            daily.append(DailyPoint(
                date=day, weather_code=code, condition_key=condition_key(code), temp_max_c=tmax, temp_min_c=tmin,
                precipitation_sum_mm=mm, rain_probability_pct=prob, wind_max_kmh=14.0 + (10 if mm > 40 else 0),
                wind_gusts_max_kmh=25.0 + (30 if mm > 40 else 0), uv_index=7.0,
                sunrise=f"{day}T06:05", sunset=f"{day}T18:10"))
        return hourly, daily

    async def marine(self, location: Location):
        e = _PLACES.get(location.name.strip().lower())
        if not e or not e[5]:
            return []
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        return [MarinePoint(time=(now + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00"),
                            wave_height_m=round(1.2 + 0.4 * math.sin(i / 6), 2), wave_period_s=7.0) for i in range(48)]

    async def history(self, location, start, end, parameter):
        d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
        rows, d = [], d0
        while d <= d1:
            doy = d.timetuple().tm_yday
            trend = (d.year - 2000) * 0.03
            if parameter == "rainfall":
                monsoon = max(0.0, math.sin((doy - 150) / 120 * math.pi)) if 150 <= doy <= 270 else 0.0
                wet = _noise(f"{d}r") > 0.35
                v = round(monsoon * 22 * (1 + _noise(f"{d.year}y") * 0.4) if wet else 0.0, 1)
            elif parameter == "temperature":
                v = round(27 + 5 * math.sin((doy - 90) / 365 * 2 * math.pi) + trend + _noise(f"{d}t"), 1)
            else:
                v = round(60 + 20 * math.sin((doy - 180) / 365 * 2 * math.pi) + _noise(f"{d}h") * 4, 1)
            rows.append((d.isoformat(), v))
            d += timedelta(days=1)
        return rows
