import { Bar, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApp } from "../context/AppContext.jsx";

export default function HourlyChart({ hourly, height = 240 }) {
  const { t } = useApp();
  const data = hourly.map((h) => ({
    label: `${h.time.slice(8, 10)}/${h.time.slice(5, 7)} ${h.time.slice(11, 13)}:00`,
    temp: h.temperature_c, rain: h.rain_probability_pct ?? 0,
  }));
  return (
    <div className="muted" style={{ width: "100%", height }} role="img" aria-label={`${t("chart.temp")}, ${t("chart.rain")}`}>
      <ResponsiveContainer>
        <ComposedChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.3} />
          <XAxis dataKey="label" tickFormatter={(v) => v.split(" ")[1]} interval="preserveStartEnd" minTickGap={28} tick={{ fill: "currentColor", fontSize: 12 }} />
          <YAxis yAxisId="t" tick={{ fill: "currentColor", fontSize: 12 }} unit="°" />
          <YAxis yAxisId="r" orientation="right" domain={[0, 100]} tick={{ fill: "currentColor", fontSize: 12 }} unit="%" />
          <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--ring)", color: "var(--fg)" }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar yAxisId="r" dataKey="rain" name={t("chart.rain")} fill="#38bdf8" fillOpacity={0.55} />
          <Line yAxisId="t" dataKey="temp" name={t("chart.temp")} stroke="#f97316" strokeWidth={2.5} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
