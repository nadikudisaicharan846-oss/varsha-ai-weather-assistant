"""Rule-based natural-language understanding (English / Telugu / Hindi). Always available; an LLM parser
is used on top only when the rules cannot decide (unknown intent or an unsupported language)."""
import re
from dataclasses import dataclass, field
from datetime import date

from app.chat.gazetteer import ALIASES

TE = re.compile(r"[\u0C00-\u0C7F]")
HI = re.compile(r"[\u0900-\u097F]")
OTHER_INDIC = re.compile(r"[\u0B80-\u0BFF\u0C80-\u0CFF\u0D00-\u0D7F\u0980-\u09FF\u0A80-\u0AFF\u0A00-\u0A7F\u0B00-\u0B7F]")

INTENTS: list[tuple[str, list[str]]] = [  # ordered by priority
    ("climate_trend", ["trend", "historical", "history", "over the years", "increased", "decreased", "climatolog",
                       "ట్రెండ్", "ధోరణి", "గత ", "रुझान", "इतिहास", "पिछले"]),
    ("agriculture", ["farm", "crop", "pesticide", "spray", "irrigat", "sowing", "harvest", "fertili", "agricultur",
                     "రైతు", "పంట", "పురుగుమందు", "పిచికారీ", "వ్యవసాయ", "किसान", "फसल", "कीटनाशक", "छिड़काव", "खेती", "सिंचाई"]),
    ("marine", ["fisher", "marine", "boat", "ocean", " wave", "sailing", "at sea", " sea ", "మత్స్య", "చేపల", "సముద్ర",
                "मछुआर", "मछली", "समुद्र", "नाव"]),
    ("aviation", ["flight", "aviation", "aircraft", "airport", "pilot", "take off", "takeoff", "landing", "drone",
                  "విమాన", "ఎయిర్‌పోర్ట్", "उड़ान", "विमान", "हवाई"]),
    ("urban", ["urban", "city planning", "town planning", "drainage", "infrastructure", "smart city", "పట్టణ ప్రణాళిక", "शहरी"]),
    ("disaster", ["disaster", "evacuat", "preparedness", "relief", "ndrf", "affected area", "విపత్తు", "आपदा"]),
    ("travel", ["travel", " trip", "journey", " drive", "commut", "safe to go", "ప్రయాణ", "यात्रा", "सफर"]),
    ("safety_advice", ["precaution", "safety", "tips", "stay safe", "what should", "జాగ్రత్తలు", "सावधानी", "सुरक्षा", "बचाव"]),
    ("alerts", ["warning", "alert", "advisory", "cyclone", "extreme", "severe", "danger", "hazard", "flood",
                "హెచ్చరిక", "వరద", "चेतावनी", "अलर्ट", "खतरा", "बाढ़"]),
    ("rain", [" rain", "umbrella", "shower", "drizzle", "precipitation", "monsoon", "వర్ష", "గొడుగు", "बारिश", "बरसात", "छाता", "वर्षा"]),
    ("temperature", ["temperature", "how hot", "how cold", " hot ", " cold", " warm", " heat", "ఉష్ణోగ్రత", "వేడి", "తాపం", "तापमान", "गर्मी", "ठंड"]),
    ("wind", [" wind", "breeze", " gust", "గాలి", "हवा"]),
    ("humidity", ["humid", "తేమ", "नमी", "आर्द्रता"]),
    ("forecast_range", ["forecast", "weekend", "this week", "next week", "next 7", "next few days", "వారాంతం", "వారం", "సూచన",
                        "पूर्वानुमान", "सप्ताह", "हफ्ते", "वीकेंड"]),
    ("weather", ["weather", "climate", "వాతావరణ", "मौसम"]),
]
HAZARD_TOPICS = {"heat": [" heat", "హీట్", "వడగాల్పు", "వేడి", "लू", "गर्मी", "तापमान"],
                 "rain": [" rain", " flood", "వర్ష", "వరద", "बारिश", "बाढ़"],
                 "thunderstorm": [" thunder", "lightning", " storm", "ఉరుము", "మెరుపు", "बिजली", "आंधी", "गरज"],
                 "wind": [" wind", "cyclone", "గాలి", "హరికేన్", "हवा", "चक्रवात"]}
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
FOLLOWUP = re.compile(r"^\s*(what|how)\s+about\b|^\s*and\b|^\s*also\b|^\s*then\b|^\s*ఇంకా|^\s*और\b|^\s*उसके बाद", re.I)
STOP_WORDS = {"spraying", "farming", "pesticides", "pesticide", "fishermen", "fishing", "travel", "travelling", "traveling",
              "tomorrow", "today", "weekend", "heatwave", "farmers", "farmer", "crops", "irrigation", "flights", "flying",
              "rainfall", "temperature", "humidity", "weather", "forecast", "warnings", "alerts"}
_ENGLISH_KWS = [k.strip() for _, kws in INTENTS for k in kws if k.isascii()]
NOT_PLACES = {"my", "the", "this", "our", "a", "an", "your", "that", "these", "those", "last", "next", "each", "any", "general"}
LOC_RX = re.compile(
    r"\b(?:in|at|for|near|around|of)\s+([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,2}?)"
    r"(?=\s+(?:today|tomorrow|tonight|this|next|over|during|on|for|please|now|weather|rain|and|is|will|be)\b|[?.!,]|$)", re.I)


@dataclass
class Parsed:
    intent: str = "weather"
    intent_matched: bool = False
    location_query: str | None = None
    date_start: int | None = None
    date_end: int | None = None
    parameter: str | None = None
    years: int | None = None
    reply_lang: str | None = None
    topic: str | None = None
    is_followup: bool = False
    needs_llm: bool = False
    explain_request: bool = False
    notes: list[str] = field(default_factory=list)


def detect_script_lang(text: str) -> str | None:
    if TE.search(text):
        return "te"
    if HI.search(text):
        return "hi"
    return None


def _has_any(text: str, kws: list[str]) -> bool:
    return any(k in text for k in kws)


def parse(message: str, today: date | None = None) -> Parsed:
    today = today or date.today()
    text = message.strip()
    low = " " + text.lower() + " "
    p = Parsed()

    # --- language ---
    script = detect_script_lang(text)
    if OTHER_INDIC.search(text) and not script:
        p.needs_llm = True  # a language we have no rules for -> let the LLM parse it (if configured)
    explicit = re.search(r"\b(?:in|into)\s+(telugu|hindi|english)\b|తెలుగులో|हिंदी में|हिन्दी में", low)
    if explicit:
        word = explicit.group(1) or ("telugu" if "తెలుగు" in explicit.group(0) else "hindi")
        p.reply_lang = {"telugu": "te", "hindi": "hi", "english": "en"}[word]
    elif script:
        p.reply_lang = script
    if re.search(r"\b(explain|translate|tell me again|repeat)\b|వివరించు|समझाइए|समझाओ", low) and explicit:
        p.explain_request = True

    # --- intent ---
    for name, kws in INTENTS:
        if _has_any(low, kws):
            p.intent, p.intent_matched = name, True
            break
    if p.intent == "climate_trend" and not re.search(r"rain|temperature|humid|heat|వర్ష|ఉష్ణ|తేమ|बारिश|वर्षा|तापमान|नमी", low) \
            and "climate" not in low and not p.years:
        pass
    if p.intent in ("safety_advice", "alerts", "rain", "temperature", "wind"):
        for topic, kws in HAZARD_TOPICS.items():
            if _has_any(low, kws):
                p.topic = topic
                break
    if p.intent == "alerts" and re.search(r"heavy rain|very heavy", low):
        p.intent = "rain"

    # --- climate parameter / years ---
    if re.search(r"rain|వర్ష|बारिश|वर्षा|precip", low):
        p.parameter = "rainfall"
    elif re.search(r"temperature|temp\b|heat|ఉష్ణ|तापमान|गर्मी", low):
        p.parameter = "temperature"
    elif re.search(r"humid|తేమ|नमी|आर्द्रता", low):
        p.parameter = "humidity"
    if m := re.search(r"(\d{1,2})\s*(?:years?|yrs?|సంవత్సర|साल|वर्ष)", low):
        p.years = max(3, min(30, int(m.group(1))))
    if p.intent == "weather" and p.parameter and p.years:
        p.intent, p.intent_matched = "climate_trend", True

    # --- date ---
    if re.search(r"day after(?: tomorrow)?|ఎల్లుండి|परसों", low):
        p.date_start = p.date_end = 2
    elif re.search(r"tomorrow|రేపు|\bकल\b", low):
        p.date_start = p.date_end = 1
    elif re.search(r"weekend|వారాంతం|सप्ताहांत|वीकेंड", low):
        sat = (5 - today.weekday()) % 7
        p.date_start, p.date_end = sat, min(sat + 1, 6)
    elif re.search(r"this week|next week|next 7|next few days|7.day|week|వారం|सप्ताह|हफ्ते", low):
        p.date_start, p.date_end = 0, 6
    elif re.search(r"\btoday\b|\btonight\b|\bnow\b|ఈ రోజు|ఈరోజు|ఇవాళ|\bआज\b|\bअभी\b", low):
        p.date_start = p.date_end = 0
    else:
        for i, wd in enumerate(WEEKDAYS):
            if re.search(rf"\b{wd}\b", low):
                off = (i - today.weekday()) % 7
                p.date_start = p.date_end = off
                break
    if p.intent == "forecast_range" and p.date_start is None:
        p.date_start, p.date_end = 0, 6

    # --- location ---
    for alias, canon in ALIASES:
        if alias.isascii():
            if re.search(rf"\b{re.escape(alias)}\b", low):
                p.location_query = canon
                break
        elif alias in text:
            p.location_query = canon
            break
    if not p.location_query:
        for m in LOC_RX.finditer(text):
            cand = m.group(1).strip(" .'-")
            first = cand.split()[0].lower()
            words = {w.lower() for w in cand.split()}
            bad = words & STOP_WORDS or any(k in cand.lower() for k in _ENGLISH_KWS) or first.endswith("ing")
            if first not in NOT_PLACES and not bad and not re.search(r"\d", cand) and len(cand) > 2:
                p.location_query = cand
                break

    # --- follow-up detection ---
    p.is_followup = bool(FOLLOWUP.match(text)) or len(text.split()) <= 4 or (
        not p.location_query and not p.intent_matched)
    return p
