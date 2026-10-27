const BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(method, path, { params = {}, body, clientId } = {}) {
  const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")).toString();
  let res;
  try {
    res = await fetch(`${BASE}${path}${qs ? `?${qs}` : ""}`, {
      method,
      headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(clientId ? { "X-Client-Id": clientId } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("Can't reach the Varsha AI server. Check your connection or that the backend is running.");
  }
  let data = null;
  try { data = await res.json(); } catch { /* non-JSON */ }
  if (!res.ok) {
    throw new Error(data?.error?.message || (typeof data?.detail === "string" ? data.detail : null) ||
      (res.status === 422 ? "Please check what you entered and try again." : "Something went wrong. Please try again."));
  }
  return data;
}

export const placeParams = (p) => (p.city ? { city: p.city } : { lat: p.lat, lon: p.lon });

export const api = {
  health: () => request("GET", "/api/health"),
  current: (p) => request("GET", "/api/weather/current", { params: placeParams(p) }),
  forecast: (p) => request("GET", "/api/weather/forecast", { params: placeParams(p) }),
  alerts: (p, lang, clientId) => request("GET", "/api/alerts", { params: { ...placeParams(p), lang }, clientId }),
  thresholds: () => request("GET", "/api/alerts/thresholds"),
  alertHistory: (clientId) => request("GET", "/api/alerts/history", { clientId }),
  climate: (p, parameter, years, lang, ai) => request("GET", "/api/climate/history", { params: { ...placeParams(p), parameter, years, lang, ai: ai ? "true" : undefined } }),
  decision: (sector, p, day, lang) => request("GET", `/api/decision/${sector}`, { params: { ...placeParams(p), day, lang } }),
  chat: (body, clientId) => request("POST", "/api/chat", { body, clientId }),
  locations: (clientId) => request("GET", "/api/locations", { clientId }),
  addLocation: (body, clientId) => request("POST", "/api/locations", { body, clientId }),
  removeLocation: (id, clientId) => request("DELETE", `/api/locations/${id}`, { clientId }),
  analyses: (clientId) => request("GET", "/api/analyses", { clientId }),
  addAnalysis: (body, clientId) => request("POST", "/api/analyses", { body, clientId }),
  removeAnalysis: (id, clientId) => request("DELETE", `/api/analyses/${id}`, { clientId }),
  conversations: (clientId) => request("GET", "/api/history/conversations", { clientId }),
};
