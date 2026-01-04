## “What Could Go Wrong?” (and how do we catch it?)


### Goal

- Understand dependencies between chatbot components
- Think in terms of risks, impact/likelihood, and propagation
- Map risks to testing techniques and other mitigations


### Sample Component Names in an AI chatbot implementation

![Sample Chatbot Components](./img/components.jpeg)

The above image has some possible components listed:

- Channel Adapters (web, mobile, WhatsApp, etc.)
- Conversation Orchestrator
- Intelligence / Skill Layer
- NLU
- Caches / Data Stores
- Internal Dashboards
- Client Admin Dashboard
- Compliance
- Governance
- Training & Evaluation

### Exercise

**As an individual:**
- Pick one primary component. It could be representative of what you are working on currently or what is thematically the closest.
- Make a list of components from the list with it shares first degree if input/output relationship (upstream as well as downstream)

**Form a group**
Now for the related components, organise yourselves into groups are formed. Otherwise, we adjust till we have groups of 2-3 people in each team.

**As a group:**:
1.1 Create the risk profile of your own components based on what you think is the criticality of these components in the overall architecture in terms of the following quality dimensions (they can add more dimensions as they find fit.):
- Functionality (Its role in the overall functionality of the chatbot.)
- Performance
- Security
- UX
- Globalization
- Compliance with Law & Standards
- Technical Dimensions: Extensibility etc. which are critical for future business

1.2 For each quality dimension, write at least one example of a risk e.g. "NLU misclassifies intents for rare queries"

1.3 Assess the risks from the input components which are relevant for these components.

1.4 Assess the risks which a component can cause for the immediate components that they send output to.

1.5 Map these risks to methods of mitigation:
- Preventive (design, process, governance)
- Detective (tests (levels & types), monitoring, alerts)
- Corrective (fixes, regression/confirmation testing, rollbacks, etc.)

2. From the sample metrics provided in Evaluation, shortlist the metrics which can help in the above mitigation measures.
   
3. Present, based on the time available, what you found interesting in your documented output.

### A short example of a risk

#### Risk

NLU misclassifies user intent for high-stakes queries (Impact 5, Likelihood 3)

#### Risk-Type
- Self-created: Improper/Incomplete prompt, Missing Examples etc.
- Inputs: Training & Evaluation (bad data), Governance (weak guardrails), Data Stores (wrong context)
- Outputs: Conversation Orchestrator, Compliance

#### Testing ideas
- NLU test set with critical scenarios
- Adversarial testing

#### Testing Techniques
- ECP/BVA
- Decision Tables
- Exploratory Testing, Metamorphic Testing

#### Testing Levels
- Component Testing
- Acceptance Testing

#### Other mitigations
- Regression tests to look for side-effects of other changes on intent classification
- Online evaluation with canary deployment
- Clearly labeled high-risk intents
- Human-in-the-loop for specific flows
- Monitoring misclassification rates

#### Some Relevant Metrics
1. Core NLU – Intent Classification (directly relevant)
- Accuracy
- Precision
- Recall
- F1-score
2. NLU – Entities / Slots (relevant if high-stakes flows depend on slots)
- Exact Match vs Partial Match Rate
- Entity Type-level Metrics (per-slot F1 for critical slots like policy_number, amount)
- Normalization Accuracy (for things like dates, IDs, amounts in high-stakes actions)
- Out-of-Vocabulary / OOD Handling Rate (for new products/policies in those intents)
3. Fairness, Bias & Robustness (for “high-stakes” specifically)
- Performance Gap by Group (NLU accuracy/F1 across language, accent, region, etc.)
- Disparate Error Rates (false negatives/positives for high-stakes intents across groups)
- Robustness to Distribution Shifts (drop in NLU performance when traffic changes)
4. End-to-End & Drift (to see real-world impact of those misclassifications)
- Task Success Rate (per Scenario) – for flows driven by those high-stakes intents
- Recovery Success Rate – how often the system recovers after NLU errors
- Escalation Rate & Reasons – especially those triggered by low NLU confidence
- Offline / Lab Metrics vs Online / Live Metrics – comparing NLU intent metrics on test sets vs production





