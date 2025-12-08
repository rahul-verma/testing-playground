// src/chat.ts
export type ChatState = {
  conversationId: string | null;
  userId: string | null;
  locale: string;          // e.g. "en-US"
  consentGiven: boolean;
};

export type MessagePayload = {
  messageId: string;       // UUID v4
  conversationId: string;
  userId: string;
  locale: string;
  text: string;            // sanitized & truncated
  length: number;          // character length of `text` in Unicode code points
  createdAt: string;       // ISO timestamp
  channel: "web";
  retryOf?: string;        // messageId of previous attempt, if this is a retry
};

export const MAX_TEXT_LENGTH = 4000;

// Simple UUID v4 generator for demo purposes only.
export function uuidV4(): string {
  // Not crypto-strong, but fine for the exercise
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    const v = c === "x" ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Count Unicode code points in a JS string.
 * Using spread syntax, which iterates over code points.
 */
export function codePointLength(text: string): number {
  return [...text].length;
}

/**
 * Extremely simple "sanitization":
 * strip `<` and `>` so that they never reach the backend.
 * Real life: you'd use a proper HTML/markdown sanitizer.
 */
export function sanitizeText(rawText: string): string {
  return rawText.replace(/[<>]/g, "");
}

/**
 * Truncate text to respect MAX_TEXT_LENGTH in terms of code points.
 * If truncated, we keep (MAX_TEXT_LENGTH - 1) code points and add an ellipsis `…`.
 */
export function truncateWithEllipsis(text: string, maxLength: number): string {
  const cps = [...text];
  if (cps.length <= maxLength) {
    return text;
  }
  if (maxLength <= 0) {
    return "";
  }
  if (maxLength === 1) {
    return "…";
  }
  const head = cps.slice(0, maxLength - 1).join("");
  return head + "…";
}

export function buildMessagePayload(
  rawText: string,
  state: ChatState,
  retryOf?: string
): MessagePayload {
  // 1. Consent
  if (!state.consentGiven) {
    throw new Error("Consent is required to send messages.");
  }

  // 2. Basic state validation
  if (!state.conversationId || !state.conversationId.trim()) {
    throw new Error("Missing conversationId");
  }
  if (!state.userId || !state.userId.trim()) {
    throw new Error("Missing userId");
  }

  // 3. Raw text validation
  if (!rawText || rawText.trim().length === 0) {
    throw new Error("Empty or whitespace-only messages are not allowed.");
  }

  // 4. Sanitize
  const sanitized = sanitizeText(rawText);

  // 5. Truncate to max length in code points
  const truncated = truncateWithEllipsis(sanitized, MAX_TEXT_LENGTH);

  // 6. Compute length in code points
  const length = codePointLength(truncated);

  // 7. Build payload
  const payload: MessagePayload = {
    messageId: uuidV4(),
    conversationId: state.conversationId,
    userId: state.userId,
    locale: state.locale,
    text: truncated,
    length,
    createdAt: new Date().toISOString(),
    channel: "web",
  };

  if (retryOf) {
    payload.retryOf = retryOf;
  }

  return payload;
}
