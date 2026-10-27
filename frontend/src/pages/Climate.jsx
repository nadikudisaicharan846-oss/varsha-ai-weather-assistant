import { useEffect, useState } from "react";
import Banner from "../components/Banner.jsx";
import ClimateView from "../components/ClimateView.jsx";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";
import SearchBar from "../components/SearchBar.jsx";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";
import { placeLabel } from "../utils/format.js";

export default function Climate() {
  const { t, lang, place, clientId, setResolved } = useApp();
  const [param, setParam] = useState("rainfall");
  const [years, setYears] = useState(10);
  const [withAi, setWithAi] = useState(false);
  const [applied, setApplied] = useState({ param: "rainfall", years: 10, withAi: false });
  const [saveState, setSaveState] = useState(null);
  const health = useApi(() => api.health(), []);
  const { data, loading, error, reload } = useApi(
    async () => { const d = await api.climate(place, applied.param, applied.years, lang, applied.withAi); setResolved(d.location); return d; },
    [JSON.stringify(place), lang, applied]);
  useEffect(() => setSaveState(null), [data]);

  const save = async () => {
    try {
      await api.addAnalysis({ title: `${t(`clim.${data.parameter}`)} · ${placeLabel(data.location)} · ${data.start_year}–${data.end_year}`, location: placeLabel(data.location),
        parameter: data.parameter, years: applied.years,
        summary: { unit: data.unit, stats: data.stats, trend: data.trend && { ...data.trend, line: undefined }, observed: data.observed_text, statistical: data.trend_text, interpretation: data.interpretation_text } }, clientId);
      setSaveState("ok");
    } catch (e) { setSaveState(e.message); }
  };

  return (
    <div className="space-y-4">
      <SearchBar />
      <form className="card flex flex-wrap items-end gap-3 p-4" onSubmit={(e) => { e.preventDefault(); setApplied({ param, years, withAi }); }}>
        <div><label htmlFor="cp" className="muted mb-1 block text-sm">{t("clim.param")}</label>
          <select id="cp" className="field" value={param} onChange={(e) => setParam(e.target.value)}>
            {["rainfall", "temperature", "humidity"].map((p) => <option key={p} value={p}>{t(`clim.${p}`)}</option>)}</select></div>
        <div><label htmlFor="cy" className="muted mb-1 block text-sm">{t("clim.years")}</label>
          <select id="cy" className="field" value={years} onChange={(e) => setYears(Number(e.target.value))}>{[5, 10, 15, 20, 30].map((y) => <option key={y} value={y}>{y}</option>)}</select></div>
        {health.data?.ai?.enabled && <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={withAi} onChange={(e) => setWithAi(e.target.checked)} />{t("clim.withai")}</label>}
        <button className="btn btn-primary" type="submit">{t("clim.run")}</button>
        {data && <button type="button" onClick={save} className="btn btn-ghost">⭐ {t("clim.save")}</button>}
      </form>
      {saveState === "ok" && <Banner kind="info">{t("clim.saved")}</Banner>}
      {saveState && saveState !== "ok" && <Banner kind="warning">{saveState}</Banner>}
      {data?.source.is_mock && <Banner kind="warning" title={t("mock.title")}>{t("mock.body")}</Banner>}
      {error && <Banner title={t("err.title")} action={<button onClick={reload} className="btn btn-ghost py-1 text-sm">{t("retry")}</button>}>{error}</Banner>}
      {loading && !data ? <LoadingSkeleton rows={4} /> : data && (
        <div className={loading ? "opacity-60" : ""}>
          <h2 className="mb-2 text-lg font-bold">{t(`clim.${data.parameter}`)} — {placeLabel(data.location)} ({data.start_year}–{data.end_year})</h2>
          <ClimateView report={data} />
        </div>
      )}
    </div>
  );
}
