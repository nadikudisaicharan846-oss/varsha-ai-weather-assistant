class WeatherError(Exception):
    """Base error. `message` is always safe to show to end users."""

    status_code = 500
    code = "weather_error"
    message = "Something went wrong while fetching weather. Please try again."

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class LocationNotFound(WeatherError):
    status_code = 404
    code = "location_not_found"

    def __init__(self, query: str):
        self.query = query
        super().__init__(
            f"We couldn't find a place called “{query}”. Check the spelling or try a nearby city."
        )


class ProviderUnavailable(WeatherError):
    status_code = 502
    code = "provider_unavailable"
    message = "The weather service is not responding right now. Please try again shortly."


class RateLimited(ProviderUnavailable):
    status_code = 429
    code = "rate_limited"
    message = "The weather service is busy (rate limit reached). Please try again in a minute."


class ConfigurationError(WeatherError):
    status_code = 500
    code = "configuration_error"
    message = "The server is not configured correctly. Please contact the administrator."


class UnsupportedLanguage(WeatherError):
    status_code = 400
    code = "unsupported_language"
    message = "That language isn't supported yet. Supported: English (en), Telugu (te), Hindi (hi)."


class MissingHistoricalData(WeatherError):
    status_code = 404
    code = "missing_historical_data"
    message = "Not enough historical data is available for this place and period."


class AIUnavailable(WeatherError):
    status_code = 502
    code = "ai_unavailable"
    message = "The AI service is not responding right now."


class StorageUnavailable(WeatherError):
    status_code = 503
    code = "storage_unavailable"
    message = "Saving is unavailable right now (database not reachable). Weather features still work."


class BadRequest(WeatherError):
    status_code = 400
    code = "bad_request"


class VoiceNotConfigured(WeatherError):
    status_code = 501
    code = "voice_not_configured"
    message = "Server-side speech isn't configured. Your browser's built-in speech features are used instead."
