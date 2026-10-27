import ChatPanel from "../components/ChatPanel.jsx";
import { useApp } from "../context/AppContext.jsx";

export default function Assistant() {
  const { t } = useApp();
  return (
    <div className="mx-auto max-w-3xl space-y-3">
      <ChatPanel full />
      <p className="muted text-sm">{t("disclaimer")}</p>
    </div>
  );
}
