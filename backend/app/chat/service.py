import json
import logging
import re
from datetime import date as _date

from app.ai.service import get_ai
from app.alerts.engine import fmt_date
from app.alerts.service import build_alerts
from app.chat import nlu
from app.chat.sessions import Session, SessionStore
from app.climate.service import climate_report
from app.decision.advisor import SECTORS, DecisionService, day_label, window
from app.exceptions import (AIUnavailable, LocationNotFound, MissingHistoricalData, UnsupportedLanguage)
from app.i18n.messages import LANGS, M, t
from app.schemas.chat import Card, ChatRequest, ChatResponse
from app.services.weather_service import WeatherService

log = logging.getLogger("varsha.chat")

INTERPRETIVE = {"rain", "travel", "safety_advice", "alerts", "climate_trend", *SECTORS}
PERSONA = {"agriculture": "a farmer (non-expert, practical advice)", "disaster": "a disaster-management officer",
           "aviation": "an aviation operations planner (informational only)", "marine": "a fisherman / marine operator",
           "urban": "an urban planner or researcher", "climate_trend": "a researcher; separate observed data from interpretation"}
ALLOWED_INTENTS = {"weather", "rain", "temperature", "wind", "humidity", "forecast_range", "alerts", "travel",
                   "safety_advice", "climate_trend", *SECTORS}
STATUS_ICON = {"good": "🟢", "caution": "🟡", "avoid": "🔴", "info": "⚪", "na": "⚪"}


def _numbers_ok(reply: str, allowed: str) -> bool:
    """Guard against hallucinated figures: every ASCII number >31 in the LLM reply must appear in the facts."""
    ok = set(re.findall(r"\d+(?:\.\d+)?", allowed))
    return all(float(n) <= 31 or n in ok for n in re.findall(r"\d+(?:\.\d+)?", reply))


class ChatService:
    def __init__(self, ws: WeatherService, decision: DecisionService, default_city: str):
        self.ws, self.decision, self.default_city = ws, decision, default_city
        self.sessions = SessionStore()

    # ------------------------------------------------------------------ main entry
    async def handle(self, req: ChatRequest) -> ChatResponse:
        ui_lang = req.language if req.language in LANGS else None
        if not ui_lang:
            raise UnsupportedLanguage()
        sess = self.sessions.get(req.session_id)
        ai = get_ai()

        p = nlu.parse(req.message)
        nlu_mode = "rules"
        if ai and (p.needs_llm or (not p.intent_matched and not (sess.intent and p.is_followup))):
            try:
                if d := await ai.parse_query(req.message, {"last_intent": sess.intent,
                                                          "last_location": sess.location.name if sess.location else None}):
                    self._merge_llm(p, d)
                    nlu_mode = "llm+rules"
            except AIUnavailable:
                pass

        lang = p.reply_lang if p.reply_lang in LANGS else ui_lang
        intent = p.intent if p.intent_matched else (sess.intent or p.intent)
        if p.explain_request and sess.intent and not p.intent_matched:
            intent = sess.intent

        # --- location: message > session > UI hint > default ---
        hint = req.location
        hint_key = (hint.city or f"{hint.lat},{hint.lon}") if hint else None
        if hint_key != sess.hint_key:
            sess.hint_key, sess.location = hint_key, None
        loc, query = None, p.location_query
        try:
            if query:
                loc = await self.ws.resolve(city=query)
            elif sess.location:
                loc = sess.location
            elif hint and hint.city:
                loc = await self.ws.resolve(city=hint.city)
            elif hint and hint.lat is not None and hint.lon is not None:
                loc = await self.ws.resolve(lat=hint.lat, lon=hint.lon)
            else:
                loc = await self.ws.resolve(city=self.default_city)
        except LocationNotFound as e:
            return self._simple(sess, req, intent, lang, t("reply.not_found", lang, query=e.query), p, nlu_mode)

        # --- dates ---
        if p.date_start is not None:
            ds, de = p.date_start, p.date_end
        elif p.is_followup and sess.date and intent == (sess.intent or intent):
            ds, de = sess.date
        else:
            ds, de = 0, 0

        try:
            result = await self._answer(intent, loc, ds, de, p, sess, lang, req.message)
        except MissingHistoricalData as e:
            return self._simple(sess, req, intent, lang, e.message, p, nlu_mode, loc)
        reply, facts, cards, sources, loc, ds, de = result

        # --- optional LLM explanation (never for simple data lookups) ---
        ai_mode = "rule_based"
        if ai and intent in INTERPRETIVE:
            try:
                persona = PERSONA.get(intent, "the general public")
                llm_reply = await ai.compose_reply(req.message, facts, reply, lang, persona, sess.turns)
                if llm_reply and _numbers_ok(llm_reply, json.dumps(facts, ensure_ascii=False) + reply):
                    reply, ai_mode = llm_reply, "llm"
                else:
                    ai_mode = "llm_error_fallback"
                    reply += "\n\n" + t("reply.ai_note", lang)
            except AIUnavailable:
                ai_mode = "llm_error_fallback"
                reply += "\n\n" + t("reply.ai_note", lang)
        if any(s.is_mock for s in sources):
            reply = t("reply.mock_note", lang) + "\n\n" + reply

        sess.location, sess.intent, sess.date = loc, intent, (ds, de)
        if p.parameter:
            sess.parameter = p.parameter
        self.sessions.remember(sess, req.message, reply)
        return ChatResponse(
            session_id=sess.id, reply=reply, language=lang, intent=intent, location=loc,
            date_label=self._range_label(ds, de, lang, facts), cards=cards, sources=sources, ai_mode=ai_mode,
            parsed={"intent": intent, "location_query": query, "date": [ds, de], "parameter": p.parameter,
                    "nlu": nlu_mode}, disclaimer=t("disclaimer.general", lang))

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _merge_llm(p: nlu.Parsed, d: dict):
        if d.get("intent") in ALLOWED_INTENTS:
            p.intent, p.intent_matched = d["intent"], True
        if d.get("location") and not p.location_query:
            p.location_query = str(d["location"])[:80]
        if p.date_start is None and isinstance(d.get("date_start"), int):
            p.date_start = max(0, min(6, d["date_start"]))
            p.date_end = max(p.date_start, min(6, d["date_end"])) if isinstance(d.get("date_end"), int) else p.date_start
        if d.get("parameter") in ("rainfall", "temperature", "humidity") and not p.parameter:
            p.parameter = d["parameter"]
        if isinstance(d.get("years"), int) and not p.years:
            p.years = max(3, min(30, d["years"]))
        if d.get("reply_language") in LANGS and not p.reply_lang:
            p.reply_lang = d["reply_language"]

    def _simple(self, sess: Session, req, intent, lang, text, p, nlu_mode, loc=None) -> ChatResponse:
        self.sessions.remember(sess, req.message, text)
        return ChatResponse(session_id=sess.id, reply=text, language=lang, intent=intent, location=loc, cards=[],
                            sources=[], ai_mode="rule_based", parsed={"intent": intent, "nlu": nlu_mode},
                            disclaimer=t("disclaimer.general", lang))

    @staticmethod
    def _range_label(ds, de, lang, facts) -> str | None:
        return facts.get("period")

    def _day(self, fc, cur, off, lang) -> dict:
        d = fc.daily[off]
        w = window(fc, off)
        hum = w["hum"] if w["hum"] is not None else (cur.current.humidity_pct if off == 0 else None)
        return {"date": d.date, "label": day_label(off, fc, lang), "condition": t(f"cond.{d.condition_key}", lang),
                "tmin": round(d.temp_min_c) if d.temp_min_c is not None else None,
                "tmax": round(d.temp_max_c) if d.temp_max_c is not None else None,
                "prob": d.rain_probability_pct or 0, "mm": round(d.precipitation_sum_mm, 1),
                "wind": round(d.wind_max_kmh or 0), "gust": round(d.wind_gusts_max_kmh or 0), "hum": hum,
                "thunder": w["thunder"]}

    @staticmethod
    def _rain_timing(fc, date, lang) -> str:
        wet = [h.time[11:16] for h in fc.hourly if h.time[:10] == date and h.precipitation_mm >= 0.5]
        return t("reply.rain.timing", lang, start=wet[0], end=wet[-1]) if wet else ""

    # ------------------------------------------------------------------ intents
    async def _answer(self, intent, loc, ds, de, p, sess, lang, question):
        if intent == "climate_trend":
            return await self._climate(loc, p, sess, lang)

        cur, fc = await self.decision._bundle(loc)
        n = len(fc.daily)
        ds, de = min(ds, n - 1), min(max(de, ds), n - 1)
        place = loc.name
        sources = [cur.source] if cur.source.fetched_at != fc.source.fetched_at or cur.source.is_mock != fc.source.is_mock else []
        sources = [fc.source, *sources]
        cards: list[Card] = []
        single = ds == de
        days = [self._day(fc, cur, i, lang) for i in range(ds, de + 1)]
        dfacts = days[0]
        period = dfacts["label"] if single else f"{fmt_date(fc.daily[ds].date)}–{fmt_date(fc.daily[de].date)}"
        facts: dict = {"place": place, "period": period, "days": days}
        c = cur.current

        def day_cards(hourly=False):
            if ds == 0:
                cards.append(Card(type="current", data=cur.model_dump()))
            cards.append(Card(type="daily", data=[fc.daily[i].model_dump() for i in range(ds, de + 1)]))
            if hourly and single:
                cards.append(Card(type="hourly", data=[h.model_dump() for h in fc.hourly if h.time[:10] == fc.daily[ds].date]
                                  or [h.model_dump() for h in fc.hourly[:24]]))

        def lines():
            return t("reply.week.intro", lang, place=place) + "\n" + "\n".join(
                "• " + t("line.day", lang, date=fmt_date(d["date"]), condition=d["condition"], tmin=d["tmin"],
                         tmax=d["tmax"], prob=d["prob"]) for d in days)

        if intent == "alerts":
            alerts = build_alerts(fc, lang)
            facts["alerts"] = [{"type": a.type, "level": a.level_label, "summary": a.summary} for a in alerts]
            body = t("reply.alerts.intro", lang, place=place) + "\n" + (
                "\n".join(f"{a.icon} {a.level_label}: {a.title} — {a.summary}" for a in alerts)
                if alerts else t("alerts.none", lang, place=place))
            body += "\n\n" + t("alert.limits", lang)
            cards.append(Card(type="alerts", data=[a.model_dump() for a in alerts]))
            return body, facts, cards, sources, loc, ds, de

        if intent == "safety_advice":
            topic = p.topic if p.topic in ("heat", "rain", "thunderstorm", "wind") else "heat"
            atype = "heat" if topic == "heat" else topic
            advice = [t(f"alert.{atype}.a{i}", lang) for i in (1, 2, 3) if f"alert.{atype}.a{i}" in M]
            alerts = [a for a in build_alerts(fc, lang) if a.type == atype]
            body = t("reply.safety.intro", lang, topic=t(f"topic.{topic}", lang), place=place) + "\n" + "\n".join("• " + a for a in advice)
            if alerts:
                body += "\n\n" + t("reply.safety.active", lang, title=f"{alerts[0].level_label} – {alerts[0].title}")
                cards.append(Card(type="alerts", data=[a.model_dump() for a in alerts]))
            facts.update({"topic": topic, "advice": advice, "active": [a.summary for a in alerts]})
            return body, facts, cards, sources, loc, ds, de

        if intent in SECTORS:
            rep = await getattr(self.decision, f"_{intent}")(loc, cur, fc, ds, lang)
            body = f"{rep.headline}\n" + "\n".join(f"{STATUS_ICON[c_.status]} {c_.label}: {c_.value}" for c_ in rep.checks)
            body += "\n\n" + "\n".join("• " + r for r in rep.recommendations) + "\n\n" + rep.disclaimer
            facts.update({"sector": intent, "verdict": rep.verdict, "headline": rep.headline,
                          "checks": [{"label": c_.label, "value": c_.value, "status": c_.status} for c_ in rep.checks],
                          "recommendations": rep.recommendations, "alerts": rep.alerts_summary})
            cards.append(Card(type="decision", data=rep.model_dump()))
            return body, facts, cards, sources, loc, ds, de

        # ---- plain weather intents ----
        d = dfacts
        if intent == "forecast_range" or (not single and intent in ("weather", "rain", "temperature", "wind", "humidity", "travel")):
            body = lines()
            day_cards()
        elif intent == "rain":
            lvl = "likely" if (d["prob"] >= 60 or d["mm"] >= 5) else "possible" if (d["prob"] >= 30 or d["mm"] >= 1) else "unlikely"
            body = t(f"reply.rain.{lvl}", lang, day=d["label"], place=place, prob=d["prob"], mm=d["mm"])
            if lvl != "unlikely":
                tm = self._rain_timing(fc, d["date"], lang)
                body += (" " + tm) if tm else ""
            body += " " + t({"likely": "reply.umbrella.yes", "possible": "reply.umbrella.maybe", "unlikely": "reply.umbrella.no"}[lvl], lang)
            facts["rain_level"] = lvl
            day_cards(hourly=True)
        elif intent == "temperature":
            if ds == 0:
                body = t("reply.temp.now", lang, place=place, temp=round(c.temperature_c), feels=round(c.feels_like_c), tmin=d["tmin"], tmax=d["tmax"])
            else:
                body = t("reply.temp.day", lang, day=d["label"], place=place, tmin=d["tmin"], tmax=d["tmax"])
            day_cards()
        elif intent == "wind":
            body = t("reply.wind", lang, day=d["label"], place=place, wind=d["wind"], gust=d["gust"])
            day_cards()
        elif intent == "humidity":
            body = t("reply.humidity", lang, day=d["label"], place=place, hum=d["hum"] if d["hum"] is not None else "–")
            day_cards()
        elif intent == "travel":
            w = window(fc, ds)
            alerts = [a for a in build_alerts(fc, lang) if a.date == fc.daily[ds].date]
            reasons, level = [], 0
            if w["prob"] >= 60 and w["mm"] >= 5:
                reasons.append(t("reason.rain", lang, prob=w["prob"], mm=w["mm"])); level = max(level, 1)
            if (w["mm"] or 0) >= 50:
                level = 2
            if (w["gust"] or 0) >= 45:
                reasons.append(t("reason.wind", lang, gust=round(w["gust"]))); level = max(level, 2 if w["gust"] >= 70 else 1)
            if (w["temp"] or 0) >= 40:
                reasons.append(t("reason.heat", lang, temp=round(w["temp"]))); level = max(level, 2 if w["temp"] >= 45 else 1)
            if w["thunder"]:
                reasons.append(t("reason.thunder", lang)); level = max(level, 1)
            if w["vis"] is not None and w["vis"] < 2:
                reasons.append(t("reason.fog", lang, vis=w["vis"])); level = max(level, 1)
            for a in alerts:
                if a.level_rank >= 2:
                    reasons.append(t("reason.alert", lang, title=a.title)); level = max(level, 2 if a.level_rank >= 3 else 1)
            key = ["ok", "caution", "avoid"][level]
            body = t(f"reply.travel.{key}", lang, day=d["label"], place=place, reasons="; ".join(dict.fromkeys(reasons)))
            facts.update({"travel": key, "reasons": reasons})
            day_cards(hourly=True)
            if alerts:
                cards.append(Card(type="alerts", data=[a.model_dump() for a in alerts]))
        else:  # general weather
            body = (t("reply.now", lang, place=place, condition=t(f"cond.{c.condition_key}", lang), temp=round(c.temperature_c),
                      feels=round(c.feels_like_c), hum=c.humidity_pct, wind=round(c.wind_speed_kmh)) + "\n"
                    if ds == 0 else "")
            body += t("reply.day", lang, day=d["label"], place=place, condition=d["condition"], tmin=d["tmin"], tmax=d["tmax"],
                      prob=d["prob"], mm=d["mm"], wind=d["wind"])
            if ds == 0:
                facts["now"] = {"temp": round(c.temperature_c), "feels": round(c.feels_like_c), "humidity": c.humidity_pct,
                                "wind": round(c.wind_speed_kmh)}
            day_cards()
        return body, facts, cards, sources, loc, ds, de

    async def _climate(self, loc, p, sess, lang):
        parameter = p.parameter or sess.parameter or "rainfall"
        years = p.years or 10
        rep = await climate_report(self.ws, loc, parameter, years, lang)
        body = "\n".join([
            t("reply.climate.intro", lang, place=loc.name, param=t(f"param.{parameter}", lang), y1=rep.start_year, y2=rep.end_year),
            "• " + rep.observed_text, *(["• " + rep.trend_text] if rep.trend_text else []),
            "• " + rep.interpretation_text, "", "ⓘ " + " ".join(rep.caveats)])
        facts = {"place": loc.name, "period": f"{rep.start_year}–{rep.end_year}", "parameter": parameter, "unit": rep.unit,
                 "stats": rep.stats, "trend": rep.trend.model_dump(exclude={"line"}) if rep.trend else None}
        sess.parameter = parameter
        return body, facts, [Card(type="climate", data=rep.model_dump())], [rep.source], loc, 0, 0
