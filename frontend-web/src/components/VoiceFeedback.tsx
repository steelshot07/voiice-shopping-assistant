import { useEffect } from "react";
import { Check, AlertTriangle, X, Info } from "lucide-react";
import type { VoiceCommandResponse, ProductOption } from "../types/api";

interface VoiceFeedbackProps {
  response: VoiceCommandResponse | null;
  onDismiss: () => void;
  onSelectProduct?: (productId: number) => void;
  onConfirm?: () => void;
  onCancel?: () => void;
}

export function VoiceFeedback({
  response,
  onDismiss,
  onSelectProduct,
  onConfirm,
  onCancel,
}: VoiceFeedbackProps) {
  // Auto-dismiss success after 4s
  useEffect(() => {
    if (response?.status === "success") {
      const timer = setTimeout(onDismiss, 4000);
      return () => clearTimeout(timer);
    }
  }, [response, onDismiss]);

  if (!response) return null;

  const { status, message, items, suggestion, confirmation_required, transcript } = response;

  let feedbackClass = "voice-feedback";
  let Icon = Info;

  if (status === "success") {
    feedbackClass += " voice-feedback--success";
    Icon = Check;
  } else if (status === "ambiguous" || status === "clarification_needed") {
    feedbackClass += " voice-feedback--warning";
    Icon = AlertTriangle;
  } else if (status === "confirmation_needed") {
    feedbackClass += " voice-feedback--warning";
    Icon = AlertTriangle;
  } else if (status === "error") {
    feedbackClass += " voice-feedback--error";
    Icon = AlertTriangle;
  } else if (status === "unknown") {
    feedbackClass += " voice-feedback--muted";
    Icon = Info;
  }

  // Collect all options from ambiguous items
  const ambiguousOptions: ProductOption[] = [];
  for (const item of items) {
    if (item.status === "ambiguous" && item.options) {
      ambiguousOptions.push(...item.options);
    }
  }

  return (
    <div className={feedbackClass}>
      <div className="voice-feedback__header">
        <Icon size={18} className="voice-feedback__icon" />
        <span className="voice-feedback__message">{message}</span>
        <button
          className="voice-feedback__close"
          onClick={onDismiss}
          aria-label="Dismiss"
        >
          <X size={16} />
        </button>
      </div>

      {/* Per-item results for multi-item commands */}
      {items.length > 1 && (
        <div className="voice-feedback__items">
          {items.map((item, i) => (
            <div key={i} className={`voice-feedback__item voice-feedback__item--${item.status}`}>
              <span>{item.status === "success" ? "✓" : item.status === "not_found" ? "✗" : "⚠"}</span>
              <span>{item.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Product selection for ambiguous results */}
      {ambiguousOptions.length > 0 && onSelectProduct && (
        <div className="voice-feedback__options">
          {ambiguousOptions.map((opt) => (
            <button
              key={opt.id}
              className="voice-feedback__option"
              onClick={() => onSelectProduct(opt.id)}
            >
              <span className="voice-feedback__option-name">{opt.name}</span>
              <span className="voice-feedback__option-meta">
                {opt.category && <span>{opt.category}</span>}
                {opt.price && <span>₹{opt.price}</span>}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Confirmation dialog for destructive actions */}
      {confirmation_required && (
        <div className="voice-feedback__confirm-actions">
          <button className="btn btn-small btn-danger" onClick={onConfirm}>
            Yes, clear all
          </button>
          <button className="btn btn-small btn-secondary" onClick={onCancel || onDismiss}>
            Cancel
          </button>
        </div>
      )}

      {/* Suggestion */}
      {suggestion && !confirmation_required && (
        <div className="voice-feedback__suggestion">{suggestion}</div>
      )}

      {/* Subtle transcript */}
      {transcript && (
        <div className="voice-feedback__transcript">Heard: "{transcript}"</div>
      )}
    </div>
  );
}
