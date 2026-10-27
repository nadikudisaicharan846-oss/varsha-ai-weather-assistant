import { Bar, BarChart, CartesianGrid, Cell, ComposedChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApp } from "../context/AppContext.jsx";
import { monthName } from "../utils/format.js";
import SourceFooter from "./SourceFooter.jsx";

const tip = { contentStyle: { background: "var(--card)", border: "1px solid var(--ring)", color: "var(--fg)" } };
const axis = { tick: { fill: "currentColor", fontSize: 12 } };
const grid = <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.3} />;

function Chart({ title, height = 230, children }) {
  return (
    <div>
      <h4 className="mb-1 text-sm font-semibold">{title}</h4>
      <div className="muted" style={{ width: "100%", height }}><ResponsiveContainer>{children}</ResponsiveContainer></div>
    </div>
  );
}
const Stat = ({ label, value }) => <div className="card p-3"><p className="muted text-xs">{label}</p><p className="mt-1 text-lg font-bold">{value}</p></div>;

export default function ClimateView({ report: r, compact }) {
  const { t, lang } = useApp();
  const trendMap = Object.fromEntries((r.trend?.line || []).map((p) => [p.label, p.value]));
  const yearly = r.yearly.map((y) => ({ year: y.label, value: y.value, trend: trendMap[y.label] }));
  const clim = r.monthly_climatology.map((m) => ({ month: monthName(m.label, lang), value: m.value }));
  const u = r.unit;
  return (
    <section className="space-y-4" aria-label={t("clim.title")}>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat label={t("clim.mean")} value={`${r.stats.yearly_mean} ${u}`} />
        <Stat label={t("clim.max")} value={`${r.stats.max_year} (${r.stats.max_value})`} />
        <Stat label={t("clim.min")} value={`${r.stats.min_year} (${r.stats.min_value})`} />
        {r.trend && <Stat label={t("clim.slope")} value={`${r.trend.slope_per_decade > 0 ? "+" : ""}${r.trend.slope_per_decade} ${u}${r.trend.significant ? " ✓" : ""}`} />}
      </div>
      <Chart title={`${t("clim.yearly")} (${u})`}>
        <ComposedChart data={yearly} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          {grid}<XAxis dataKey="year" {...axis} /><YAxis {...axis} /><Tooltip {...tip} />
          <Bar dataKey="value" fill="#38bdf8" radius={[4, 4, 0, 0]} />
          {r.trend && <Line dataKey="trend" stroke="#f97316" strokeWidth={2.5} strokeDasharray="6 4" dot={false} />}
        </ComposedChart>
      </Chart>
      <Chart title={`${t("clim.monthly")} (${u})`}>
        <BarChart data={clim} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          {grid}<XAxis dataKey="month" {...axis} /><YAxis {...axis} /><Tooltip {...tip} /><Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </Chart>
      {!compact && (
        <>
          <Chart title={`${t("clim.series")} (${u})`} height={200}>
            <LineChart data={r.monthly} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              {grid}<XAxis dataKey="label" interval={Math.max(0, Math.floor(r.monthly.length / 8))} {...axis} /><YAxis {...axis} /><Tooltip {...tip} />
              <Line dataKey="value" stroke="#14b8a6" strokeWidth={1.8} dot={false} />
            </LineChart>
          </Chart>
          <Chart title={`${t("clim.yoy")} (${u})`} height={190}>
            <BarChart data={r.year_to_year_change} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              {grid}<XAxis dataKey="label" {...axis} /><YAxis {...axis} /><Tooltip {...tip} />
              <Bar dataKey="value">{r.year_to_year_change.map((p) => <Cell key={p.label} fill={p.value >= 0 ? "#ef4444" : "#3b82f6"} />)}</Bar>
            </BarChart>
          </Chart>
        </>
      )}
      <div className="card space-y-3 p-4">
        <div><h4 className="text-sm font-bold">📊 {t("clim.observed")}</h4><p className="text-sm">{r.observed_text}</p></div>
        {r.trend_text && <div><h4 className="text-sm font-bold">📈 {t("clim.stat")}</h4><p className="text-sm">{r.trend_text}</p></div>}
        <div><h4 className="text-sm font-bold">💡 {t("clim.interp")}</h4><p className="text-sm">{r.interpretation_text}</p></div>
        {r.ai_interpretation && <div><h4 className="text-sm font-bold">🤖 {t("clim.ai")}</h4><p className="text-sm">{r.ai_interpretation}</p></div>}
        <div><h4 className="text-sm font-bold">ⓘ {t("clim.note")}</h4><ul className="muted list-disc pl-5 text-xs">{r.caveats.map((c) => <li key={c}>{c}</li>)}</ul></div>
      </div>
      <SourceFooter source={r.source} historical />
    </section>
  );
}
