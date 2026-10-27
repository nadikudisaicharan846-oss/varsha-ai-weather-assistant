import { useState } from "react";
import { useApp } from "../context/AppContext.jsx";

export default function SearchBar({ onGeoError }) {
  const { t, setPlace } = useApp();
  const [value, setValue] = useState("");

  const submit = (e) => {
    e.preventDefault();
    const city = value.trim();
    if (city.length >= 2) { setPlace({ city }); setValue(""); }
  };
  const locate = () => {
    if (!navigator.geolocation) return onGeoError?.(t("geo.unsupported"));
    navigator.geolocation.getCurrentPosition(
      (pos) => setPlace({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => onGeoError?.(t("geo.denied")), { timeout: 10000 });
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-2 sm:flex-row" role="search">
      <label htmlFor="city" className="sr-only">{t("search.placeholder")}</label>
      <input id="city" value={value} onChange={(e) => setValue(e.target.value)} maxLength={80}
        placeholder={t("search.placeholder")} className="field w-full flex-1 text-base" />
      <div className="flex gap-2">
        <button type="submit" disabled={value.trim().length < 2} className="btn btn-primary flex-1 sm:flex-none">{t("search.go")}</button>
        <button type="button" onClick={locate} className="btn btn-ghost flex-1 sm:flex-none"><span aria-hidden="true">🎯 </span>{t("search.locate")}</button>
      </div>
    </form>
  );
}
