import { useApp } from "../context/AppContext.jsx";
import { conditionIcon, fmtWeekday } from "../utils/format.js";

export default function DailyList({ daily }) {
  const { t, lang } = useApp();
  return (
    <ul className="divide-y" style={{ borderColor: "var(--ring)" }}>
      {daily.map((d) => (
        <li key={d.date} className="flex flex-wrap items-center gap-x-4 gap-y-1 py-2.5" style={{ borderColor: "var(--ring)" }}>
          <span className="w-28 font-medium">{fmtWeekday(d.date, lang)}</span>
          <span className="text-2xl" aria-hidden="true">{conditionIcon(d.weather_code)}</span>
          <span className="muted min-w-32 flex-1 text-sm">{t(`cond.${d.condition_key}`)}</span>
          <span className="text-sm">☔ {d.rain_probability_pct ?? 0}% · {d.precipitation_sum_mm.toFixed(1)} mm</span>
          <span className="w-24 text-right font-semibold">{Math.round(d.temp_max_c)}° / {Math.round(d.temp_min_c)}°</span>
        </li>
      ))}
    </ul>
  );
}
