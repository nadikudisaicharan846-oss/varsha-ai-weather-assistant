import { useCallback, useEffect, useRef, useState } from "react";
import { useApp } from "../context/AppContext.jsx";
import { api } from "../services/api.js";
import { speak, stopSpeaking, useSpeechRecognition } from "../hooks/useSpeech.js";
import CardRenderer from "./CardRenderer.jsx";

export default function ChatPanel({ full = false }) {
  const { t, lang, place, clientId, autoSpeak, voiceRequestAt } = useApp();
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const [speakingId, setSpeakingId] = useState(null);
  const sid = useRef(null);
  const end = useRef(null);
  const sendRef = useRef(null);

  const readAloud = useCallback((id, text, l) => {
    if (speakingId === id) { stopSpeaking(); setSpeakingId(null); return; }
    const ok = speak(text, l, () => setSpeakingId(null));
    if (ok) setSpeakingId(id); else setNotice(t("chat.novoice"));
  }, [speakingId, t]);

  const send = useCallback(async (raw) => {
    const text = (raw ?? input).trim();
    if (!text || busy) return;
    setInput(""); setNotice(null); setBusy(true);
    setMsgs((m) => [...m, { id: Date.now(), role: "user", text }]);
    try {
      const res = await api.chat({
        message: text, session_id: sid.current || undefined, language: lang,
        location: place.city ? { city: place.city } : { lat: place.lat, lon: place.lon },
      }, clientId);
      sid.current = res.session_id;
      const id = Date.now() + 1;
      setMsgs((m) => [...m, { id, role: "assistant", text: res.reply, cards: res.cards, sources: res.sources, aiMode: res.ai_mode, lang: res.language }]);
      if (autoSpeak && !speak(res.reply, res.language, () => setSpeakingId(null))) setNotice(t("chat.novoice"));
      else if (autoSpeak) setSpeakingId(id);
    } catch (e) {
      setMsgs((m) => [...m, { id: Date.now() + 2, role: "error", text: e.message }]);
    } finally { setBusy(false); }
  }, [input, busy, lang, place, clientId, autoSpeak, t]);
  sendRef.current = send;

  const { listening, start, stop, supported } = useSpeechRecognition(lang, {
    onResult: (txt) => { setInput(txt); sendRef.current?.(txt); },
    onError: (code) => setNotice(t(code === "denied" ? "chat.mic.denied" : code === "unsupported" ? "chat.mic.unsupported" : "chat.mic.error")),
  });
  useEffect(() => { if (voiceRequestAt && Date.now() - voiceRequestAt < 3000) start(); }, [voiceRequestAt]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { end.current?.scrollIntoView({ block: "end", behavior: "smooth" }); }, [msgs, busy]);
  useEffect(() => () => stopSpeaking(), []);

  const reset = () => { sid.current = null; setMsgs([]); setNotice(null); stopSpeaking(); };
  const suggestions = ["chat.s1", "chat.s2", "chat.s3", "chat.s4", "chat.s5", "chat.s6"];

  return (
    <section className={`card flex flex-col ${full ? "h-[calc(100vh-13rem)] min-h-[32rem]" : "h-[34rem] lg:h-[40rem]"}`} aria-label={t("chat.title")}>
      <div className="flex items-center justify-between border-b px-4 py-3" style={{ borderColor: "var(--ring)" }}>
        <h2 className="font-bold"><span aria-hidden="true">💬 </span>{t("chat.title")}</h2>
        {msgs.length > 0 && <button onClick={reset} className="btn btn-ghost px-3 py-1 text-sm">{t("chat.clear")}</button>}
      </div>
      <div className="scroll-thin flex-1 space-y-3 overflow-y-auto p-4" aria-live="polite">
        {msgs.length === 0 && (
          <div className="space-y-3">
            <p className="muted">{t("chat.welcome")}</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((k) => <button key={k} onClick={() => send(t(k))} className="btn btn-ghost px-3 py-1.5 text-left text-sm">{t(k)}</button>)}
            </div>
          </div>
        )}
        {msgs.map((m) => m.role === "user" ? (
          <div key={m.id} className="flex justify-end"><p className="max-w-[85%] whitespace-pre-line rounded-2xl rounded-br-sm bg-sky-700 px-4 py-2 text-white">{m.text}</p></div>
        ) : m.role === "error" ? (
          <p key={m.id} role="alert" className="rounded-xl border border-red-400 bg-red-50 px-4 py-2 text-sm text-red-950 dark:bg-red-950/50 dark:text-red-100">{m.text}</p>
        ) : (
          <div key={m.id} className="max-w-full space-y-2">
            <div className="card whitespace-pre-line rounded-2xl rounded-bl-sm px-4 py-3">{m.text}</div>
            {m.cards?.map((c, i) => <CardRenderer key={i} card={c} />)}
            <div className="muted flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
              <button onClick={() => readAloud(m.id, m.text, m.lang)} className="underline">🔊 {speakingId === m.id ? t("chat.stop") : t("chat.speak")}</button>
              <span>{m.aiMode === "llm" ? "🤖 " + t("chat.ai") : "📊 " + t("chat.data")}</span>
              {m.sources?.map((s) => <span key={s.provider + s.fetched_at}>{s.is_mock ? "⚠️ " : ""}{s.provider}</span>)}
            </div>
          </div>
        ))}
        {busy && <p className="muted text-sm" role="status">⏳ {t("chat.thinking")}</p>}
        <div ref={end} />
      </div>
      {notice && <p className="mx-4 mb-2 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-950 dark:bg-amber-950/50 dark:text-amber-100" role="status">{notice}</p>}
      {listening && <p className="mx-4 mb-2 text-sm font-medium text-red-600" role="status">🔴 {t("chat.listening")}</p>}
      <form onSubmit={(e) => { e.preventDefault(); send(); }} className="flex gap-2 border-t p-3" style={{ borderColor: "var(--ring)" }}>
        <label htmlFor={full ? "chat-full" : "chat-compact"} className="sr-only">{t("chat.placeholder")}</label>
        <input id={full ? "chat-full" : "chat-compact"} value={input} onChange={(e) => setInput(e.target.value)} maxLength={500}
          placeholder={t("chat.placeholder")} className="field min-w-0 flex-1" disabled={busy} />
        <button type="button" onClick={listening ? stop : start} disabled={!supported || busy} aria-pressed={listening}
          title={supported ? t("chat.mic") : t("chat.mic.unsupported")} aria-label={t("chat.mic")}
          className={`btn ${listening ? "bg-red-600 text-white" : "btn-ghost"}`}>🎙️</button>
        <button type="submit" disabled={busy || !input.trim()} className="btn btn-primary">{t("chat.send")}</button>
      </form>
    </section>
  );
}
