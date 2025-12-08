// tests/chat.property.test.ts
import * as fc from "fast-check";
import {
  buildMessagePayload,
  ChatState,
  MAX_TEXT_LENGTH,
  codePointLength,
} from "../src/chat";

// ---------- Arbitraries ----------

// Simple locale generator
const localeArb = fc.constantFrom("en-US", "de-DE", "fr-FR", "es-ES");

// "UUID-looking" strings for user/conversation IDs (ASCII only, fine for tests)
const uuidishArb = fc
  .tuple(
    fc.string({ minLength: 8, maxLength: 8 }),
    fc.string({ minLength: 4, maxLength: 4 }),
    fc.string({ minLength: 4, maxLength: 4 }),
    fc.string({ minLength: 4, maxLength: 4 }),
    fc.string({ minLength: 12, maxLength: 12 })
  )
  .map(([a, b, c, d, e]) => `${a}-${b}-${c}-${d}-${e}`);

// Valid state: consent given, non-empty IDs
const validStateArb = fc
  .record({
    conversationId: uuidishArb,
    userId: uuidishArb,
    locale: localeArb,
    consentGiven: fc.constant(true),
  })
  .map((s) => s as ChatState);

// State with no consent
const noConsentStateArb = fc
  .record({
    conversationId: fc.option(uuidishArb, { nil: null }),
    userId: fc.option(uuidishArb, { nil: null }),
    locale: localeArb,
    consentGiven: fc.constant(false),
  })
  .map((s) => s as ChatState);

// Arbitrary string (possibly empty). For older fast-check we just use string()
const unicodeTextArb = fc.string();

// Long strings (definitely longer than MAX_TEXT_LENGTH)
const longUnicodeTextArb = fc
  .string({
    minLength: MAX_TEXT_LENGTH + 10,
    maxLength: MAX_TEXT_LENGTH * 3,
  })
  // Make sure we don't accidentally generate only whitespace
  .filter((s) => s.replace(/\s+/g, "").length > 0);

// Strings that are whitespace-only
const whitespaceOnlyTextArb = fc
  .string({ minLength: 1, maxLength: 200 })
  .filter((s) => s.trim().length === 0);

// Retry IDs (any UUID-ish string)
const retryIdArb = uuidishArb;

// ---------- Helper: UUID v4 regex ----------

const uuidV4Regex =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

// ---------- Properties ----------

// P1/2/3/4/9: IDs, locale, channel, sanitation, length, UUID format
test("P1/2/3/4/9: payload respects IDs, locale, sanitation, length and UUID format", () => {
  fc.assert(
    fc.property(
      unicodeTextArb,
      validStateArb,
      (rawText: string, state: ChatState) => {
        // Precondition: non-empty, non-whitespace text
        fc.pre(rawText.trim().length > 0);

        const payload = buildMessagePayload(rawText, state);

        // Conversation & user IDs
        expect(payload.conversationId).toBe(state.conversationId);
        expect(payload.userId).toBe(state.userId);
        expect(payload.conversationId).not.toHaveLength(0);
        expect(payload.userId).not.toHaveLength(0);

        // Locale & channel
        expect(payload.locale).toBe(state.locale);
        expect(payload.channel).toBe("web");

        // Sanitization
        expect(payload.text.includes("<")).toBe(false);
        expect(payload.text.includes(">")).toBe(false);

        // Length & max limit
        const cpLen = codePointLength(payload.text);
        expect(cpLen).toBeLessThanOrEqual(MAX_TEXT_LENGTH);
        expect(payload.length).toBe(cpLen);

        // Message ID UUID v4
        expect(uuidV4Regex.test(payload.messageId)).toBe(true);
      }
    ),
    { verbose: true }
  );
});

// P5: Long text must be truncated with ellipsis and exact max length in code points
test("P5: long text is truncated with ellipsis and max code-point length", () => {
  fc.assert(
    fc.property(
      longUnicodeTextArb,
      validStateArb,
      (rawText: string, state: ChatState) => {
        const payload = buildMessagePayload(rawText, state);

        const cpLen = codePointLength(payload.text);

        expect(cpLen).toBe(MAX_TEXT_LENGTH);
        expect(payload.text.endsWith("…")).toBe(true);
        expect(payload.length).toBe(cpLen);
      }
    ),
    { verbose: true }
  );
});

// P6: Consent is required - no message when consentGiven === false
test("P6: consent is required; buildMessagePayload throws if consentGiven = false", () => {
  fc.assert(
    fc.property(
      unicodeTextArb,
      noConsentStateArb,
      (rawText: string, state: ChatState) => {
        expect(() => buildMessagePayload(rawText, state)).toThrow();
      }
    ),
    { verbose: true }
  );
});

// P7: Empty or whitespace-only messages are rejected even if consent is true
test("P7: empty or whitespace-only messages are rejected", () => {
  fc.assert(
    fc.property(
      whitespaceOnlyTextArb,
      validStateArb,
      (rawText: string, state: ChatState) => {
        expect(() => buildMessagePayload(rawText, state)).toThrow();
      }
    ),
    { verbose: true }
  );
});

// P3 (sanitization-specific) targeted: '<' and '>' must be removed
test("P3 (focused): '<' and '>' are removed from outgoing text", () => {
  const textWithAnglesArb = fc
    .string()
    .filter((s) => s.includes("<") || s.includes(">"));

  fc.assert(
    fc.property(
      textWithAnglesArb,
      validStateArb,
      (rawText: string, state: ChatState) => {
        const payload = buildMessagePayload(rawText, state);

        expect(payload.text.includes("<")).toBe(false);
        expect(payload.text.includes(">")).toBe(false);
      }
    ),
    { verbose: true }
  );
});

// P8: Retry semantics — retryOf is propagated and messageId is different
test("P8: retryOf is propagated and messageId is always new", () => {
  fc.assert(
    fc.property(
      unicodeTextArb,
      validStateArb,
      retryIdArb,
      (rawText: string, state: ChatState, retryOf: string) => {
        fc.pre(rawText.trim().length > 0);

        const payload = buildMessagePayload(rawText, state, retryOf);

        expect(payload.retryOf).toBe(retryOf);
        expect(payload.messageId).not.toBe(retryOf);
      }
    ),
    { verbose: true }
  );
});
