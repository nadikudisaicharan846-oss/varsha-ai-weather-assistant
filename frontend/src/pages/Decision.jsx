import { useState } from "react";
import Banner from "../components/Banner.jsx";
import DecisionCard from "../components/DecisionCard.jsx";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";
import SearchBar from "../components/SearchBar.jsx";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";
import { placeLabel } from "../utils/format.js";

const SECTORS = [["agriculture", "🌾"], ["disaster", "🚨"], ["aviation", "✈️"], ["marine", "⛵"], ["urban", "🏙️"]];

export default function Decision() {
  const { t, lang, place, setResolved } = useApp();
  const [sector, setSector] = useState("agriculture");
  const [day, setDay] = useState(1);
  const { data, loading, error, reload } = useApi(
    async () => { const d = await api.decision(sector, place, day, lang); setResolved(d.location); return d; },
    [sector, day, JSON.stringify(place), lang]);
  return (
    <div className="space-y-4">
      <SearchBar />
      <div role="tablist" aria-label={t("dec.title")} className="flex flex-wrap gap-2">
        {SECTORS.map(([s, icon]) => (
          <button key={s} role="tab" aria-selected={sector === s} onClick={() => setSector(s)} className={`btn px-4 py-2 ${sector === s ? "btn-primary" : "btn-ghost"}`}>
            <span aria-hidden="true">{icon} </span>{t(`sec.${s}`)}</button>
        ))}
      </div>
      <p className="muted text-sm">{t(`desc.${sector}`)}</p>
      <div className="flex items-center gap-2">
        <label htmlFor="dday" className="muted text-sm">{t("dec.day")}</label>
        <select id="dday" className="field py-1.5" value={day} onChange={(e) => setDay(Number(e.target.value))}>
          <option value={0}>{t("m.today")}</option>
          <option value={1}>{{ en: "Tomorrow", te: "రేపు", hi: "कल" }[lang]}</option>
          <option value={2}>{{ en: "Day after tomorrow", te: "ఎల్లుండి", hi: "परसों" }[lang]}</option>
        </select>
        {data && <span className="muted text-sm">📍 {placeLabel(data.location)}</span>}
      </div>
      {data?.source.is_mock && <Banner kind="warning" title={t("mock.title")}>{t("mock.body")}</Banner>}
      {error && <Banner title={t("err.title")} action={<button onClick={reload} className="btn btn-ghost py-1 text-sm">{t("retry")}</button>}>{error}</Banner>}
      {loading && !data ? <LoadingSkeleton /> : data && <div className={loading ? "opacity-60" : ""}><DecisionCard report={data} /></div>}
    </div>
  );
}
