import { useState } from "react";
import Banner from "../components/Banner.jsx";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";
import { placeLabel } from "../utils/format.js";

export default function Saved({ go }) {
  const { t, clientId, resolved, setPlace } = useApp();
  const [msg, setMsg] = useState(null);
  const locs = useApi(() => api.locations(clientId), []);
  const ana = useApi(() => api.analyses(clientId), []);
  const conv = useApi(() => api.conversations(clientId), []);
  const act = async (fn, reload) => { try { await fn(); setMsg(null); reload(); } catch (e) { setMsg(e.message); } };
  const down = locs.error && /Saving is unavailable|database/i.test(locs.error);

  return (
    <div className="space-y-5">
      {(msg || down) && <Banner kind="warning">{msg || t("saved.nodb")}</Banner>}
      <section className="card space-y-3 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-bold">⭐ {t("saved.title")}</h2>
          <button disabled={!resolved} className="btn btn-primary text-sm" onClick={() => act(() => api.addLocation({ name: resolved.name, admin1: resolved.admin1, country: resolved.country, latitude: resolved.latitude, longitude: resolved.longitude }, clientId), locs.reload)}>
            {t("saved.add")}{resolved ? ` (${resolved.name})` : ""}</button>
        </div>
        {!locs.data?.length ? <p className="muted">{t("saved.none")}</p> : (
          <ul className="space-y-2">{locs.data.map((l) => (
            <li key={l.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg px-3 py-2" style={{ boxShadow: "inset 0 0 0 1px var(--ring)" }}>
              <span>📍 {placeLabel(l)}</span>
              <span className="flex gap-2">
                <button className="btn btn-ghost py-1 text-sm" onClick={() => { setPlace({ city: l.name }); go("home"); }}>{t("saved.open")}</button>
                <button className="btn btn-ghost py-1 text-sm" onClick={() => act(() => api.removeLocation(l.id, clientId), locs.reload)}>{t("saved.remove")}</button>
              </span>
            </li>))}</ul>)}
      </section>
      <section className="card space-y-2 p-4">
        <h2 className="font-bold">🌍 {t("saved.analyses")}</h2>
        {!ana.data?.length ? <p className="muted">{t("saved.none")}</p> : ana.data.map((a) => (
          <details key={a.id} className="rounded-lg px-3 py-2" style={{ boxShadow: "inset 0 0 0 1px var(--ring)" }}>
            <summary className="cursor-pointer font-medium">{a.title}</summary>
            <div className="mt-2 space-y-1 text-sm"><p>{a.summary.observed}</p><p>{a.summary.statistical}</p><p className="muted">{a.summary.interpretation}</p>
              <button className="btn btn-ghost py-1 text-sm" onClick={() => act(() => api.removeAnalysis(a.id, clientId), ana.reload)}>{t("saved.remove")}</button></div>
          </details>))}
      </section>
      <section className="card space-y-2 p-4">
        <h2 className="font-bold">💬 {t("saved.history")}</h2>
        {!conv.data?.length ? <p className="muted">{t("saved.none")}</p> : (
          <ul className="space-y-1 text-sm">{conv.data.slice(-30).map((m) => <li key={m.id}><span className="muted">{m.role === "user" ? "🧑" : "🌧️"} </span>{m.content.slice(0, 180)}{m.content.length > 180 ? "…" : ""}</li>)}</ul>)}
      </section>
    </div>
  );
}
