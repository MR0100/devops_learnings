# L01/C02/T05 — "You Build It, You Run It"

## Learning Objectives

- Explain the origin and intent of the principle
- Defend it against common objections
- Implement it humanely (without burning out engineers)

## Origin

> "Giving developers operational responsibilities has greatly enhanced the quality of the services, both from a customer and a technology point of view... You build it, you run it."
> — Werner Vogels, Amazon CTO, 2006 (interviewed by Jim Gray)

The idea: if the team that builds the service also operates it, the incentive to build operable software is direct.

## What "You Run It" Actually Means

- The team is on-call for the service
- The team triages and fixes incidents
- The team owns the SLOs
- The team owns the operational backlog
- The team chooses observability tooling within platform constraints

## Common Objections (and Responses)

### "Engineers will burn out on-call"
- True if mismanaged. Mitigations:
  - On-call rotations no more than 1 week per 6 weeks
  - Quiet on-call (low page volume) as a design goal
  - Page only on customer-impacting issues
  - On-call compensation (in cash or time off)

### "Engineers don't have ops skills"
- True initially. Training, runbooks, and pairing fix it. Most modern infra is software anyway.

### "It's inefficient — let specialists handle ops"
- Mirror image: it was always inefficient to hand off; specialists are a queue.
- *Exception*: deep specialist domains (DBA tuning, network engineering) may stay separate.

### "It violates separation of concerns"
- Concerns can be separated logically without org silos. Code review, runbooks, and shared SRE consulting accomplish this.

## How to Implement (90-Day Plan)

| Phase | Activities |
|---|---|
| 0–30 days | Inventory services, define ownership, baseline incident metrics |
| 30–60 days | Build on-call rotations, train teams, deploy runbook templates |
| 60–90 days | Shift on-call, retain ops as consulting/SRE, measure DORA + page burden |

## SRE as Counterweight

Even at Google, the SRE team can *refuse* to operate a service that doesn't meet a production readiness bar. This protects the principle: dev must build for operability, or they keep on-call.

## Healthy Antibodies

- Error budget policies (slow down deploys if SLO is broken)
- Production Readiness Reviews (PRRs) before SRE accepts a service
- "Operational pain budget" — measure the human cost of operating

## Interview Prep

**Mid**: "What does 'you build it, you run it' mean?"

**Senior**: "Engineers complain on-call is brutal because the service is unreliable. What do you do?"
- Diagnose: violates the principle's intent (which should reduce burnout). Use SLOs to slow deploys, invest in reliability work, escalate to leadership with data.

**Staff**: "Defend 'you build it, you run it' against a VP who wants to centralize ops to save cost."

## Next Chapter

→ [C03 — The DevOps Lifecycle](../C03/README.md)
