import { useApp } from "../context/AppContext.jsx";
import { conditionIcon, fmtDateTime, placeLabel } from "../utils/format.js";

export default function WeatherHero({ location, current }) {
  const { t, lang } = useApp();
  return (
    <section aria-label="Current weather" className="rounded-3xl bg-gradient-to-br from-sky-700 to-indigo-800 p-6 text-white shadow-lg sm:p-8">
      <p className="text-lg font-medium text-sky-100">{placeLabel(location)}</p>
      <div className="mt-3 flex items-center gap-4 sm:gap-6">
        <span className="text-7xl sm:text-8xl" role="img" aria-label={t(`cond.${current.condition_key}`)}>{conditionIcon(current.weather_code, current.is_day)}</span>
        <div>
          <p className="text-6xl font-bold leading-none sm:text-7xl">{Math.round(current.temperature_c)}°C</p>
          <p className="mt-2 text-xl">{t(`cond.${current.condition_key}`)}</p>
        </div>
      </div>
      <dl className="mt-6 flex flex-wrap gap-x-8 gap-y-2">
        <div className="flex gap-2"><dt className="text-sky-100">{t("m.feels")}</dt><dd className="font-semibold">{Math.round(current.feels_like_c)}°C</dd></div>
        {current.temp_max_c != null && (
          <div className="flex gap-2"><dt className="text-sky-100">{t("m.today")}</dt><dd className="font-semibold">↑ {Math.round(current.temp_max_c)}° ↓ {Math.round(current.temp_min_c)}°</dd></div>
        )}
      </dl>
      <p className="mt-4 text-sm text-sky-100">{t("m.observed")}: {fmtDateTime(current.observed_at, lang)} ({t("m.local")})</p>
    </section>
  );
}
