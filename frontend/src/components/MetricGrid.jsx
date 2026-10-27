import { useApp } from "../context/AppContext.jsx";
import { aqiKey, compass, fmtClock, rainKey, uvKey } from "../utils/format.js";

function Metric({ icon, label, value, hint }) {
  return (
    <div className="card p-4">
      <p className="muted flex items-center gap-2 text-sm font-medium"><span aria-hidden="true">{icon}</span>{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      {hint && <p className="muted mt-1 text-sm">{hint}</p>}
    </div>
  );
}

export default function MetricGrid({ current: c }) {
  const { t, lang } = useApp();
  const dash = "–";
  return (
    <section aria-label="Weather details" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <Metric icon="💧" label={t("m.humidity")} value={`${c.humidity_pct}%`} />
      <Metric icon="💨" label={t("m.wind")} value={`${Math.round(c.wind_speed_kmh)} km/h`}
        hint={[compass(c.wind_direction_deg), c.wind_gusts_kmh != null ? `${t("m.gusts")} ${Math.round(c.wind_gusts_kmh)}` : ""].filter(Boolean).join(" · ")} />
      <Metric icon="☔" label={t("m.rain")} value={c.rain_probability_pct != null ? `${c.rain_probability_pct}%` : dash} hint={rainKey(c.rain_probability_pct) && t(rainKey(c.rain_probability_pct))} />
      <Metric icon="🕶️" label={t("m.uv")} value={c.uv_index != null ? c.uv_index.toFixed(1) : dash} hint={uvKey(c.uv_index) && t(uvKey(c.uv_index))} />
      <Metric icon="👁️" label={t("m.vis")} value={c.visibility_km != null ? `${c.visibility_km} km` : dash} />
      <Metric icon="🌫️" label={t("m.aqi")} value={c.aqi_us != null ? c.aqi_us : dash} hint={aqiKey(c.aqi_us) && t(aqiKey(c.aqi_us))} />
      <Metric icon="🌅" label={t("m.sun")} value={fmtClock(c.sunrise, lang)} hint={`${t("m.sunset")} ${fmtClock(c.sunset, lang)}`} />
      <Metric icon="🌡️" label={t("m.feels")} value={`${Math.round(c.feels_like_c)}°C`} />
    </section>
  );
}
