# L01/C02/T04 — Blameless Culture & Psychological Safety

## Learning Objectives

- Define blamelessness in operational terms (and distinguish it from "no accountability")
- Run a blameless postmortem end-to-end
- Recognize when a "blameless" culture is performative versus real
- Connect psychological safety to measurable team and reliability outcomes

## Why It Matters

**Westrum (1988)** categorized organizational cultures by how information flows — and DORA's research found this single dimension predicts software delivery and operational performance:

| Type | Information Flow | Failure Treated As | Messengers Are… |
|---|---|---|---|
| Pathological (power-oriented) | Hidden, hoarded | Punished | Shot |
| Bureaucratic (rule-oriented) | Ignored, siloed | Process gap to patch | Tolerated |
| Generative (performance-oriented) | Actively shared | Learning opportunity | Trained and rewarded |

DORA's *Accelerate* research correlates a **Generative** culture with elite delivery performance. The causal claim is concrete: in a blame culture, engineers hide information to protect themselves, and you cannot operate a complex system safely on hidden information.

## Defining Blamelessness

**Blameless ≠ accountability-free.** This is the distinction every interview probes. Blamelessness means:

- We don't punish individuals for honest mistakes inside complex systems
- We focus on contributing factors, not "who screwed up"
- We assume operators acted reasonably given the information they had at the time (the **local rationality** principle from Sidney Dekker / Safety II)
- We change systems, not just exhort people to "be more careful"

Accountability survives: the team still *owns* fixing the underlying systemic gap. What disappears is *punishment*, because punishment buys you silence, and silence is the actual risk.

> Human error is a symptom of a deeper systemic problem, never the cause. If a single human action could take down production, the system — not the human — is the defect.

## The Blameless Postmortem

Standard structure:

1. **Incident Summary** — one paragraph, plain language, no jargon
2. **Impact** — customer-facing, internal, and financial (quantify it: minutes, requests, dollars)
3. **Timeline** — UTC timestamps, what was observed, what was done, what resulted
4. **Root Causes & Contributing Factors** — *plural*; real incidents have a chain, not a culprit
5. **What Went Well** — yes, capture good practice so it's reinforced
6. **What Went Wrong** — the systemic gaps
7. **Where We Got Lucky** — the near-misses that didn't hurt this time but will next time
8. **Action Items** — each with an owner, a deadline, and a ticket link

Rules of the room:
- Names appear *only* against actions taken ("Priya rolled back at 14:32"), never against judgment ("Priya should have known")
- Action items must change **systems** — add a guardrail, an automated check, a rollback — not "the engineer will be more careful"
- The document is **public to the engineering org by default**; hidden postmortems train people that failure is shameful
- Use the **Five Whys** (or a fishbone) to push past the first human action to the system gap behind it

```
Five Whys example:
  Outage: API returned 500s for 30 min.
  Why? A bad config was deployed.
  Why? It passed review.            → review didn't catch config errors
  Why? No automated config validation. → missing guardrail
  Why? The schema check was opt-in.    → safe path wasn't the default
  Why? No one owned config tooling.    → ownership gap
  → 4 systemic action items, 0 blamed humans.
```

## How to Tell If It's Performative

The word "blameless" is cheap; the behavior is expensive. Signals:

| Real | Performative |
|---|---|
| Engineers volunteer to lead postmortems | Postmortems assigned as punishment |
| Action items reduce systemic risk | Action items mandate "training" or "more care" |
| Failures discussed publicly with no consequences | Quiet conversations after the meeting |
| Senior engineers admit their own mistakes | Blame only ever flows downward |
| Lead time on action items is tracked and short | Action items rot in a backlog forever |

## Psychological Safety (Edmondson)

Amy Edmondson defines **psychological safety** as the shared belief that a team is safe for interpersonal risk-taking — that you can admit a mistake, ask a "dumb" question, or challenge a decision without humiliation. Her research (and Google's Project Aristotle, which found it the #1 predictor of effective teams) shows that high-safety teams:

- *Report* more errors (not make more) — the errors were always there; now they surface
- Learn faster, because the information flow is open
- Outperform peers on the metrics that matter

The counterintuitive trap: a low-safety team looks better on an error dashboard precisely because people hide errors. Falling reported-incident counts can mean improving safety *or* collapsing psychological safety — you have to know which.

## Building Psychological Safety as a Staff Engineer

You build it by spending your own status, repeatedly and visibly:

- **Admit your own mistakes publicly** — the most senior person in the room going first sets the ceiling for everyone else
- **Praise the act of speaking up**, even when the speaker turns out to be wrong
- **Separate "we made a bad decision" from "you are a bad engineer"** — attack the decision, never the person
- **Insist on blameless framing** in every postmortem *and* every code review
- **Frame work as learning problems, not execution problems** — "this is complex and we'll get surprised" invites flagging

## Common Mistakes

- **Equating blameless with consequence-free** — then over-correcting into "accountability" that means punishment
- **Action items that say "be more careful"** — unactionable, unmeasurable, and a tell that the postmortem skipped the system
- **Stopping at the first human action** in root-cause analysis instead of asking why the system allowed it
- **Letting only ICs admit mistakes** — if blame flows one direction, it's not blameless
- **Reading falling incident counts as pure good news** — it can mean people stopped reporting

## Best Practices

- **Write postmortems for every significant incident, blamelessly, and publish them** org-wide
- **Treat action items like product backlog** — owner, deadline, ticket, tracked lead time
- **Have the most senior person model fallibility first** in the room
- **Use a structured technique** (Five Whys, fishbone) to force past the human into the system
- **Measure culture directly** — the Westrum survey items are in DORA's research and easy to run

## Quick Refs

```
Westrum:  Pathological → Bureaucratic → Generative  (aim: Generative)
Blameless = no punishment for honest mistakes; accountability = own the fix.
Local rationality: operators acted sensibly given what they knew.

Postmortem skeleton:
  Summary · Impact · Timeline (UTC) · Causes (plural) ·
  Went well · Went wrong · Got lucky · Action items (owner+date+ticket)

Action-item test: does it change a SYSTEM? If it changes a person → reject.
Psych safety: high-safety teams report more, hide less, learn faster.
```

## Interview Prep

**Junior**: "What's a blameless postmortem?"
- A written, public review of an incident that focuses on the systemic and contributing factors rather than on who made the mistake, producing action items that fix systems instead of blaming people.

**Mid**: "Doesn't blameless mean no one is accountable?"
- No — blameless removes *punishment* for honest mistakes, but the team is still fully accountable for owning and fixing the underlying system gap; the goal is to keep information flowing, which punishment destroys.

**Senior**: "An engineer caused a 30-minute outage with a bad config. How do you handle it?"
- I'd run a blameless postmortem and ask system-level questions: why was the change approved, why didn't a test or schema check catch it, why wasn't rollback automated — each gap becomes an owned action item, because if one config change could break prod, the system is the defect, not the engineer.

**Staff**: "Your VP says 'We need accountability — someone caused this incident, what's the consequence?' How do you respond?"
- I'd reframe accountability as ownership of solving the underlying system gap, and explain — citing Westrum and the DORA culture research — that attaching consequences to individuals drives the information flow underground, which is exactly what makes the next incident more likely and harder to diagnose.

## Next Topic

→ [T05 — "You Build It, You Run It"](T05-You-Build-You-Run.md)
