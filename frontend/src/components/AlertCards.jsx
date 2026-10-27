import { useApp } from "../context/AppContext.jsx";

const STYLE = {
  information: "border-sky-500 bg-sky-50 dark:bg-sky-950/40",
  advisory: "border-amber-500 bg-amber-50 dark:bg-amber-950/40",
  warning: "border-orange-600 bg-orange-50 dark:bg-orange-950/40",
  severe_warning: "border-red-600 bg-red-50 dark:bg-red-950/50",
};
const BADGE = { information: "bg-sky-600", advisory: "bg-amber-600", warning: "bg-orange-700", severe_warning: "bg-red-700" };

export function AlertCard({ alert: a, compact }) {
  const { t } = useApp();
  return (
    <article className={`rounded-xl border-l-8 p-4 ${STYLE[a.level]}`}>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-2xl" aria-hidden="true">{a.icon}</span>
        <h3 className="text-lg font-bold">{a.title}</h3>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold text-white ${BADGE[a.level]}`}>{a.level_label}</span>
      </div>
      <p className="mt-2">{a.summary}</p>
      {!compact && a.advice.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{a.advice.map((x) => <li key={x}>{x}</li>)}</ul>}
      {a.starts_at && !compact && <p className="muted mt-2 text-xs">{t("alerts.when")}: {a.starts_at.slice(11, 16)}–{a.ends_at?.slice(11, 16)}</p>}
    </article>
  );
}

export function AlertList({ alerts, place, compact = false }) {
  const { t } = useApp();
  if (!alerts.length) return <p className="card p-4">✅ {t("alerts.none")}</p>;
  return <div className="space-y-3">{alerts.map((a) => <AlertCard key={a.id} alert={a} compact={compact} />)}</div>;
}
