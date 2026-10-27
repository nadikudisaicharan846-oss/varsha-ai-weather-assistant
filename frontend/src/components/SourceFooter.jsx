import { useApp } from "../context/AppContext.jsx";

export default function SourceFooter({ source, historical = false }) {
  const { t, lang } = useApp();
  const at = new Date(source.fetched_at).toLocaleTimeString(lang === "en" ? "en-IN" : lang + "-IN", { hour: "numeric", minute: "2-digit" });
  return (
    <p className="muted text-sm">
      {historical ? t("src.hist") : t("src.weather")}:{" "}
      {source.url ? <a href={source.url} target="_blank" rel="noreferrer" className="font-medium underline">{source.provider}</a> : <strong>{source.provider}</strong>}
      {" · "}{t("src.at")} {at}
    </p>
  );
}
