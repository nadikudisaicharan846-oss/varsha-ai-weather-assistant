from app.i18n.messages import t

_KEYS = {
    0: "clear", 1: "mostly_clear", 2: "partly_cloudy", 3: "overcast", 45: "fog", 48: "fog",
    51: "drizzle", 53: "drizzle", 55: "drizzle", 56: "drizzle", 57: "drizzle",
    61: "light_rain", 63: "rain", 65: "heavy_rain", 66: "freezing_rain", 67: "freezing_rain",
    71: "snow", 73: "snow", 75: "snow", 77: "snow", 80: "showers", 81: "showers", 82: "heavy_showers",
    85: "snow", 86: "snow", 95: "thunderstorm", 96: "thunderstorm_hail", 99: "thunderstorm_hail",
}


def condition_key(code: int) -> str:
    return _KEYS.get(code, "unknown")


def describe(code: int, lang: str = "en") -> str:
    return t(f"cond.{condition_key(code)}", lang)
