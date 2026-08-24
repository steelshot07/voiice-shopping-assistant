import { useState, useCallback, useRef, useEffect } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import { processVoiceCommand } from "../api/voice";
import { VoiceFeedback } from "./VoiceFeedback";
import type { VoiceCommandResponse } from "../types/api";

// Tell TypeScript about vendor-prefixed Web Speech API
declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    SpeechRecognition: any;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    webkitSpeechRecognition: any;
  }
}

interface VoiceButtonProps {
  token: string;
  onCommandSuccess: () => void;
  mode?: "fab" | "hero" | "nav";
}

type UIState = "idle" | "listening" | "processing" | "result";

const isSpeechSupported =
  typeof window !== "undefined" &&
  !!(window.SpeechRecognition || window.webkitSpeechRecognition);

const isSecureContext =
  typeof window !== "undefined" && window.isSecureContext;

export function VoiceButton({ token, onCommandSuccess, mode = "fab" }: VoiceButtonProps) {
  const [uiState, setUiState] = useState<UIState>("idle");
  const [transcript, setTranscript] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [voiceResponse, setVoiceResponse] = useState<VoiceCommandResponse | null>(null);

  // Context for follow-up commands
  const [commandContext, setCommandContext] = useState<Record<string, unknown> | undefined>();

  const uiStateRef = useRef<UIState>("idle");
  const transcriptRef = useRef("");
  const tokenRef = useRef(token);
  const onSuccessRef = useRef(onCommandSuccess);
  const contextRef = useRef(commandContext);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);

  useEffect(() => { tokenRef.current = token; }, [token]);
  useEffect(() => { onSuccessRef.current = onCommandSuccess; }, [onCommandSuccess]);
  useEffect(() => { contextRef.current = commandContext; }, [commandContext]);

  useEffect(() => {
    if (!isSpeechSupported || !isSecureContext) return;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognitionAPI: any = window.SpeechRecognition || window.webkitSpeechRecognition;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognition: any = new SpeechRecognitionAPI();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      uiStateRef.current = "listening";
      setUiState("listening");
      setTranscript("");
      setErrorMsg("");
      setVoiceResponse(null);
      transcriptRef.current = "";
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onresult = (event: any) => {
      let current = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        current += event.results[i][0].transcript;
      }
      transcriptRef.current = current;
      setTranscript(current);
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onerror = (event: any) => {
      uiStateRef.current = "idle";
      setUiState("idle");

      const code: string = event.error ?? "";
      if (code === "not-allowed" || code === "permission-denied") {
        setErrorMsg("Microphone access is required for voice commands.");
      } else if (code === "no-speech") {
        setErrorMsg("No speech detected. Please try again.");
      } else if (code === "network") {
        const proto = window.location.protocol;
        if (proto !== "https:") {
          setErrorMsg(`Voice recognition requires HTTPS. You're on ${proto}//`);
        } else {
          setErrorMsg("Couldn't connect to speech service. Check your internet.");
        }
      } else if (code === "service-not-allowed") {
        setErrorMsg("Speech recognition requires HTTPS.");
      } else {
        setErrorMsg("Voice recognition failed. Please try again.");
      }
    };

    recognition.onend = async () => {
      if (uiStateRef.current !== "listening") return;

      const final = transcriptRef.current.trim();
      if (!final) {
        uiStateRef.current = "idle";
        setUiState("idle");
        return;
      }

      uiStateRef.current = "processing";
      setUiState("processing");

      try {
        const res = await processVoiceCommand(
          tokenRef.current,
          final,
          contextRef.current,
        );

        setVoiceResponse(res);
        uiStateRef.current = "result";
        setUiState("result");

        // Save context for follow-up
        if (res.context) {
          setCommandContext(res.context as Record<string, unknown>);
        }

        // Refresh list on success
        if (res.status === "success" && res.intent !== "HELP" && res.intent !== "SHOW_LIST") {
          onSuccessRef.current();
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Couldn't connect to the shopping service.";
        setErrorMsg(message);
        uiStateRef.current = "idle";
        setUiState("idle");
      }
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
      recognitionRef.current = null;
    };
  }, []);

  const handleClick = useCallback(() => {
    setErrorMsg("");

    if (!isSecureContext) {
      setErrorMsg("HTTPS is required for microphone access.");
      return;
    }
    if (!isSpeechSupported) {
      setErrorMsg("Your browser does not support voice recognition. Use Chrome or Safari.");
      return;
    }
    if (!recognitionRef.current) return;

    if (uiState === "listening") {
      recognitionRef.current.stop();
    } else if (uiState === "idle" || uiState === "result") {
      setVoiceResponse(null);
      setTranscript("");
      try {
        recognitionRef.current.start();
      } catch {
        // Silently ignore rapid re-start
      }
    }
  }, [uiState]);

  const handleDismissFeedback = useCallback(() => {
    setVoiceResponse(null);
    uiStateRef.current = "idle";
    setUiState("idle");
  }, []);

  const handleSelectProduct = useCallback(async (productId: number) => {
    if (!token) return;
    try {
      const { addShoppingItem } = await import("../api/shopping");
      await addShoppingItem(token, productId, 1);
      onCommandSuccess();
      handleDismissFeedback();
    } catch {
      // Silently fail
    }
  }, [token, onCommandSuccess, handleDismissFeedback]);

  const handleConfirmClear = useCallback(async () => {
    try {
      const res = await processVoiceCommand(token, "clear my list", undefined, true);
      setVoiceResponse(res);
      if (res.status === "success") {
        onCommandSuccess();
      }
    } catch {
      setErrorMsg("Failed to clear list.");
    }
  }, [token, onCommandSuccess]);

  const isListening = uiState === "listening";
  const isProcessing = uiState === "processing";
  const notSupported = !isSpeechSupported || !isSecureContext;

  // Determine button class
  let btnClass = "voice-btn";
  if (mode === "hero") btnClass += " voice-btn--hero";
  if (mode === "nav") btnClass += " voice-btn--nav";
  if (isListening) btnClass += " voice-btn--listening";
  if (isProcessing) btnClass += " voice-btn--processing";

  return (
    <div className={mode === "hero" ? "voice-hero-container" : mode === "nav" ? "voice-nav-container" : "voice-fab-container"}>
      {/* Error message */}
      {errorMsg && (
        <div className="voice-error-banner">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg("")} className="voice-error-banner__close" aria-label="Dismiss">×</button>
        </div>
      )}

      {/* Live transcript while listening */}
      {isListening && transcript && (
        <div className="voice-transcript-bubble">{transcript}</div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="voice-transcript-bubble">
          <Loader2 size={14} className="spinner" style={{ display: "inline", marginRight: "0.5rem" }} />
          Understanding...
        </div>
      )}

      {/* Voice feedback (results) */}
      {voiceResponse && uiState === "result" && (
        <VoiceFeedback
          response={voiceResponse}
          onDismiss={handleDismissFeedback}
          onSelectProduct={handleSelectProduct}
          onConfirm={handleConfirmClear}
          onCancel={handleDismissFeedback}
        />
      )}

      {/* Microphone button */}
      <button
        id="voice-command-button"
        onClick={handleClick}
        disabled={isProcessing || notSupported}
        className={btnClass}
        aria-label={
          isListening ? "Stop listening" : isProcessing ? "Processing…" : "Start voice command"
        }
      >
        {isListening ? <MicOff size={mode === "hero" ? 28 : 22} /> : isProcessing ? <Loader2 size={mode === "hero" ? 28 : 22} className="spinner" /> : <Mic size={mode === "hero" ? 28 : 22} />}
      </button>

      {/* Label */}
      {mode !== "nav" && (
        <span className="voice-btn__label">
          {isListening
            ? "Tap to stop"
            : isProcessing
            ? "Processing…"
            : notSupported
            ? (!isSecureContext ? "HTTPS required" : "Not supported")
            : "Voice command"}
        </span>
      )}
    </div>
  );
}
