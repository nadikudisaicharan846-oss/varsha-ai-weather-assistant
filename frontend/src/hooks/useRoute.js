import { useEffect, useState } from "react";

export const ROUTES = ["home", "assistant", "forecast", "alerts", "climate", "decision", "saved", "settings"];
const read = () => { const r = window.location.hash.replace(/^#\/?/, ""); return ROUTES.includes(r) ? r : "home"; };

export function useRoute() {
  const [route, setRoute] = useState(read);
  useEffect(() => { const f = () => { setRoute(read()); window.scrollTo(0, 0); }; window.addEventListener("hashchange", f); return () => window.removeEventListener("hashchange", f); }, []);
  return [route, (r) => { window.location.hash = `/${r}`; }];
}
