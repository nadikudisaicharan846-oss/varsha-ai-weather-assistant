import { Suspense, lazy } from "react";
import { useApp } from "../context/AppContext.jsx";
import { AlertList } from "./AlertCards.jsx";
import DailyList from "./DailyList.jsx";
import DecisionCard from "./DecisionCard.jsx";
import { conditionIcon } from "../utils/format.js";

const ClimateView = lazy(() => import("./ClimateView.jsx")); // recharts is loaded only when a chart is needed
const HourlyChart = lazy(() => import("./HourlyChart.jsx"));
const Wait = ({ children }) => <Suspense fallback={<div className="card h-32 animate-pulse opacity-60" />}>{children}</Suspense>;

/** Renders the structured cards returned by POST /api/chat inside a message bubble. */
export default function CardRenderer({ card }) {
  const { t } = useApp();
  switch (card.type) {
    case "current": {
      const c = card.data.current;
      return (
        <div className="card flex items-center gap-4 p-3">
          <span className="text-5xl" aria-hidden="true">{conditionIcon(c.weather_code, c.is_day)}</span>
          <div>
            <p className="text-3xl font-bold">{Math.round(c.temperature_c)}°C</p>
            <p className="muted text-sm">{t(`cond.${c.condition_key}`)} · 💧 {c.humidity_pct}% · 💨 {Math.round(c.wind_speed_kmh)} km/h</p>
          </div>
        </div>
      );
    }
    case "daily": return <div className="card px-3"><DailyList daily={card.data} /></div>;
    case "hourly": return <div className="card p-3"><Wait><HourlyChart hourly={card.data} height={180} /></Wait></div>;
    case "alerts": return card.data.length ? <AlertList alerts={card.data} compact /> : null;
    case "decision": return <DecisionCard report={card.data} compact />;
    case "climate": return <Wait><ClimateView report={card.data} compact /></Wait>;
    default: return null;
  }
}
