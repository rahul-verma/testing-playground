## Evaluation

Various evaluation metrics exist across the span of components and their purpose.

The key thing to keep in mind is - "Am I the one responsible for the quality of X, or someone else is (e.g. a vendor driven by promises in contracts, or when you choose something based on external reputed benchmarks.)

Your exercise:
1. Pick a few metrics which you already measure and are critical in your opinion. Share interesting stories from your work.
2. Pick a few metrics which you aren't measuring but they appear interesting to you for future work.
3. Categorize metrics into Classical AI metrics (e.g. classification/regression) vs LLM/domain-specific metrics.
4. Identify new test ideas from the metrics which you'll try.
5. Identify training/test data expansion opportunities.

**Note**
You might be able to notice something which is not related to your own work. It could be an important piece of information for someone you know in your team/your org. Take a note of that separately.

![Architecture](./img/arch.png)

## 1. Components (with containment)

### Compliance & Security Context
- **GDPR EU**
- **Insurance / Finance Sectoral Regulations**
- **PII Handling & Consent incl. call recording**
- **Strict Auditability & Traceability**

### Governance & Observability
- **Central Logging & Monitoring**
- **Metrics & Dashboards**
- **Audit Logs for agents, prompts, routing**

### Channel Adapters
- **Web Chat Widget**
- **Phone IVR + ASR/TTS**

### Conversation Orchestrator
- **Dialogue State & Routing / Handoff**

### Intelligence Layer
- **Skills**
  - **FAQ / Knowledge Skill**
  - **Refund Skill**
  - **Order Tracking Skill**
- **NLU / LLM**

### Backend Integrations
- **Billing REST API**
- **Claims REST API**
- **CRM REST API**
- **OMS REST API**
- **Tracking Provider REST API**
- **Rule Engine Policy Logic**
- **Caches & Data Stores for sessions, partial results**

---

## 2. Inter-relationships (as shown by arrows / labels)

### Regulatory / governance relationships

| From | To | Relationship |
|------|----|--------------|
| Compliance & Security Context | Governance & Observability | **“governs”** – regulations drive logging, metrics, and audit capabilities. |
| Compliance & Security Context | Conversation Orchestrator | **“applies to”** – orchestrator behavior must respect GDPR, sector rules, PII handling, auditability. |

---

### Channel → Orchestrator → Intelligence

| From | To | Relationship |
|------|----|--------------|
| Web Chat Widget (Channel Adapters) | Dialogue State & Routing / Handoff | User chat messages are passed into the dialogue/orchestration core. |
| Phone IVR + ASR/TTS (Channel Adapters) | Dialogue State & Routing / Handoff | Voice calls (after ASR/TTS) are passed into the dialogue/orchestration core. |
| Dialogue State & Routing / Handoff | Intelligence Layer – *Skills* (container) | Orchestrator invokes the appropriate skill for the current intent/task. |
| Dialogue State & Routing / Handoff | NLU / LLM | Orchestrator sends user turns (and context) to NLU/LLM for understanding / generation. |

---

### Skills ↔ Backend Integrations

| From | To | Relationship (diagram-level) |
|------|----|-----------------------------|
| FAQ / Knowledge Skill | Backend Integrations (block) | Skill calls backend/knowledge APIs to answer FAQs (arrow from skill into backend block). |
| Refund Skill | OMS REST API (within Backend Integrations) | Skill uses the OMS REST API for refund-related operations (arrow aligned with OMS REST API). |
| Order Tracking Skill | Tracking Provider REST API (within Backend Integrations) | Skill uses the Tracking Provider REST API for shipment / tracking info (arrow aligned with Tracking Provider REST API). |
| Conversation Orchestrator (right edge) | Backend Integrations (block) | Direct orchestration-level calls to backend services (arrow from orchestrator into backend block). |

(Other backend services inside the block – Billing REST API, Claims REST API, CRM REST API, Rule Engine Policy Logic, Caches & Data Stores – are shown as part of the same integration layer that these skills/orchestrations can use.)

---

### Observability relationships

| From | To | Relationship |
|------|----|--------------|
| Conversation Orchestrator | Central Logging & Monitoring | Runtime events / logs flow into the central logging system. |
| Conversation Orchestrator | Metrics & Dashboards | Orchestrator emits metrics that feed dashboards. |
| Metrics & Dashboards | Central Logging & Monitoring | Metrics component consumes/uses data from the logging system (arrow from Metrics up to Logging). |
| Metrics & Dashboards | Backend Integrations (block) | Metrics component also relies on backend data stores (arrow from Metrics down into Backend Integrations). |

Inside **Governance & Observability**, *Audit Logs for agents, prompts, routing* is shown as a dedicated component alongside logging & metrics, responsible for recording detailed, reviewable history of agent configuration and routing decisions.


## 1. NLU: Intent Classification & Entity Extraction

### 1.1 Intent Classification Metrics

**Purpose:** Measure how well the system understands *what* the user wants.

- **Accuracy**  
  - % of utterances where predicted intent = gold intent.  
  - Good for balanced datasets; not enough on its own for skewed traffic.

- **Precision (per intent + macro/micro)**  
  - Of all utterances predicted as intent *X*, how many are actually *X*?  
  - Important when false positives are costly (e.g., treating “cancel quote” as “cancel policy”).

- **Recall (per intent + macro/micro)**  
  - Of all utterances that truly belong to intent *X*, how many did we correctly detect?  
  - Important when missing an intent is costly (e.g., “complaint” not recognized).

- **F1-score (per intent, macro, micro, weighted)**  
  - Harmonic mean of precision & recall.  
  - Macro F1 highlights performance on rare intents; micro F1 is dominated by frequent ones.

- **Confusion Matrix**  
  - Matrix showing how intents get confused with each other.  
  - Critical for debugging misclassification: “track order” vs “change order” vs “return order”.

- **Top-N Accuracy (e.g., top-2, top-3)**  
  - Intent is correct if it appears in top-N predictions.  
  - Useful when downstream dialog uses disambiguation among top-N candidates.

- **Coverage / “Recognized vs Fallback” Rate**  
  - % of utterances that map to a known intent vs fallback/“I don’t understand”.  
  - Too low = poor NLU or incomplete intent set. Too high (with low accuracy) = overconfident.

- **Calibration Measures (e.g., Expected Calibration Error)**  
  - How well predicted confidence aligns with actual accuracy.  
  - Important for thresholding: “When confidence < X, escalate to human.”

---

### 1.2 Entity / Slot Extraction Metrics

**Purpose:** Measure how well the system extracts structured data (order IDs, dates, amounts, etc.).

- **Token-level Precision / Recall / F1**  
  - For NER: how well each token is labeled as part of an entity type.

- **Span-level Precision / Recall / F1**  
  - Entity is counted correct only if full span and type match (e.g., full order ID).

- **Exact Match vs Partial Match Rate**  
  - Exact: all required entities are correctly extracted.  
  - Partial: at least some entities correct, but not complete.

- **Entity Type-level Metrics**  
  - Slot-wise performance (e.g., F1 for `order_id` vs `policy_number` vs `date`).  
  - Identifies weak or ambiguous entity types.

- **Normalization Accuracy**  
  - Correctness after formatting (dates, IBANs, phone numbers).  
  - Measures transformation: user text → canonical backend format.

- **Out-of-Vocabulary / OOD Handling Rate**  
  - Performance on unseen entity values (new products, new policy types).  
  - Critical in dynamic domains.

---

## 2. ASR (Automatic Speech Recognition)

**Purpose:** Measure how accurately voice is turned into text for NLU/dialog.

- **Word Error Rate (WER)**  
  - (Substitutions + Insertions + Deletions) / Total words.  
  - Canonical ASR metric; lower is better.

- **Character Error Rate (CER)**  
  - Similar to WER but on characters; useful for IDs, codes.

- **Sentence/Utterance Error Rate**  
  - % of utterances containing any error.  
  - Highlights how often a whole turn may be compromised.

- **Domain-specific Term Error Rate**  
  - WER restricted to critical words (product names, policy types, brand names).  
  - Captures impact on business flows.

- **ASR Latency**  
  - Time from speech end to transcript availability.  
  - Important for real-time UX.

- **Robustness Metrics**  
  - Performance under noise, accent, and channel changes (e.g., ΔWER in noisy conditions).  
  - Measured via segmented test sets.

---

## 3. TTS (Text-to-Speech)

**Purpose:** Measure quality and usability of spoken responses.

- **Intelligibility Scores**  
  - Human rating of “how easy is it to understand?”.

- **Naturalness / MOS (Mean Opinion Score)**  
  - 1–5 subjective rating of voice naturalness.

- **Prosody / Expressiveness Metrics**  
  - Alignment between expected emphasis and produced emphasis.  
  - Important for sensitive situations (claims, denials, bad news).

- **Pronunciation Error Rate**  
  - Especially for entity names, product terms, foreign words.

- **TTS Latency**  
  - Time to first audio and total synthesis time.  
  - Key for responsiveness.

---

## 4. Dialogue Management & Policy / Orchestration

**Purpose:** Evaluate *conversation behavior* independent of raw ASR/NLU.

- **Task Success Rate (per Scenario)**  
  - % of conversations where the defined goal is achieved (e.g., tracking info given, refund initiated).

- **Dialog Efficiency**  
  - Average number of turns to complete a task.  
  - Lower is usually better, balanced with clarity.

- **User Effort Metrics**  
  - No. of times user repeats information or intent.  
  - No. of clarification questions from user side.

- **Recovery Success Rate**  
  - When an error occurs (misrecognition, fallback), how often the system recovers and completes the task.

- **Turn-Level Appropriateness**  
  - Expert- or model-based rating of whether each system action is appropriate given context.

- **Conversation-level Coherence**  
  - Whether the sequence of responses is logically consistent and on-topic.

- **Handoff Appropriateness**  
  - % of escalations judged “correct” by human reviewers.  
  - Captures both under-escalation and over-escalation.

---

## 5. LLM / Generative Components (Answers, Reasoning, Tool Use)

**Purpose:** Evaluate output quality of large language models / generative agents.

- **Groundedness / Factuality Metrics**  
  - % of answers fully supported by known sources (KB, backend).  
  - Hallucination rate = portion of answers with unsupported claims.

- **Helpfulness / Task Utility**  
  - Human or model-based rating of how well the answer solves the user’s problem.

- **Safety / Policy Compliance Metrics**  
  - Rate of unsafe outputs (privacy violations, regulatory violations, offensive content).  
  - Pass/fail on curated safety test sets.

- **Instruction-following Accuracy**  
  - Does the response follow constraints (e.g., language, style, format)?  
  - Binary or graded.

- **Reasoning Quality (if chain-of-thought used internally)**  
  - Correctness of multi-step reasoning (e.g., deductible calculations, condition checks).

- **Tool-Use Success Rate**  
  - For agent-style models: % of tool calls that are appropriate and succeed.  
  - Includes correct tool choice, correct parameters, correct sequencing.

- **Response Diversity**  
  - Variation across prompts/tests when diversity is desired.  
  - For support flows you often prefer *consistency* over creativity.

---

## 6. Retrieval & Knowledge Components (RAG, FAQ Search, Document QA)

**Purpose:** Evaluate how well the system finds and uses knowledge.

- **Precision@K (P@K)**  
  - Among top K retrieved passages/FAQ entries, how many are relevant?  
  - Typically P@1, P@3, P@5.

- **Recall@K**  
  - For questions with multiple relevant docs, proportion retrieved in top K.

- **MRR (Mean Reciprocal Rank)**  
  - Inverse rank of first relevant document; averaged over queries.

- **nDCG (Normalized Discounted Cumulative Gain)**  
  - Measures ranking quality, rewarding relevant items at top ranks.

- **Answer Exact-Match (EM) / F1**  
  - For QA tasks: comparison of final answer vs gold answer text.

- **Knowledge Base Coverage**  
  - % of known FAQs / policy rules where at least one relevant doc is retrievable.

- **Retrieval Latency**  
  - Time to retrieve knowledge; affects end-to-end response time.

---

## 7. Routing & Classification Components (Channel, Department, Priority)

**Purpose:** Evaluate decisions like which queue/team, which channel, which language.

- **Routing Accuracy**  
  - % of cases routed to the correct department or skill queue.

- **Precision/Recall per Route/Class**  
  - Metrics for specific classes (complaint vs sales vs claims vs tech support).

- **Escalation Route Correction Rate**  
  - % of escalated cases re-routed by humans (signals misrouting).

- **Queue Balancing Metrics**  
  - Load distribution across queues vs target distribution.

- **Priority Compliance**  
  - How often priority labels (VIP, urgent) are correctly assigned and respected.

---

## 8. ML for Voice/Channel/UX Personalization

**Purpose:** Evaluate models that personalize responses, flows, or offers.

- **CTR / Engagement Metrics**  
  - Click-through rate, acceptance rate, follow-up rate on recommendations.

- **Lift vs Baseline**  
  - Improvement in conversion or engagement over control group.

- **Exploration vs Exploitation Ratios**  
  - For bandit-style strategies; ensure sufficient exploration without harming UX.

- **User Satisfaction Proxies**  
  - Difference in abandonment, AHT, CSAT between personalized vs non-personalized flows.

---

## 9. Fairness, Bias & Robustness Metrics

**Purpose:** Ensure consistent quality and fairness across different user groups.

- **Performance Gap by Group**  
  - Accuracy, F1, WER, etc., broken down by language, accent, region, etc.

- **Disparate Error Rates**  
  - False positive / false negative rates across groups.

- **Fairness Metrics (e.g., Equalized Odds, Demographic Parity)**  
  - Depending on use case and regulatory context.

- **Robustness to Distribution Shifts**  
  - Performance delta when deployed to new channels, domains, or seasons (e.g., Black Friday).

---

## 10. End-to-End Quality & Business Metrics

### 10.1 Service & Contact-Center Metrics

- **Containment Rate (Self-Service Rate)**  
  - % of contacts fully handled by AI without human escalation.

- **Escalation Rate & Reasons**  
  - % of conversations escalated; categorized by reason (low confidence, policy, user request, etc.).

- **Average Handling Time (AHT)**  
  - Time from first user message/call start to resolution.  
  - Breakdown: AI-only, AI+human, human-only.

- **First Contact Resolution (FCR)**  
  - % of cases solved in a single interaction.

- **Abandonment Rate**  
  - % of users dropping out before resolution.

- **Transfer Rate (Human ↔ Human)**  
  - AI → human → other human transfers; high rates suggest routing or understanding issues.

---

### 10.2 User Experience & Satisfaction Metrics

- **CSAT (Customer Satisfaction Score)**  
  - Typically 1–5 or 1–10 rating post-interaction.

- **NPS (Net Promoter Score)**  
  - Overall loyalty/advocacy measure for the service/brand.

- **User Effort Score**  
  - Self-reported or inferred (“It was easy to resolve my issue”).

- **Sentiment Trajectory**  
  - Change in sentiment from start to end of conversation.

- **Expert UX Ratings**  
  - Human evaluation of clarity, politeness, empathy, appropriateness.

---

### 10.3 Safety, Compliance & Risk Metrics

- **Compliance Violation Rate**  
  - % of interactions lacking required disclosures or violating rules.

- **Sensitive Action Error Rate**  
  - Incorrect or unsafe actions on high-risk operations (large refunds, cancellations, policy changes).

- **PII Exposure Incidents**  
  - Count/rate of PII leakage (by component, by channel).

- **Auditability & Traceability Coverage**  
  - % of interactions with complete logs, decision traces, and associated configuration versions.

---

### 10.4 Operational & Performance Metrics (ML-Adjacent)

- **End-to-End Latency per Channel**  
  - Time from user message/speech to system reply; broken down by component (ASR, NLU, orchestration, retrieval, LLM, TTS).

- **Throughput & Concurrency**  
  - Max concurrent conversations within latency SLOs.

- **Error Rate & Timeout Rate**  
  - Non-2xx rates from backends and internal services.

- **Model Drift Indicators**  
  - Trends in NLU accuracy, ASR WER, task success over time.

---

## 11. Pre-Production vs Production Usage

**Offline / Lab Metrics (Pre-Prod)**  
- Accuracy, F1, WER, P@K, EM, etc.  
- Measured on curated labeled datasets, synthetic conversations, golden test suites.

**Online / Live Metrics (Prod)**  
- Containment, AHT, CSAT, violation rates, conversion, etc.  
- Measured with A/B testing, canary deployments, live logging.

**Human Evaluation Metrics**  
- Used for: helpfulness, empathy, regulatory wording, nuanced dialog quality.  
- Require structured annotation schemes and rubrics.

