import { LANGS } from "../i18n.js";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";

export default function Settings() {
  const { t, lang, setLang, theme, setTheme, autoSpeak, setAutoSpeak } = useApp();
  const h = useApi(() => api.health(), []);
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-bold">⚙️ {t("set.title")}</h1>
      <section className="card space-y-2 p-4">
        <h2 className="font-semibold">{t("set.lang")}</h2>
        <div className="flex flex-wrap gap-2" role="group">{LANGS.map((l) => (
          <button key={l.code} aria-pressed={lang === l.code} onClick={() => setLang(l.code)} className={`btn ${lang === l.code ? "btn-primary" : "btn-ghost"}`}>{l.name}</button>))}</div>
      </section>
      <section className="card space-y-2 p-4">
        <h2 className="font-semibold">{t("set.theme")}</h2>
        <div className="flex gap-2" role="group">{["light", "dark"].map((m) => (
          <button key={m} aria-pressed={theme === m} onClick={() => setTheme(m)} className={`btn ${theme === m ? "btn-primary" : "btn-ghost"}`}>{t(`set.${m}`)}</button>))}</div>
      </section>
      <section className="card p-4">
        <label className="flex items-center gap-3"><input type="checkbox" className="h-5 w-5" checked={autoSpeak} onChange={(e) => setAutoSpeak(e.target.checked)} />{t("set.speak")}</label>
      </section>
      <section className="card space-y-1 p-4">
        <h2 className="font-semibold">{t("set.status")}</h2>
        {h.data ? (<ul className="space-y-1 text-sm">
          <li>☁️ {h.data.weather_provider}</li>
          <li>{h.data.ai.enabled ? "🤖 " + t("set.ai.on") + ` (${h.data.ai.provider})` : "📊 " + t("set.ai.off")}</li>
          <li>{h.data.database ? "💾 " + t("set.db.on") : "⚠️ " + t("set.db.off")}</li>
          <li>🎙️ {h.data.voice_provider}</li></ul>) : <p className="muted text-sm">{h.error || t("loading")}</p>}
      </section>
      <section className="card space-y-1 p-4"><h2 className="font-semibold">{t("set.sources")}</h2><p className="muted text-sm">{t("set.sources.text")}</p><p className="muted text-sm">{t("disclaimer")}</p></section>
    </div>
  );
}
