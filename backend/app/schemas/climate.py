from typing import Any

from pydantic import BaseModel

from app.schemas.weather import DataSource, Location


class SeriesPoint(BaseModel):
    label: str  # "2021" or "2021-07" or "7"
    value: float | None


class Trend(BaseModel):
    slope_per_decade: float
    r2: float
    n_years: int
    significant: bool  # 95% two-sided t-test on the slope
    direction: str  # increasing | decreasing | none
    line: list[SeriesPoint]  # fitted values per year, for charting


class ClimateReport(BaseModel):
    location: Location
    parameter: str  # rainfall | temperature | humidity
    unit: str
    aggregation: str  # "total" (yearly rainfall total) or "mean"
    start_year: int
    end_year: int
    yearly: list[SeriesPoint]
    monthly: list[SeriesPoint]  # every month in the period
    monthly_climatology: list[SeriesPoint]  # average per calendar month ("1".."12")
    year_to_year_change: list[SeriesPoint]  # change vs previous year (same unit)
    trend: Trend | None
    stats: dict[str, Any]  # observed summary values
    observed_text: str
    trend_text: str
    interpretation_text: str
    ai_interpretation: str | None = None
    caveats: list[str]
    language: str
    source: DataSource
