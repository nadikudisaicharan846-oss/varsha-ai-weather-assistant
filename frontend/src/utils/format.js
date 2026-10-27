import { locale } from "../i18n.js";

const COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
export const compass = (deg) => (deg == null ? "" : COMPASS[Math.round(deg / 22.5) % 16]);

export const uvKey = (uv) => (uv == null ? null : uv < 3 ? "lvl.low" : uv < 6 ? "lvl.moderate" : uv < 8 ? "lvl.high" : uv < 11 ? "lvl.veryhigh" : "lvl.extreme");
export const rainKey = (p) => (p == null ? null : p < 20 ? "rain.unlikely" : p < 50 ? "rain.possible" : p < 80 ? "rain.likely" : "rain.verylikely");
export const aqiKey = (a) => (a == null ? null : a <= 50 ? "aqi.good" : a <= 100 ? "aqi.moderate" : a <= 150 ? "aqi.sensitive" : a <= 200 ? "aqi.unhealthy" : a <= 300 ? "aqi.very" : "aqi.hazard");

export function conditionIcon(code, isDay = true) {
  if (code === 0) return isDay ? "☀️" : "🌙";
  if (code === 1) return isDay ? "🌤️" : "🌙";
  if (code === 2) return isDay ? "⛅" : "☁️";
  if (code === 3) return "☁️";
  if (code === 45 || code === 48) return "🌫️";
  if (code >= 51 && code <= 57) return "🌦️";
  if (code >= 61 && code <= 67) return "🌧️";
  if (code >= 71 && code <= 77) return "🌨️";
  if (code >= 80 && code <= 82) return "🌦️";
  if (code === 85 || code === 86) return "🌨️";
  if (code >= 95) return "⛈️";
  return "🌡️";
}

// Backend times are local to the place (no offset); parse as-is and show the same clock digits.
export const fmtDateTime = (iso, lang) => (iso ? new Date(iso).toLocaleString(locale(lang), { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }) : "");
export const fmtClock = (iso, lang) => (iso ? new Date(iso).toLocaleTimeString(locale(lang), { hour: "numeric", minute: "2-digit" }) : "–");
export const fmtWeekday = (d, lang) => new Date(d + "T00:00").toLocaleDateString(locale(lang), { weekday: "short", day: "numeric", month: "short" });
export const fmtHour = (iso) => iso.slice(11, 13);
export const monthName = (m, lang) => new Date(2021, Number(m) - 1, 1).toLocaleDateString(locale(lang), { month: "short" });
export const placeLabel = (loc) => (loc ? [loc.name, loc.admin1].filter((v, i, a) => v && a.indexOf(v) === i).join(", ") : "");
