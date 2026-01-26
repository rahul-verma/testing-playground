### Exercise 6.1 (Multi-var): Parcel Support Chatbot

You are testing a simplified parcel support chatbot that has two input fields:

- contact channel (three possible options: chat, phone, email)
- request type (three possible options: track status, ask delivery time, report problem)

| TC | channel | request type |
|---:|---------|--------------|
| 1  | chat    | track status |
| 2  | phone   | ask delivery time |
| 3  | email   | report problem |
| 4  | inv  | - |
| 5  | -| inv |

**Invalid values and partition coverage**
- For an invalid value of a given variable, keep other inputs valid and stable (to isolate the failure).
- However, do **not** claim ECP coverage for the “other variable” unless you know the system evaluates it (many systems short-circuit validation; the other field may not be processed at all).

## 6.2 Considering Constraints (Compatibility)

**Business Rule:** customers are only allowed to report a problem over the phone.  
(Formally: `requestType = report problem ⇒ channel = phone`)

Your goal here is *not* to exhaustively test all variable relationships. Your strategy is:

- Use **OFAT** for valid partition coverage: when targeting a partition of the variable-in-focus, choose **any compatible** value for the other variable(s).
- Build a **minimal** set that covers each partition at least once, while respecting the constraint.

| TC | channel | request type |
|---:|---------|--------------|
| 1  | chat    | track status |
| 2  | email   | ask delivery time |
| 3  | phone   | report problem |
| 4  | inv  | - |
| 5  | -| inv |

Notes:
- This does **not** mean that `phone + track status` is invalid. It’s simply not required for this *minimal partition-coverage* set.
- Additional valid combinations can still be tested if risk/requirements warrant them.

## Exercise 7 (Constraints can force extra valid tests)

You are testing a simplified apartment search form with two criteria:

- **floor** (ground floor; first floor; second or higher floor)
- **garden type** (no garden; small garden; large garden)

**Rule:** only apartments on the ground floor have gardens.  
(Formally: `gardenType ≠ no garden ⇒ floor = ground floor`)

Here, the constraint forces you to create additional valid tests to achieve partition coverage.

Minimal **valid ECP** set:

| TC | floor        | garden type |
|---:|--------------|-------------|
| 1  | ground floor | small garden |
| 2  | ground floor | large garden |
| 3  | first floor  | no garden |
| 4  | second+ floor| no garden |
| 5  | inv  | - |
| 6  | -| inv |

Because “small” and “large” gardens are only compatible with “ground floor”, you need two separate ground-floor tests to cover both garden partitions.

---

## What about constraint violations?

Typical violations:
- Exercise 6: `report problem` + non-phone channel
- Exercise 7: `small/large garden` + non-ground floor

Whether you test *all* violating combinations depends on what you’re trying to cover.

### Some heuristics

**H1 — If the invalid combinations are expected to behave the same (same error, same handling), test one representative per violated rule.**
- Ex 6: test **one** of {report+chat, report+email} as a representative violation.
- Ex 7: test **one** representative non-ground floor with a garden (e.g., first floor + small garden).

**H2 — If different violating combinations can produce different behavior, test one per “distinct handling path”.**
Examples of “distinct handling”:
- Different UI messages by channel (chat vs email)
- Different server routes / APIs

Then it can be justified to test:
- Ex 6: both **report+chat** and **report+email**
- Ex 7: at least one violation per floor bucket (first floor + small, second+ + large)

**H3 — If there are many options (6–7+) and you can’t do all, use constrained pairwise on VALID values, and keep a small targeted “violation suite” for constraints.**
- Pairwise is usually for valid levels (interaction sampling).
- Constraint-violation tests remain a small, separate set that verifies enforcement.

**H4 - If there are many constraints or many outcomes/actions, use decision tables as a top-up technique to ensure rule coverage and rule precedence.**
