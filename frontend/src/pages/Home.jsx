import { Suspense, lazy, useEffect, useState } from "react";
import Banner from "../components/Banner.jsx";
import ChatPanel from "../components/ChatPanel.jsx";
import DailyList from "../components/DailyList.jsx";
import { AlertCard } from "../components/AlertCards.jsx";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";
import MetricGrid from "../components/MetricGrid.jsx";
import SearchBar from "../components/SearchBar.jsx";
import SourceFooter from "../components/SourceFooter.jsx";
import WeatherHero from "../components/WeatherHero.jsx";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";

const HourlyChart = lazy(() => import("../components/HourlyChart.jsx"));

export default function Home({ go }) {
  const { t, lang, place, setResolved, clientId } = useApp();
  const [geoErr, setGeoErr] = useState(null);
  const key = JSON.stringify(place);
  const cur = useApi(() => api.current(place), [key]);
  const fc = useApi(() => api.forecast(place), [key]);
  const al = useApi(() => api.alerts(place, lang, clientId), [key, lang]);
  useEffect(() => { if (cur.data) setResolved(cur.data.location); }, [cur.data, setResolved]);

  const mock = cur.data?.source.is_mock || fc.data?.source.is_mock;
  const top = al.data?.alerts?.[0];

  return (
    <div className="space-y-4">
      <SearchBar onGeoError={setGeoErr} />
      {geoErr && <Banner kind="warning">{geoErr}</Banner>}
      {mock && <Banner kind="warning" title={t("mock.title")}>{t("mock.body")}</Banner>}
      {cur.error && <Banner title={t("err.title")} action={<button onClick={cur.reload} className="btn btn-ghost py-1 text-sm">{t("retry")}</button>}>{cur.error}</Banner>}
      {top && (
        <div className="space-y-2">
          <AlertCard alert={top} compact />
          <button onClick={() => go("alerts")} className="text-sm font-medium underline">{t("alerts.view")} ({al.data.alerts.length}) →</button>
        </div>
      )}
      {cur.loading && !cur.data ? <LoadingSkeleton rows={3} /> : cur.data && (
        <div className="grid grid-cols-[minmax(0,1fr)] gap-4 lg:grid-cols-5">
          <div className={`lg:col-span-3 ${cur.loading ? "opacity-60" : ""}`}><WeatherHero location={cur.data.location} current={cur.data.current} /></div>
          <div className="lg:col-span-2 lg:row-span-3"><ChatPanel /></div>
          <div className="lg:col-span-3"><MetricGrid current={cur.data.current} /></div>
          <div className="lg:col-span-3 space-y-4">
            {fc.data && (
              <>
                <section className="card p-4"><h2 className="mb-2 font-bold">{t("sec.hourly")}</h2>
                  <Suspense fallback={<div className="h-56 animate-pulse" />}><HourlyChart hourly={fc.data.hourly.slice(0, 24)} /></Suspense></section>
                <section className="card p-4"><h2 className="mb-1 font-bold">{t("sec.daily")}</h2><DailyList daily={fc.data.daily} /></section>
              </>
            )}
            {fc.error && <Banner kind="warning">{fc.error}</Banner>}
          </div>
        </div>
      )}
      {cur.data && <SourceFooter source={cur.data.source} />}
      <p className="muted text-sm">{t("disclaimer")}</p>
    </div>
  );
}
