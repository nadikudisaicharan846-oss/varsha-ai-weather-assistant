import Banner from "../components/Banner.jsx";
import { AlertList } from "../components/AlertCards.jsx";
import LoadingSkeleton from "../components/LoadingSkeleton.jsx";
import SearchBar from "../components/SearchBar.jsx";
import SourceFooter from "../components/SourceFooter.jsx";
import { useApp } from "../context/AppContext.jsx";
import { useApi } from "../hooks/useApi.js";
import { api } from "../services/api.js";
import { placeLabel } from "../utils/format.js";

export default function Alerts() {
  const { t, lang, place, clientId, setResolved } = useApp();
  const { data, loading, error, reload } = useApi(async () => { const d = await api.alerts(place, lang, clientId); setResolved(d.location); return d; }, [JSON.stringify(place), lang]);
  const th = useApi(() => api.thresholds(), []);
  const hist = useApi(() => api.alertHistory(clientId), [data?.generated_at]);
  return (
    <div className="space-y-4">
      <SearchBar />
      {data?.source.is_mock && <Banner kind="warning" title={t("mock.title")}>{t("mock.body")}</Banner>}
      {error && <Banner title={t("err.title")} action={<button onClick={reload} className="btn btn-ghost py-1 text-sm">{t("retry")}</button>}>{error}</Banner>}
      {loading && !data ? <LoadingSkeleton /> : data && (
        <section className="space-y-3">
          <h2 className="text-lg font-bold">{t("sec.alerts")} — {placeLabel(data.location)}</h2>
          <AlertList alerts={data.alerts} />
          <p className="muted text-sm">{data.disclaimer}</p>
          <p className="muted text-sm">ⓘ {data.limitations}</p>
          <SourceFooter source={data.source} />
        </section>
      )}
      {th.data && (
        <details className="card p-4">
          <summary className="cursor-pointer font-semibold">{t("alerts.thresholds")}</summary>
          <pre className="muted scroll-thin mt-2 overflow-x-auto text-xs">{JSON.stringify(th.data, null, 2)}</pre>
        </details>
      )}
      {hist.data?.length > 0 && (
        <details className="card p-4">
          <summary className="cursor-pointer font-semibold">{t("alerts.history")} ({hist.data.length})</summary>
          <ul className="mt-2 space-y-1 text-sm">{hist.data.map((h) => <li key={h.id}>{h.date} · {h.location} · {h.title} <span className="muted">({h.level})</span></li>)}</ul>
        </details>
      )}
    </div>
  );
}
