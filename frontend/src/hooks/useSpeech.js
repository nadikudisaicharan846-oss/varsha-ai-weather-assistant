
import { useCallback, useEffect, useRef, useState } from "react";
import { speechLang } from "../i18n.js";

const SR =
  typeof window !== "undefined"
    ? window.SpeechRecognition || window.webkitSpeechRecognition
    : null;

export const speechInputSupported = !!SR;

/**
 * Browser speech-to-text.
 */
export function useSpeechRecognition(lang, { onResult, onError }) {
  const [listening, setListening] = useState(false);
  const rec = useRef(null);

  const start = useCallback(() => {
    if (!SR) {
      onError?.("unsupported");
      return;
    }

    try {
      const r = new SR();
      r.lang = speechLang(lang);
      r.interimResults = false;
      r.maxAlternatives = 1;

      r.onresult = (e) => {
        onResult?.(e.results[0][0].transcript);
      };

      r.onerror = (e) => {
        onError?.(
          e.error === "not-allowed" ||
          e.error === "service-not-allowed"
            ? "denied"
            : "error"
        );
      };

      r.onend = () => setListening(false);

      rec.current = r;
      setListening(true);
      r.start();
    } catch (error) {
      console.error("Speech recognition error:", error);
      setListening(false);
      onError?.("error");
    }
  }, [lang, onResult, onError]);

  const stop = useCallback(() => {
    rec.current?.stop();
  }, []);

  useEffect(() => {
    return () => rec.current?.abort?.();
  }, []);

  return { listening, start, stop, supported: !!SR };
}

/**
 * Removes emoji and extra whitespace before speaking.
 */
export function stripForSpeech(text) {
  return String(text ?? "")
    .replace(/\p{Extended_Pictographic}/gu, "")
    .replace(/[•ⓘ]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

// Track audio playback and ongoing requests.
let currentAudio = null;
let currentAudioUrl = null;
let audioRequestId = 0;

/**
 * Stop any currently playing browser or backend speech.
 */
export const stopSpeaking = () => {
  audioRequestId++;

  if (
    typeof window !== "undefined" &&
    "speechSynthesis" in window
  ) {
    window.speechSynthesis.cancel();
  }

  if (currentAudio) {
    currentAudio.pause();
    currentAudio.onended = null;
    currentAudio.onerror = null;
    currentAudio.src = "";
    currentAudio = null;
  }

  if (currentAudioUrl) {
    URL.revokeObjectURL(currentAudioUrl);
    currentAudioUrl = null;
  }
};

/**
 * Telugu uses the backend TTS endpoint.
 * Other languages continue using browser text-to-speech.
 *
 * Returns false if speech cannot be started.
 */
export function speak(text, lang, onEnd) {
  if (typeof window === "undefined") {
    return false;
  }

  const cleanText = stripForSpeech(text);

  if (!cleanText) {
    return false;
  }

  const code = String(speechLang(lang) || lang || "en")
    .toLowerCase();

  // Stop previous speech before starting new speech.
  stopSpeaking();

  // Telugu: generate audio using the backend TTS model.
  if (
    String(lang).toLowerCase().startsWith("te") ||
    code.startsWith("te")
  ) {
    const requestId = audioRequestId;

    fetch("/api/voice/speak", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: cleanText,
        language: "te",
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          const details = await response.text().catch(() => "");
          throw new Error(
            `Telugu TTS request failed (${response.status}): ${details}`
          );
        }

        return response.blob();
      })
      .then((blob) => {
        // Ignore a response if the user stopped or changed speech.
        if (requestId !== audioRequestId) return;

        if (!blob.size) {
          throw new Error("Telugu TTS returned an empty audio file.");
        }

        const audioUrl = URL.createObjectURL(blob);
        currentAudioUrl = audioUrl;

        const audio = new Audio(audioUrl);
        currentAudio = audio;

        const cleanup = () => {
          if (currentAudio === audio) {
            currentAudio = null;
          }

          if (currentAudioUrl === audioUrl) {
            URL.revokeObjectURL(audioUrl);
            currentAudioUrl = null;
          }
        };

        audio.onended = () => {
          cleanup();

          if (requestId === audioRequestId) {
            onEnd?.();
          }
        };

        audio.onerror = () => {
          cleanup();
          console.error("Telugu audio playback failed.");

          if (requestId === audioRequestId) {
            onEnd?.();
          }
        };

        audio.play().catch((error) => {
          cleanup();
          console.error("Could not play Telugu audio:", error);

          if (requestId === audioRequestId) {
            onEnd?.();
          }
        });
      })
      .catch((error) => {
        if (requestId === audioRequestId) {
          console.error("Telugu TTS error:", error);
          onEnd?.();
        }
      });

    return true;
  }

  // English/Hindi and other supported languages: browser TTS.
  if (!("speechSynthesis" in window)) {
    return false;
  }

  const voices = window.speechSynthesis.getVoices();

  const voice =
    voices.find(
      (v) => v.lang.toLowerCase() === code
    ) ||
    voices.find((v) =>
      v.lang.toLowerCase().startsWith(code.slice(0, 2))
    );

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = code;

  if (voice) {
    utterance.voice = voice;
  }

  utterance.onend = onEnd;

  utterance.onerror = (event) => {
  if (event.error === "interrupted" || event.error === "canceled") {
    return;
  }

  console.error("Speech output error:", event.error);
  onEnd?.();
};

  window.speechSynthesis.speak(utterance);

  return true;
}
