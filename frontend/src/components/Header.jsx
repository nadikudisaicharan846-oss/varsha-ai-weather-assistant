import { LANGS } from "../i18n.js";
import { useApp } from "../context/AppContext.jsx";
import { ROUTES } from "../hooks/useRoute.js";
import { placeLabel } from "../utils/format.js";
import { speechInputSupported } from "../hooks/useSpeech.js";

const ICONS = { home: "🏠", assistant: "💬", forecast: "📈", alerts: "⚠️", climate: "🌍", decision: "🧭", saved: "⭐", settings: "⚙️" };

export default function Header({ route, go }) {
  const { t, lang, setLang, theme, setTheme, resolved, requestVoice } = useApp();
  const voice = () => { requestVoice(); if (route !== "assistant" && route !== "home") go("assistant"); };
  return (
    <header className="sticky top-0 z-20 border-b backdrop-blur" style={{ background: "color-mix(in srgb, var(--bg) 88%, transparent)", borderColor: "var(--ring)" }}>
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <button onClick={() => go("home")} className="flex items-center gap-2 text-left" aria-label="Varsha AI – home">
          <span className="text-3xl" aria-hidden="true">🌧️</span>
          <span>
            <span className="block text-xl font-bold leading-tight">Varsha AI</span>
            <span className="muted block text-xs">{t("tagline")}</span>
          </span>
        </button>
        <div className="flex flex-wrap items-center gap-2">
          {resolved && <span className="card px-3 py-1.5 text-sm font-medium"><span aria-hidden="true">📍 </span>{placeLabel(resolved)}</span>}
          <label className="sr-only" htmlFor="lang">Language</label>
          <select id="lang" value={lang} onChange={(e) => setLang(e.target.value)} className="field py-1.5 text-sm">
            {LANGS.map((l) => <option key={l.code} value={l.code}>{l.name}</option>)}
          </select>
          <button onClick={voice} disabled={!speechInputSupported} title={speechInputSupported ? t("chat.mic") : t("chat.mic.unsupported")}
            className="btn btn-ghost px-3 py-1.5 text-sm" aria-label={t("voice.btn")}><span aria-hidden="true">🎙️ </span><span className="hidden sm:inline">{t("voice.btn")}</span></button>
          <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} className="btn btn-ghost px-3 py-1.5 text-sm" aria-label={t("theme.toggle")}>
            <span aria-hidden="true">{theme === "dark" ? "☀️" : "🌙"}</span>
          </button>
        </div>
      </div>
      <nav aria-label="Main" className="mx-auto max-w-6xl overflow-x-auto px-4 pb-2 scroll-thin">
        <ul className="flex gap-1">
          {ROUTES.map((r) => (
            <li key={r}>
              <button onClick={() => go(r)} aria-current={route === r ? "page" : undefined}
                className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium ${route === r ? "bg-sky-700 text-white" : "hover:bg-black/5 dark:hover:bg-white/10"}`}>
                <span aria-hidden="true">{ICONS[r]} </span>{t(`nav.${r}`)}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
