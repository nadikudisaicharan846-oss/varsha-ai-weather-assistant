import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { translate } from "../i18n.js";

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);

const load = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage may be blocked */ } };

function makeClientId() {
  const id = load("varsha_client_id", null);
  if (id) return id;
  const n = (crypto.randomUUID?.() || String(Math.random()).slice(2) + Date.now()).replace(/[^A-Za-z0-9]/g, "").slice(0, 32).padEnd(12, "0");
  save("varsha_client_id", n);
  return n;
}

export function AppProvider({ children }) {
  const [lang, setLang] = useState(() => load("varsha_lang", "en"));
  const [theme, setTheme] = useState(() => load("varsha_theme", window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  const [autoSpeak, setAutoSpeak] = useState(() => load("varsha_speak", false));
  const [place, setPlaceState] = useState(() => load("varsha_place", { city: "Hyderabad" }));
  const [resolved, setResolved] = useState(null); // Location object returned by the backend
  const [voiceRequestAt, setVoiceRequestAt] = useState(0);
  const clientId = useMemo(makeClientId, []);

  useEffect(() => { save("varsha_lang", lang); document.documentElement.lang = lang; }, [lang]);
  useEffect(() => { save("varsha_theme", theme); document.documentElement.classList.toggle("dark", theme === "dark"); }, [theme]);
  useEffect(() => save("varsha_speak", autoSpeak), [autoSpeak]);
  const setPlace = useCallback((p) => { setPlaceState(p); save("varsha_place", p); }, []);
  const t = useCallback((key) => translate(lang, key), [lang]);

  const value = { lang, setLang, theme, setTheme, autoSpeak, setAutoSpeak, place, setPlace, resolved, setResolved,
    clientId, t, voiceRequestAt, requestVoice: () => setVoiceRequestAt(Date.now()) };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
