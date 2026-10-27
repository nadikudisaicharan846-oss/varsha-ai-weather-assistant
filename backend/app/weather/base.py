from abc import ABC, abstractmethod

from app.schemas.weather import CurrentWeather, DailyPoint, HourlyPoint, Location, MarinePoint


class WeatherProvider(ABC):
    """Every weather source implements this. Swap/add providers without touching services."""

    name: str
    url: str
    is_mock: bool = False

    @abstractmethod
    async def geocode(self, query: str) -> Location: ...

    @abstractmethod
    async def current(self, location: Location) -> CurrentWeather: ...

    @abstractmethod
    async def forecast(self, location: Location) -> tuple[list[HourlyPoint], list[DailyPoint]]: ...

    @abstractmethod
    async def marine(self, location: Location) -> list[MarinePoint]:
        """Empty list = no marine data for this location (e.g. inland)."""

    @abstractmethod
    async def history(
        self, location: Location, start: str, end: str, parameter: str
    ) -> list[tuple[str, float | None]]:
        """Daily (date, value) pairs. parameter: rainfall (mm/day) | temperature (°C mean) | humidity (% mean)."""
