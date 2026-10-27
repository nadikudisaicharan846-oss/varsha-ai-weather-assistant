import { useApp } from "../context/AppContext.jsx";
import SourceFooter from "./SourceFooter.jsx";

const V = {
  good: "border-green-600 bg-green-50 dark:bg-green-950/40", caution: "border-amber-500 bg-amber-50 dark:bg-amber-950/40",
  avoid: "border-red-600 bg-red-50 dark:bg-red-950/40", info: "border-sky-500 bg-sky-50 dark:bg-sky-950/40",
};
const DOT = { good: "🟢", caution: "🟡", avoid: "🔴", info: "⚪", na: "⚪" };

export default function DecisionCard({ report: r, compact }) {
  const { t } = useApp();
  return (
    <section className="card space-y-3 p-4" aria-label={t(`sec.${r.sector}`)}>
      <div className={`rounded-xl border-l-8 p-3 ${V[r.verdict] || V.info}`}>
        <p className="muted text-xs font-semibold uppercase">{t(`sec.${r.sector}`)} · {r.period}</p>
        <p className="mt-1 text-lg font-bold">{t(`v.${r.verdict}`)} — {r.headline}</p>
      </div>
      <ul className="grid gap-2 sm:grid-cols-2">
        {r.checks.map((c) => (
          <li key={c.key} className="flex items-center justify-between gap-3 rounded-lg px-3 py-2" style={{ boxShadow: "inset 0 0 0 1px var(--ring)" }}>
            <span className="text-sm">{c.label}</span>
            <span className="text-right text-sm font-semibold"><span aria-hidden="true">{DOT[c.status]} </span>{c.value}<span className="sr-only"> ({t(`s.${c.status}`)})</span></span>
          </li>
        ))}
      </ul>
      {r.alerts_summary?.length > 0 && !compact && <ul className="space-y-1 text-sm">{r.alerts_summary.map((s) => <li key={s}>{s}</li>)}</ul>}
      <ul className="list-disc space-y-1 pl-5 text-sm">{r.recommendations.map((x) => <li key={x}>{x}</li>)}</ul>
      <p className="muted text-xs">{r.disclaimer}</p>
      {!compact && <SourceFooter source={r.source} />}
    </section>
  );
}
