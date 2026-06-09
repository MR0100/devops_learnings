# L01/C02/T04 — Blameless Culture & Psychological Safety

## Learning Objectives

- Define blamelessness in operational terms
- Run a blameless postmortem
- Recognize when a "blameless" culture is performative versus real

## Why It Matters

Westrum (1988) categorized organizational cultures:

| Type | Information Flow | Failure Treated As |
|---|---|---|
| Pathological | Hidden | Punished |
| Bureaucratic | Ignored | Process gaps |
| Generative | Shared | Learning opportunity |

DORA research correlates Generative culture with elite performance.

## Defining Blamelessness

**Blameless ≠ accountability-free.** Blamelessness means:

- We don't punish individuals for honest mistakes in complex systems
- We focus on contributing factors, not "who screwed up"
- We assume operators acted reasonably given the information they had
- We change systems, not just behavior

## The Blameless Postmortem

Standard structure:

1. **Incident Summary** (1 paragraph, no jargon)
2. **Impact** (customer-facing, internal, financial)
3. **Timeline** (UTC timestamps, actions, outcomes)
4. **Root Causes & Contributing Factors** (plural)
5. **What Went Well** (yes — capture good practice)
6. **What Went Wrong**
7. **Where We Got Lucky**
8. **Action Items** (owner, deadline, ticket link)

Rules:
- Names allowed *only* for what was done; no value judgments
- Action items must address systems, not "be more careful"
- Public to the engineering org by default

## How to Tell If It's Performative

| Real | Performative |
|---|---|
| Engineers volunteer to lead postmortems | Postmortem assigned punitively |
| Action items reduce systemic risk | Action items mandate training |
| Failures discussed publicly without consequences | Quiet conversations after the meeting |
| Senior engineers admit their mistakes | Mistakes flow downward only |

## Psychological Safety (Edmondson)

The shared belief that the team is safe for interpersonal risk-taking. Edmondson's research found teams with high psychological safety:
- Make more mistakes (because they report them honestly)
- Learn faster
- Outperform their peers on the metrics that matter

## Building Psychological Safety as a Staff Engineer

- Admit your own mistakes publicly
- Praise the act of speaking up, even when wrong
- Separate "we made a bad decision" from "you are a bad engineer"
- Insist on blameless framing in every postmortem and code review

## Interview Prep

**Mid**: "What's a blameless postmortem?"

**Senior**: "An engineer caused a 30-minute outage with a bad config. How do you handle it?"
- Blameless postmortem. Focus on: why was the change approved? Why didn't the test catch it? Why didn't the rollback automate? Each gap → action item.

**Staff**: "Your VP says, 'We need accountability — someone caused this incident, what's the consequence?' How do you respond?"
- Reframe: accountability = ownership of solving the underlying system gap. Consequences attached to individuals destroy the information flow you need to operate safely. Cite Westrum.

## Next Topic

→ [T05 — "You Build It, You Run It"](T05-You-Build-You-Run.md)
