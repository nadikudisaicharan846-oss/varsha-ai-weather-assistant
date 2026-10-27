import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import get_settings
from app.database import session as db
from app.exceptions import WeatherError
from app.services.weather_service import get_weather_service

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("varsha")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()  # optional: failure only disables saving features
    yield
    await get_weather_service().aclose()


app = FastAPI(title=f"{settings.app_name} API", version="1.0.0", lifespan=lifespan,
              description="Conversational weather & climate intelligence. Weather values always come from the data provider, never from the LLM.")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_methods=["GET", "POST", "DELETE"],
                   allow_headers=["Content-Type", "X-Client-Id"])


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


# --- simple per-IP sliding-window rate limit (use a gateway / Redis in multi-instance deployments) ---
_hits: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api") and path != "/api/health" and request.method != "OPTIONS":
        ip = request.client.host if request.client else "unknown"
        now, q = time.monotonic(), _hits[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= settings.rate_limit_per_minute:
            return _error(429, "too_many_requests", "You're sending requests too quickly. Please wait a moment and try again.")
        q.append(now)
        if len(_hits) > 5000:
            for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]:
                _hits.pop(k, None)
    return await call_next(request)


@app.exception_handler(WeatherError)
async def weather_error_handler(request: Request, exc: WeatherError):
    return _error(exc.status_code, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return _error(422, "invalid_input", "Please check what you entered and try again.")


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s", request.url.path)  # details stay in server logs only
    return _error(500, "internal_error", "Something went wrong on our side. Please try again.")


app.include_router(router)
