## Static Testing

In this exercise, you will practice **static testing**: finding issues by reviewing artefacts, without running the system.

### A Short Checklist for Reviewing Artefacts

1. **Scope & Goals**
   - Are the goals of the system/feature clearly stated and testable?

2. **Supported Channels & Markets**
   - Are all channels (web, voice, etc.) and markets/languages explicitly listed and treated consistently?

3. **User Journeys & Flows**
   - Are the main user journeys (happy paths) fully described from start to finish?

4. **Error & “No Data” Paths**
   - Are fallback paths for missing data, errors, and “no result found” clearly defined?

5. **Business Rules & Thresholds**
   - Are all business rules, thresholds, and limits documented, unambiguous, and consistent across artefacts?

6. **Compliance / Legal Requirements**
   - Are legal, regulatory, and industry-specific requirements explicitly captured (not “assumed”)?

7. **Disclaimers & Notices**
   - Are required disclaimers, consent texts, and recording/privacy notices defined per market/channel?

8. **PII & Sensitive Data Usage**
   - Is it clear which data is considered PII/sensitive and how it may (or may not) be used?

9. **Data Minimisation**
   - Is only the minimum necessary personal data collected and stored to achieve the stated goals?

10. **Logging & Redaction**
    - Are logging rules documented, including which fields are redacted and how long logs are kept?

11. **Security-Sensitive Actions**
    - Are high-risk actions (refunds, account changes, access to confidential data) clearly controlled and approved?

12. **Roles & Permissions**
    - Are role-based permissions defined, with restrictions for who can change critical settings or limits?

13. **NLU Intents & Training Data**
    - Are intents, entities/slots, and example utterances well-defined, non-overlapping, and representative of real users?

14. **Edge Cases & Ambiguity**
    - Are ambiguous or mixed-intent user messages, hostile language, and “out of scope” topics considered?

15. **Tone, Style & Accessibility**
    - Is tone appropriate for the domain and markets? Are clarity, politeness, and accessibility needs addressed?

16. **Error Messages & Escalation**
    - Are error messages understandable and helpful? Are escalation rules (to humans/support) clearly defined?

17. **Configuration Consistency**
    - Are configuration values (limits, thresholds, flags) consistent between specs, flows, and code/config files?

18. **TODOs & Assumptions**
    - Are there any “TODO”, “later”, or vague assumptions in critical areas (compliance, security, PII, refunds)?

19. **Monitoring & Metrics**
    - Is there any mention of how behaviour will be monitored (KPIs, alerts, logs) after go-live?

20. **Change Management & Versioning**
    - Is there a plan or note on how rules, limits, and flows will be versioned and updated safely over time?

### Scenario

You are reviewing a new **Casanova agent** for a regulated insurance/finance company that operates in **Germany, other EU markets, and the US**.

You are **not allowed to run the agent**. Using only what you can read, find as many issues and risks as you can.

You will use reviews to find issues in:

- Conversation briefs & flows
- NLU training examples
- Integration specs

**Instructions:**

- Highlight or underline issues.
- Label each issue with at least one tag:
  - **F** = functional / correctness
  - **C** = compliance / legal / regulatory
  - **S** = security / privacy / PII
  - **UX** = tone / clarity / accessibility
  - **Ops** = operations / maintainability

### Artefact A – Conversation brief

```
**GlobalSure Assistant – Conversation Brief (Draft)**  

**Channels:** Phone (voice), Web chat  
**Markets:** Germany, EU (English), US  

### Main goals

- Handle order tracking queries  
  (e.g. “Where is my policy document?”, “Was my claim paid?”)
- Handle returns/refunds for incorrectly charged premiums
- Answer FAQs about coverage, opening hours, and contact options

### Tone & style

- Friendly, casual, “on your side”
- For German customers, we prefer **“du”** to keep it modern and approachable
- Keep answers short, one sentence if possible

### Compliance & legal notes (to refine later)

- For calls, some countries require us to mention recording; we will implement this in the IVR later.
- In the US, we should probably mention that the assistant is not a licensed advisor.
- Refunds above 5,000 EUR/USD must be approved by a human, but in practice this rarely happens.

### Order tracking behaviour (simplified)

- The assistant asks for **policy number OR date of birth**.
- It fetches policy status from the **Policy API**.
- If no policy is found, it says:  
  “We couldn’t find anything, please call support.”
- If claim status is **“paid”**, it says:  
  “Your claim was successfully paid.”

### Refund behaviour (simplified)

- If the customer says they were charged incorrectly, the assistant tries to refund based on the **last payment**.
- If amount **≤ 10,000 EUR/USD** and the policy is active, refund automatically and confirm to the customer.
- If amount **> 10,000**, offer to transfer to an agent, but automatic refund is still allowed if the customer insists.

### Escalation behaviour

- If user says “agent”, “human”, “complaint”, immediately transfer to **general support**.
- If the assistant is more than 70% unsure, ask the customer to repeat once, then **end the conversation** if still unclear.

### PII handling (high-level)

- The assistant may ask for: **name, date of birth, address, last four of credit card, policy number**.
- We should not store sensitive data unnecessarily; logging will be handled later in the project.

```

### Artefact B – Flow/config snippet (simplified YAML-ish)

```yaml
flows:
  refund_flow:
    max_auto_refund_amount: 10000        # in EUR or USD depending on region
    require_human_approval_above: 5000   # TODO: enforce later
    ask_for_reason: false                # keep it simple for now
    log_refund_payload: full             # logs full request/response body
    escalation_queue_large_refunds: "general_support"

  order_tracking_flow:
    identifiers:
      - policy_number
      - date_of_birth
      - last_four_credit_card  # fallback, faster for users
    fallback_on_no_match: "ask_user_to_call_support"
    retry_attempts: 1
    confidence_threshold_for_status_answer: 0.4
    log_policy_status_response: true

logging:
  redact_fields:
    - "password"
    - "social_security_number"
    # TODO: add more PII fields if needed

security:
  allow_agent_triggered_refunds: true
  roles_allowed_to_edit_refund_limits:
    - "support_agent"
    - "trainee"
    - "admin"
```


### Artefact C – NLU training examples (excerpt)

```
Intent: track_order
- “Where is my package?”
- “Where’s my policy?”
- “Did you send my stuff?”
- “Is my claim already done?”

Intent: refund_premium
- “I want my money back”
- “You charged me wrongly again!”
- “Refund my last payment”
- “Stop stealing from my account”

Intent: faq_opening_hours
- “When are you open?”
- “Are you open on Sunday?”
- “Can I call tomorrow?”

Notes:

German and US customers will use the same intents; we’ll add German examples later.

Swearing and emotional messages will be handled dynamically by the LLM.

For now, everything about “cancel policy” goes to refund_premium.
```

