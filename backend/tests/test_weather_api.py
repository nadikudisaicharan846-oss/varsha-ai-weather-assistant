import os

os.environ["WEATHER_PROVIDER"] = "mock"  # tests never hit the network
os.environ["DATABASE_URL"] = "sqlite:///./test_varsha.db"
os.environ["RATE_LIMIT_PER_MINUTE"] = "100000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

CID = {"X-Client-Id": "test-client-0001"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def chat(client, msg, **kw):
    body = {"message": msg, "language": kw.pop("language", "en"), **kw}
    r = client.post("/api/chat", json=body, headers=CID)
    assert r.status_code == 200, r.text
    return r.json()


def test_health(client):
    j = client.get("/api/health").json()
    assert j["status"] == "ok" and j["ai"]["enabled"] is False


def test_current_forecast_alerts(client):
    cur = client.get("/api/weather/current", params={"city": "Hyderabad"}).json()
    assert cur["source"]["is_mock"] is True and "temperature_c" in cur["current"]
    fc = client.get("/api/weather/forecast", params={"city": "Hyderabad"}).json()
    assert len(fc["hourly"]) == 72 and len(fc["daily"]) == 7
    al = client.get("/api/alerts", params={"city": "Hyderabad", "lang": "hi"}, headers=CID).json()
    assert al["alerts"] and al["disclaimer"] and al["limitations"]
    assert {a["level"] for a in al["alerts"]} <= {"information", "advisory", "warning", "severe_warning"}
    assert client.get("/api/alerts/thresholds").json()["rain"]["warning_mm"] == 64.5
    assert client.get("/api/alerts/history", headers=CID).status_code == 200


def test_errors_are_friendly(client):
    assert client.get("/api/weather/current", params={"city": "Nowhereville"}).json()["error"]["code"] == "location_not_found"
    assert client.get("/api/weather/current").status_code == 400
    assert client.get("/api/weather/current", params={"lat": 999, "lon": 0}).status_code == 422
    assert client.get("/api/alerts", params={"city": "Hyderabad", "lang": "xx"}).json()["error"]["code"] == "unsupported_language"
    assert client.get("/api/decision/nope", params={"city": "Hyderabad"}).status_code == 400
    assert client.post("/api/voice/speak", json={"text": "hi"}).status_code == 501


def test_climate(client):
    r = client.get("/api/climate/history", params={"city": "Telangana", "parameter": "rainfall", "years": 10}).json()
    assert len(r["yearly"]) == 10 and r["trend"] and len(r["monthly_climatology"]) == 12
    assert any("region" in c for c in r["caveats"])
    assert client.get("/api/climate/history", params={"city": "Hyderabad", "parameter": "wind"}).status_code == 422


def test_decision_all_sectors(client):
    for s in ["agriculture", "disaster", "aviation", "marine", "urban"]:
        j = client.get(f"/api/decision/{s}", params={"city": "Mumbai", "day": 1, "lang": "te"}).json()
        assert j["verdict"] in ("good", "caution", "avoid") and j["checks"] and j["disclaimer"]


def test_scenario_general_weather(client):
    j = chat(client, "What is the weather in Hyderabad today?")
    assert j["intent"] == "weather" and j["location"]["name"] == "Hyderabad"
    assert {c["type"] for c in j["cards"]} >= {"current", "daily"} and j["sources"][0]["is_mock"]


def test_scenario_rain_and_context_followups(client):
    a = chat(client, "Will it rain tomorrow?", location={"city": "Hyderabad"})
    assert a["intent"] == "rain" and "umbrella" in a["reply"].lower() or "rain" in a["reply"].lower()
    sid = a["session_id"]
    b = chat(client, "What about the day after?", session_id=sid, location={"city": "Hyderabad"})
    assert b["intent"] == "rain" and b["parsed"]["date"] == [2, 2] and b["location"]["name"] == "Hyderabad"
    c = chat(client, "What about Mumbai?", session_id=sid, location={"city": "Hyderabad"})
    assert c["location"]["name"] == "Mumbai" and c["intent"] == "rain" and c["parsed"]["date"] == [2, 2]


def test_scenario_alerts_and_safety(client):
    j = chat(client, "Are there any weather warnings?", location={"city": "Hyderabad"})
    assert j["intent"] == "alerts" and any(c["type"] == "alerts" for c in j["cards"])
    s = chat(client, "What precautions should people take during a heatwave?")
    assert s["intent"] == "safety_advice" and "•" in s["reply"]


def test_scenario_telugu_and_hindi(client):
    j = chat(client, "రేపు హైదరాబాద్‌లో వర్షం పడుతుందా?")
    assert j["language"] == "te" and j["intent"] == "rain" and j["location"]["name"] == "Hyderabad"
    assert "వర్షం" in j["reply"] and j["parsed"]["date"] == [1, 1]
    h = chat(client, "कल मुंबई में बारिश होगी?")
    assert h["language"] == "hi" and h["location"]["name"] == "Mumbai"
    e = chat(client, "Explain this in Telugu", session_id=j["session_id"])
    assert e["language"] == "te" and e["intent"] == "rain"


def test_scenario_agriculture_and_sectors(client):
    j = chat(client, "Is tomorrow suitable for spraying pesticides?", location={"city": "Warangal"})
    assert j["intent"] == "agriculture" and any(c["type"] == "decision" for c in j["cards"])
    assert chat(client, "forecast for fishermen in Mumbai")["intent"] == "marine"
    assert chat(client, "Is it safe to travel today?", location={"city": "Delhi"})["intent"] == "travel"
    assert chat(client, "Temperature in Hyderabad?")["intent"] == "temperature"


def test_scenario_climate(client):
    j = chat(client, "Show rainfall trends in Telangana.")
    assert j["intent"] == "climate_trend" and j["location"]["name"] == "Telangana"
    card = [c for c in j["cards"] if c["type"] == "climate"][0]["data"]
    assert card["parameter"] == "rainfall" and card["trend"]
    k = chat(client, "Has rainfall increased in this region over the last 10 years?", location={"city": "Hyderabad"})
    assert k["intent"] == "climate_trend" and k["parsed"]["parameter"] == "rainfall"


def test_chat_validation_and_language(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "hi", "language": "xx"}).json()["error"]["code"] == "unsupported_language"
    j = chat(client, "weather in Nowhereville")
    assert "Nowhereville" in j["reply"]


def test_saved_data_roundtrip(client):
    r = client.post("/api/locations", json={"name": "Hyderabad", "admin1": "Telangana", "latitude": 17.38, "longitude": 78.48}, headers=CID)
    assert r.status_code == 200
    lid = r.json()["id"]
    assert any(x["id"] == lid for x in client.get("/api/locations", headers=CID).json())
    client.post("/api/analyses", json={"title": "t", "location": "Hyderabad", "parameter": "rainfall", "years": 10, "summary": {"a": 1}}, headers=CID)
    assert client.get("/api/analyses", headers=CID).json()[0]["summary"] == {"a": 1}
    assert client.get("/api/history/conversations", headers=CID).json()
    assert client.delete(f"/api/locations/{lid}", headers=CID).json()["deleted"] is True
    assert client.get("/api/locations").status_code == 400


def test_fallback_to_labelled_mock_when_live_provider_down():
    import asyncio

    from app.exceptions import ProviderUnavailable
    from app.services.weather_service import WeatherService
    from app.weather.mock import MockProvider

    class Down(MockProvider):
        is_mock = False

        async def current(self, loc):
            raise ProviderUnavailable()

    svc = WeatherService()
    svc.provider, svc.fallback, svc.allow_fallback = Down(), MockProvider(), True
    assert asyncio.run(svc.current(city="Hyderabad")).source.is_mock is True
    svc.allow_fallback = False
    with pytest.raises(ProviderUnavailable):
        asyncio.run(svc.current(city="Mumbai"))


def test_numbers_guard():
    from app.chat.service import _numbers_ok
    assert _numbers_ok("Expect about 52 mm", "mm 52") and not _numbers_ok("Expect about 90 mm", "mm 52")


def test_rate_limit():
    from app.config import get_settings
    import app.main as m
    old = get_settings().rate_limit_per_minute
    m.settings.rate_limit_per_minute = 2
    m._hits.clear()
    with TestClient(app) as c:
        codes = [c.get("/api/weather/current", params={"city": "Delhi"}).status_code for _ in range(4)]
    m.settings.rate_limit_per_minute = old
    m._hits.clear()
    assert 429 in codes


def test_llm_path_with_fake_provider(client, monkeypatch):
    import app.chat.service as cs

    class Fake:
        mode = "good"

        async def parse_query(self, m, ctx):
            return {"intent": "rain", "location": "Delhi", "date_start": 1, "date_end": 1, "reply_language": "en"}

        async def compose_reply(self, q, facts, baseline, lang, persona, hist):
            if Fake.mode == "bad":
                return "It will pour 999 mm tomorrow!"
            return "Tomorrow looks wet; carry an umbrella and avoid low-lying roads."

    monkeypatch.setattr(cs, "get_ai", lambda: Fake())
    ok = chat(client, "Will it rain tomorrow in Hyderabad?")
    assert ok["ai_mode"] == "llm" and "wet" in ok["reply"]
    Fake.mode = "bad"
    bad = chat(client, "Will it rain tomorrow in Hyderabad?")
    assert bad["ai_mode"] == "llm_error_fallback" and "999" not in bad["reply"]
    Fake.mode = "good"
    unk = chat(client, "qwerty zzz in Delhi")  # unknown intent -> LLM parser decides
    assert unk["parsed"]["nlu"] == "llm+rules" and unk["intent"] == "rain"
