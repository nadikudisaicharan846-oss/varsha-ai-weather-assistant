import { useState } from "react";
import Banner from "../components/Banner.jsx";
import DailyList from "../components/DailyList.jsx";
import HourlyChart from "../components/HourlyChart.jsx";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";
import SearchBar from "../components/SearchBar.jsx";
import SourceFooter from "../components/SourceFooter.jsx";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";
import { placeLabel } from "../utils/format.js";

export default function Forecast() {
  const { t, place, setResolved } = useApp();
  const [hours, setHours] = useState(48);
  const { data, loading, error, reload } = useApi(async () => { const d = await api.forecast(place); setResolved(d.location); return d; }, [JSON.stringify(place)]);
  return (
    <div className="space-y-4">
      <SearchBar />
      {data?.source.is_mock && <Banner kind="warning" title={t("mock.title")}>{t("mock.body")}</Banner>}
      {error && <Banner title={t("err.title")} action={<button onClick={reload} className="btn btn-ghost py-1 text-sm">{t("retry")}</button>}>{error}</Banner>}
      {loading && !data ? <LoadingSkeleton /> : data && (
        <>
          <section className="card p-4">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <h2 className="font-bold">{t("sec.hourly")} — {placeLabel(data.location)}</h2>
              <div role="group" aria-label="Range" className="flex gap-1">
                {[24, 48, 72].map((h) => (
                  <button key={h} onClick={() => setHours(h)} aria-pressed={hours === h} className={`btn px-3 py-1 text-sm ${hours === h ? "btn-primary" : "btn-ghost"}`}>{t(`h.${h}`)}</button>
                ))}
              </div>
            </div>
            <HourlyChart hourly={data.hourly.slice(0, hours)} height={300} />
          </section>
          <section className="card p-4"><h2 className="mb-1 font-bold">{t("sec.daily")}</h2><DailyList daily={data.daily} /></section>
          <SourceFooter source={data.source} />
        </>
      )}
    </div>
  );
}
