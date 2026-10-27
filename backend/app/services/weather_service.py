import asyncio
import logging
from datetime import datetime, timezone
from functools import lru_cache

import httpx

from app.config import get_settings
from app.exceptions import ConfigurationError, LocationNotFound, ProviderUnavailable
from app.schemas.weather import (
    CurrentWeatherResponse, DataSource, ForecastResponse, Location, MarineResponse,
)
from app.utils.cache import TTLCache
from app.weather.base import WeatherProvider
from app.weather.mock import MockProvider
from app.weather.open_meteo import OpenMeteoProvider

log = logging.getLogger("varsha.weather")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class WeatherService:
    """Provider + cache + clearly-labelled mock fallback. All weather data flows through here."""

    def __init__(self):
        s = get_settings()
        self.client = httpx.AsyncClient(timeout=s.http_timeout_seconds)
        self.cache = TTLCache(s.cache_ttl_seconds)
        self.long_cache = TTLCache(24 * 3600, max_items=256)  # geocoding + history
        self.allow_fallback = s.allow_mock_fallback
        if s.weather_provider == "open-meteo":
            self.provider: WeatherProvider = OpenMeteoProvider(self.client)
            self.fallback: WeatherProvider | None = MockProvider()
        elif s.weather_provider == "mock":
            self.provider, self.fallback = MockProvider(), None
        else:
            raise ConfigurationError(f"Unknown WEATHER_PROVIDER '{s.weather_provider}'.")

    async def aclose(self) -> None:
        await self.client.aclose()

    @staticmethod
    def source(provider: WeatherProvider, fetched_at: str | None = None) -> DataSource:
        return DataSource(provider=provider.name, url=provider.url, is_mock=provider.is_mock,
                          fetched_at=fetched_at or _now())

    async def resolve(self, city: str | None = None, lat: float | None = None, lon: float | None = None) -> Location:
        if not city:
            return Location(name=f"{lat:.2f}, {lon:.2f}", latitude=lat, longitude=lon)
        key = f"geo:{city.strip().lower()}"
        if hit := self.long_cache.get(key):
            return hit
        try:
            loc = await self.provider.geocode(city.strip())
            self.long_cache.set(key, loc)
            return loc
        except ProviderUnavailable:
            if self.fallback and self.allow_fallback:
                try:
                    return await self.fallback.geocode(city.strip())
                except LocationNotFound:
                    pass
            raise

    async def _get(self, key: str, call, cache: TTLCache | None = None):
        """Returns (payload, provider, fetched_at). Live results are cached; fallback results are not."""
        cache = cache or self.cache
        if hit := cache.get(key):
            return hit
        try:
            payload = await call(self.provider)
            out = (payload, self.provider, _now())
            cache.set(key, out)
            return out
        except ProviderUnavailable as exc:
            if not (self.fallback and self.allow_fallback):
                raise
            log.warning("Live provider failed (%s); serving labelled mock data", exc.code)
            return (await call(self.fallback), self.fallback, _now())

    @staticmethod
    def _k(kind: str, loc: Location) -> str:
        return f"{kind}:{loc.latitude:.2f},{loc.longitude:.2f}"

    async def current(self, city=None, lat=None, lon=None) -> CurrentWeatherResponse:
        loc = await self.resolve(city, lat, lon)
        cur, prov, at = await self._get(self._k("cur", loc), lambda p: p.current(loc))
        return CurrentWeatherResponse(location=loc, current=cur, source=self.source(prov, at))

    async def forecast(self, city=None, lat=None, lon=None, loc: Location | None = None) -> ForecastResponse:
        loc = loc or await self.resolve(city, lat, lon)
        (hourly, daily), prov, at = await self._get(self._k("fc", loc), lambda p: p.forecast(loc))
        return ForecastResponse(location=loc, hourly=hourly, daily=daily, source=self.source(prov, at))

    async def bundle(self, city=None, lat=None, lon=None):
        """current + forecast for one location, fetched concurrently."""
        loc = await self.resolve(city, lat, lon)
        cur, fc = await asyncio.gather(self._cur_for(loc), self.forecast(loc=loc))
        return cur, fc

    async def _cur_for(self, loc: Location) -> CurrentWeatherResponse:
        cur, prov, at = await self._get(self._k("cur", loc), lambda p: p.current(loc))
        return CurrentWeatherResponse(location=loc, current=cur, source=self.source(prov, at))

    async def marine(self, city=None, lat=None, lon=None, loc: Location | None = None) -> MarineResponse:
        loc = loc or await self.resolve(city, lat, lon)
        pts, prov, at = await self._get(self._k("mar", loc), lambda p: p.marine(loc))
        return MarineResponse(location=loc, available=bool(pts), hourly=pts, source=self.source(prov, at))

    async def history(self, loc: Location, start: str, end: str, parameter: str):
        key = f"hist:{parameter}:{loc.latitude:.2f},{loc.longitude:.2f}:{start}:{end}"
        rows, prov, at = await self._get(key, lambda p: p.history(loc, start, end, parameter), self.long_cache)
        return rows, self.source(prov, at)


@lru_cache
def get_weather_service() -> WeatherService:
    return WeatherService()
