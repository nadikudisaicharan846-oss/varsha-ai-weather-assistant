import { Component, Suspense } from "react";
import Header from "./components/Header.jsx";
import LoadingSkeleton from "./components/LoadingSkeleton.jsx";
import { AppProvider } from "./context/AppContext.jsx";
import { useRoute } from "./hooks/useRoute.js";
import Alerts from "./pages/Alerts.jsx";
import Assistant from "./pages/Assistant.jsx";
import Decision from "./pages/Decision.jsx";
import Home from "./pages/Home.jsx";
import Saved from "./pages/Saved.jsx";
import Settings from "./pages/Settings.jsx";
import { lazy } from "react";

const Forecast = lazy(() => import("./pages/Forecast.jsx"));
const Climate = lazy(() => import("./pages/Climate.jsx"));

class Boundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    return this.state.failed
      ? <p role="alert" className="card p-4">Something went wrong displaying this page. Please reload.</p>
      : this.props.children;
  }
}

function Shell() {
  const [route, go] = useRoute();
  const page = {
    home: <Home go={go} />, assistant: <Assistant />, forecast: <Forecast />, alerts: <Alerts />,
    climate: <Climate />, decision: <Decision />, saved: <Saved go={go} />, settings: <Settings />,
  }[route];
  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-white focus:p-2">Skip to content</a>
      <Header route={route} go={go} />
      <main id="main" className="mx-auto max-w-6xl px-4 py-5">
        <Boundary key={route}><Suspense fallback={<LoadingSkeleton />}>{page}</Suspense></Boundary>
      </main>
    </>
  );
}

export default function App() {
  return <AppProvider><Shell /></AppProvider>;
}
