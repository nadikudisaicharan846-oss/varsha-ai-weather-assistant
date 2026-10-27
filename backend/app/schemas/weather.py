from pydantic import BaseModel


class Location(BaseModel):
    name: str
    admin1: str | None = None
    country: str | None = None
    latitude: float
    longitude: float
    timezone: str | None = None
    is_region: bool = False  # True when the match is a state/district (we use its centre point)


class CurrentWeather(BaseModel):
    observed_at: str
    temperature_c: float
    feels_like_c: float
    humidity_pct: int
    wind_speed_kmh: float
    wind_gusts_kmh: float | None = None
    wind_direction_deg: int | None = None
    precipitation_mm: float
    rain_probability_pct: int | None = None  # today's maximum
    uv_index: float | None = None  # today's maximum
    visibility_km: float | None = None
    pressure_hpa: float | None = None
    cloud_cover_pct: int | None = None
    aqi_us: int | None = None
    pm25: float | None = None
    condition: str
    condition_key: str = "unknown"
    weather_code: int
    is_day: bool
    temp_max_c: float | None = None
    temp_min_c: float | None = None
    sunrise: str | None = None
    sunset: str | None = None


class DataSource(BaseModel):
    provider: str
    url: str
    is_mock: bool
    fetched_at: str


class CurrentWeatherResponse(BaseModel):
    location: Location
    current: CurrentWeather
    source: DataSource


class HourlyPoint(BaseModel):
    time: str  # local ISO "YYYY-MM-DDTHH:00"
    temperature_c: float | None = None
    humidity_pct: int | None = None
    rain_probability_pct: int | None = None
    precipitation_mm: float = 0.0
    wind_speed_kmh: float | None = None
    wind_gusts_kmh: float | None = None
    visibility_km: float | None = None
    cloud_cover_pct: int | None = None
    weather_code: int = 0
    condition_key: str = "unknown"


class DailyPoint(BaseModel):
    date: str
    weather_code: int = 0
    condition_key: str = "unknown"
    temp_max_c: float | None = None
    temp_min_c: float | None = None
    precipitation_sum_mm: float = 0.0
    rain_probability_pct: int | None = None
    wind_max_kmh: float | None = None
    wind_gusts_max_kmh: float | None = None
    uv_index: float | None = None
    sunrise: str | None = None
    sunset: str | None = None


class ForecastResponse(BaseModel):
    location: Location
    hourly: list[HourlyPoint]  # next 72 hours
    daily: list[DailyPoint]  # 7 days, daily[0] is today at the location
    source: DataSource


class MarinePoint(BaseModel):
    time: str
    wave_height_m: float | None = None
    wave_period_s: float | None = None


class MarineResponse(BaseModel):
    location: Location
    available: bool
    hourly: list[MarinePoint] = []
    source: DataSource
