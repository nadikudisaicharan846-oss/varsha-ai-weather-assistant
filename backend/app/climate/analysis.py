import math
from collections import defaultdict
from datetime import date

from app.exceptions import MissingHistoricalData
from app.i18n.messages import t
from app.schemas.climate import ClimateReport, SeriesPoint, Trend
from app.schemas.weather import DataSource, Location

PARAMS = {"rainfall": ("mm", "total"), "temperature": ("°C", "mean"), "humidity": ("%", "mean")}
_T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23,
        12: 2.18, 15: 2.13, 20: 2.09, 30: 2.04}


def _t_crit(df: int) -> float:
    ks = [k for k in _T95 if k <= df]
    return _T95[max(ks)] if ks else 12.71 if df < 1 else 1.96


def period(years: int, today: date | None = None) -> tuple[int, int]:
    today = today or date.today()
    end = today.year - 1  # only complete calendar years
    return end - years + 1, end


def _ols(xs: list[float], ys: list[float]):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx if sxx else 0.0
    r2 = (sxy * sxy) / (sxx * syy) if sxx and syy else 0.0
    return slope, my - slope * mx, r2


def analyze(loc: Location, parameter: str, rows: list[tuple[str, float | None]], years: int,
            source: DataSource, lang: str) -> ClimateReport:
    unit, agg = PARAMS[parameter]
    y0, y1 = period(years)
    by_year: dict[int, list[float]] = defaultdict(list)
    by_ym: dict[tuple[int, int], list[float]] = defaultdict(list)
    for day, v in rows:
        if v is None:
            continue
        y, mo = int(day[:4]), int(day[5:7])
        by_year[y].append(v)
        by_ym[(y, mo)].append(v)

    agg_fn = (lambda v: sum(v)) if agg == "total" else (lambda v: sum(v) / len(v))
    nd = 0 if parameter == "rainfall" else 1
    yearly: dict[int, float] = {}
    for y in range(y0, y1 + 1):
        days = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
        if len(by_year.get(y, [])) >= 0.9 * days:  # require near-complete years
            yearly[y] = agg_fn(by_year[y])
    if len(yearly) < 3:
        raise MissingHistoricalData()

    monthly = [SeriesPoint(label=f"{y}-{mo:02d}", value=round(agg_fn(v), 1))
               for (y, mo), v in sorted(by_ym.items()) if y0 <= y <= y1]
    clim = []
    for mo in range(1, 13):
        vals = [agg_fn(v) for (y, m_), v in by_ym.items() if m_ == mo and y in yearly]
        clim.append(SeriesPoint(label=str(mo), value=round(sum(vals) / len(vals), 1) if vals else None))

    ys = sorted(yearly)
    yoy = [SeriesPoint(label=str(y), value=round(yearly[y] - yearly[p], 1)) for p, y in zip(ys, ys[1:])]

    trend = None
    if len(ys) >= 5:
        slope, icpt, r2 = _ols([float(y) for y in ys], [yearly[y] for y in ys])
        n = len(ys)
        tstat = math.sqrt(r2 * (n - 2) / (1 - r2)) if r2 < 1 else 99.0
        sig = tstat > _t_crit(n - 2)
        direction = ("increasing" if slope > 0 else "decreasing") if sig else "none"
        trend = Trend(slope_per_decade=round(slope * 10, 2), r2=round(r2, 2), n_years=n, significant=sig,
                      direction=direction, line=[SeriesPoint(label=str(y), value=round(icpt + slope * y, 2)) for y in ys])

    vals = list(yearly.values())
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1))
    ymax, ymin = max(yearly, key=yearly.get), min(yearly, key=yearly.get)
    stats: dict = {"yearly_mean": round(mean, nd), "yearly_std": round(std, nd),
                   "max_year": ymax, "max_value": round(yearly[ymax], nd),
                   "min_year": ymin, "min_value": round(yearly[ymin], nd), "years_used": len(ys)}
    if parameter == "rainfall":
        shares = []
        for y in ys:
            tot = yearly[y]
            mon = sum(sum(v) for (yy, mo), v in by_ym.items() if yy == y and 6 <= mo <= 9)
            if tot > 0:
                shares.append(100 * mon / tot)
        if shares:
            stats["monsoon_share_pct"] = round(sum(shares) / len(shares), 0)
    else:
        cv = [(p.value, p.label) for p in clim if p.value is not None]
        if cv:
            stats["peak_month"] = int(max(cv)[1])
            stats["lowest_month"] = int(min(cv)[1])

    observed = t("climate.observed", lang, param=t(f"param.{parameter}", lang), agg=t(f"agg.{agg}", lang), mean=round(mean, nd), unit=unit,
                 maxyear=ymax, maxval=round(yearly[ymax], nd), minyear=ymin, minval=round(yearly[ymin], nd))
    if trend:
        dkey = {"increasing": "up", "decreasing": "down", "none": "none"}[trend.direction]
        sig_txt = t("climate.sig.yes" if trend.significant else "climate.sig.no", lang)
        trend_text = t(f"climate.trend.{dkey}", lang, slope=abs(trend.slope_per_decade), unit=unit,
                       r2=trend.r2, n=trend.n_years, sig=sig_txt)
        interp = t(f"climate.interp.{dkey}", lang)
    else:
        trend_text, interp = "", t("climate.interp.none", lang)

    caveats = [t("climate.caveat.mock" if source.is_mock else "climate.caveat.era5", lang)]
    if loc.is_region:
        caveats.append(t("climate.caveat.region", lang))

    return ClimateReport(
        location=loc, parameter=parameter, unit=unit, aggregation=agg, start_year=y0, end_year=y1,
        yearly=[SeriesPoint(label=str(y), value=round(yearly[y], nd)) for y in ys], monthly=monthly,
        monthly_climatology=clim, year_to_year_change=yoy, trend=trend, stats=stats,
        observed_text=observed, trend_text=trend_text, interpretation_text=interp, caveats=caveats,
        language=lang, source=source)
