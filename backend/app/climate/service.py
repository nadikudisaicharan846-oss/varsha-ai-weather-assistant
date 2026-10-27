from app.climate.analysis import analyze, period
from app.schemas.climate import ClimateReport
from app.schemas.weather import Location
from app.services.weather_service import WeatherService


async def climate_report(ws: WeatherService, loc: Location, parameter: str, years: int, lang: str) -> ClimateReport:
    y0, y1 = period(years)
    rows, src = await ws.history(loc, f"{y0}-01-01", f"{y1}-12-31", parameter)
    return analyze(loc, parameter, rows, years, src, lang)
