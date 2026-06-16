# L01/C02/T05 — "You Build It, You Run It"

## Learning Objectives

- Explain the origin and intent of the principle
- Defend it against the common objections (on-call burden, missing skills, efficiency)
- Implement it humanely, without burning engineers out
- Recognize the antibodies (SRE, error budgets, PRRs) that keep the principle healthy

## Origin

> "Giving developers operational responsibilities has greatly enhanced the quality of the services, both from a customer and a technology point of view... You build it, you run it."
> — Werner Vogels, Amazon CTO, 2006 (interviewed by Jim Gray for ACM Queue)

The core mechanism is an **incentive feedback loop**: if the team that builds a service also carries the pager for it, the incentive to build *operable* software becomes direct and personal. The engineer who writes a noisy alert or a flaky retry is the one woken at 3 a.m. by it. Operability stops being someone else's problem.

This is the organizational expression of the Three Ways (T02): it shortens the Feedback loop from "Ops files a ticket weeks later" to "the author feels the pain tonight."

## What "You Run It" Actually Means

Ownership is concrete and total within platform constraints:

- The team is **on-call** for the service it builds
- The team **triages and fixes** its own incidents
- The team **owns the SLOs** and the error budget
- The team owns the **operational backlog** (toil reduction, reliability work, capacity)
- The team **chooses observability and tooling** within the guardrails the platform team provides

What it is *not*: every team reinventing infrastructure. A platform team (see L01/C04) provides the paved road; product teams run *their service* on it, not the whole stack.

## Common Objections (and Responses)

### "Engineers will burn out on-call"

True if mismanaged — and mismanagement is common. Mitigations:
- On-call rotations no more frequent than ~1 week in 6 (a sustainable ratio needs ≥6 responders)
- **Quiet on-call as a design goal** — a target like ≤2 pages per shift; if you exceed it, that's a reliability bug, not a fact of life
- Page only on customer-impacting, actionable conditions — alert on symptoms (SLO burn), not causes
- On-call compensation, in cash or time off, and protected recovery after a rough night

### "Engineers don't have ops skills"

True initially. Training, runbooks, pairing, and shadowing fix it within a quarter. And most modern infrastructure *is* software — IaC, Kubernetes manifests, observability config — so the skill gap is smaller than it looks for a competent engineer.

### "It's inefficient — let specialists handle ops"

This is the mirror image of the real cost: a handoff to specialists creates a *queue*, and queues are where lead time goes to die. The "efficiency" of specialization is local; the system gets slower.
- *Legitimate exception*: genuinely deep specialist domains — DBA performance tuning, network engineering, kernel work — can stay separate as complicated-subsystem or platform functions.

### "It violates separation of concerns"

Concerns can be separated *logically* without separating them *organizationally*. Code review, runbooks, golden paths, and on-demand SRE consulting achieve the separation of concerns without rebuilding the dev-vs-ops wall.

## How to Implement (90-Day Plan)

| Phase | Activities |
|---|---|
| 0–30 days | Inventory services, assign clear ownership, baseline incident + page metrics, write the on-call charter (rotation, comp, escalation) |
| 30–60 days | Build rotations, train teams, deploy runbook + alert templates, define SLOs per service, set up paging tooling |
| 60–90 days | Shift on-call to owning teams, retain SRE as consulting, measure DORA *and* page burden, run the first production-readiness reviews |

Throughout: make the platform team's paved road good enough that running a service is mostly self-service, not heroics.

## SRE as Counterweight

Even at Google, the SRE team can **refuse to operate** a service that doesn't meet a production-readiness bar — and can **hand the pager back** to the developers if the service degrades below it. This is the structural enforcement of the principle: dev must build for operability, or they keep on-call themselves. The threat of "you run it" is what makes "build it well" credible.

```
   Service health vs. PRR bar
        │
   meets bar ──► SRE may co-run / consult
        │
   below bar ──► dev team keeps the pager
                 until reliability work lands
   → on-call burden is the forcing function for operability
```

## Healthy Antibodies

These keep the principle from decaying into "devs just suffer more on-call":

- **Error-budget policy** — when a service burns its budget, *feature work stops* and reliability work takes priority; this gives the team leverage to fix root causes instead of being told to ship faster
- **Production Readiness Reviews (PRRs)** — a checklist a service must pass (SLOs, runbooks, dashboards, rollback, capacity) before it ships or before SRE co-owns it
- **Operational pain / toil budget** — explicitly measure the *human* cost of operating a service (page volume, toil hours) and treat a high number as a defect to fix, not a badge of honor

## Common Mistakes

- **Shifting on-call without shifting authority** — making teams carry pagers but not letting them stop feature work to fix reliability
- **No error-budget policy** — on-call becomes pure suffering with no lever to improve the service
- **Paging on causes, not symptoms** — noisy, non-actionable alerts that train engineers to ignore the pager
- **Thin rotations** — a 1-in-3 rotation guarantees burnout; you need enough responders for a sustainable ratio
- **No platform underneath** — every team reinventing ops from scratch instead of running on a paved road

## Best Practices

- **Pair the pager with the power** — the team that runs it can prioritize reliability work via an error-budget policy
- **Design for quiet on-call** — alert on SLO burn (symptoms), set a page-per-shift target, treat overruns as bugs
- **Compensate and protect on-call** — cash or time off, plus recovery time after bad shifts
- **Gate with PRRs** — no service goes live (or gets SRE co-ownership) without passing a readiness bar
- **Measure the human cost** — track toil and page burden alongside DORA, and fund the work to drive it down

## Quick Refs

```
Principle: the team that builds a service carries its pager → operability becomes self-interest.
Origin: Werner Vogels, Amazon, 2006.

Humane implementation:
  ≥6 responders · quiet on-call (alert on symptoms/SLO burn) · comp + recovery
Antibodies:
  Error-budget policy (stop features when budget burns)
  PRR (readiness bar before launch / SRE co-own)
  Toil budget (measure & fund down the human cost)
SRE counterweight: can hand the pager back if a service is below bar.
```

## Interview Prep

**Junior**: "What does 'you build it, you run it' mean?"
- The team that builds a service also operates it — carries the pager, owns the SLOs and the incidents — so the incentive to build reliable, operable software is direct.

**Mid**: "Why does it improve software quality?"
- Because it closes the feedback loop: the engineer who writes a flaky retry or a noisy alert is the one paged at 3 a.m., so operability becomes self-interest instead of someone else's problem.

**Senior**: "Engineers complain on-call is brutal because the service is unreliable. What do you do?"
- That's a violation of the principle's intent, which should *reduce* burnout — I'd introduce an error-budget policy so reliability work can preempt features, fix the alerts to page only on actionable symptoms, ensure the rotation is staffed for a sustainable ratio, and escalate to leadership with page-burden data if the reliability investment isn't funded.

**Staff**: "Defend 'you build it, you run it' against a VP who wants to centralize ops to save cost."
- Centralizing ops reintroduces the handoff queue that inflates lead time and severs the feedback loop that keeps services operable, so the apparent saving is offset by slower delivery and more incidents; I'd propose keeping ownership with the teams, backed by a platform team for leverage and SRE for consulting, and prove it with DORA plus toil metrics rather than headcount math.

## Next Chapter

→ [C03 — The DevOps Lifecycle](../C03/README.md)
