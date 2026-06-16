# L25/C04/T01 — Planning a Game Day

## Learning Objectives

- Plan a Game Day end-to-end: scenario, hypothesis, scope, roles, comms, abort
- Right-size blast radius and define explicit stop conditions before execution
- Produce a written plan that a facilitator can run without improvising

A Game Day is a scheduled, full-team chaos exercise (2–4 hours): inject a
realistic failure, let on-call respond, learn. The planning phase is where the
exercise succeeds or fails — a vague plan produces a chaotic, un-learnable day.
(Foundations covered in L19/C07/T03 — this is the chaos-specific application.)

## The Plan (7 Steps)

```
1. Scenario   → which realistic failure?
2. Hypothesis → what do we predict happens? (testable, with numbers)
3. Scope      → blast radius: one service / cross-team / full org
4. Roles      → facilitator, IC, responders, observers, scribe
5. Schedule   → off-peak, deploy-freeze window, pre-brief date
6. Comms      → "DRILL" labeling, who to notify, who NOT to escalate
7. Rollback   → stop conditions + tested abort path
```

Each step is a written artifact. If it isn't written down, it doesn't exist on
the day.

## Step 1–2: Scenario & Hypothesis

Pick a scenario that's realistic, bounded, and exercises an *untested* path.

| Scenario            | What it stresses                              |
|---------------------|-----------------------------------------------|
| DB primary failure  | Failover RTO, replica promotion, reconnection |
| Region / AZ outage  | Multi-region routing, capacity headroom       |
| Cache cluster down  | DB miss-storm, graceful degradation           |
| Bad config push     | Rollback speed, blast-radius of config        |
| Payment 500s        | Circuit breaking, retry behavior, queueing    |
| Network partition   | Split-brain prevention, leader election       |

The hypothesis must be *falsifiable* and numeric:

```
Scenario:  Primary RDS in us-east-1 fails
Hypothesis: Multi-AZ failover completes < 60s; error rate < 5% for < 90s;
            on-call is paged and verifies recovery without manual promotion.
Steady state: error rate 0.05%, p99 200ms, 5K rps
```

A hypothesis without numbers can't be falsified — and an un-falsifiable Game
Day teaches nothing.

## Step 3: Scope & Blast Radius

Start as small as the hypothesis allows. Widen across exercises, not within one.

```
blast radius = (% of fleet) × (magnitude) × (duration)

Single service ── Cross-team ── Full org / multi-region
   (start here)                    (only when mature)
```

- **Single service** — one team, one dependency, low risk. Default starting point.
- **Cross-team** — payment + checkout + cart together; coordination is the test.
- **Full org** — annual multi-region failure; everyone responds. High prep cost.

## Step 4: Roles

| Role          | Responsibility                                          |
|---------------|---------------------------------------------------------|
| Facilitator   | Triggers chaos, holds the abort, **does NOT help respond** |
| Incident Cmdr | Leads the response, delegates, owns decisions           |
| Responders    | On-call engineers + SMEs (DB, network, app)             |
| Observers     | Note timeline, confusion, missing steps, tooling gaps   |
| Scribe        | Captures decisions and timestamps for the debrief       |

The facilitator's discipline is the linchpin: if they help, the team's real
gaps stay hidden and the exercise is theater.

## Step 5: Schedule

- **Off-peak**, away from known traffic peaks and end-of-quarter loads
- Inside a **deploy freeze** — never run chaos concurrently with a release
- **Real on-call aware** but not pre-briefed on specifics (test detection)
- Pre-brief booked **1 day before**; debrief slot booked **within 24h after**

```
Week -2 : pick scenario + hypothesis, get sign-off
Week -1 : pre-brief, verify tooling + abort, capture baseline
Day  0  : execute (2–4h)
Day +1  : debrief, document, file action items
Day +90 : re-run to verify fixes landed
```

## Step 6: Pre-Brief

Held ~1 day out, with everyone except the responders' detailed knowledge of
*which* fault fires:

- Walk through plan, roles, comms channels, and the abort procedure
- Confirm materials: runbook links, dashboards, the hypothesis doc
- Q&A — surface objections now, not mid-exercise
- Confirm the steady-state baseline is captured and dashboards are live

## Step 7: Risk Management & Abort

Define stop conditions *in writing* before you start. The facilitator aborts
the instant any trips — no debate:

```
Abort if:
  - error rate > 20% sustained > 2 min
  - any real customer escalation
  - an unrelated production incident opens
  - the abort path itself looks unsafe
```

Pre-test the kill switch (`gremlin halt`, `kubectl delete <chaos>`, FIS
`stop-experiment`) *before* the exercise. An untested abort is not an abort.

## Hypothesis Document Template

```
Scenario:    <realistic failure>
Hypothesis:  <prediction with numbers — RTO, error rate, on-call behavior>
Steady state:<baseline metrics to compare against>
Method:      1. verify steady state (5 min)
             2. inject fault
             3. observe (N min, no facilitator help)
             4. resolve / abort; verify steady state restored
Abort:       <explicit stop conditions>
Roles:       <named people per role>
Comms:       <channel, "DRILL" label, notify list>
```

## Common Mistakes

- Hypothesis with no numbers → nothing to falsify, nothing learned
- Too easy ("we already know exactly what happens") → no new information
- Too realistic → real customer impact; the drill becomes an incident
- No tested abort path → escalates beyond the intended blast radius
- Facilitator helps the team → real gaps stay hidden
- Skipping the drill because the team is "too busy" → the biggest miss of all

## Best Practices

- Quarterly minimum for top-priority services; smaller monthly exercises
- Cross-functional roster — the coordination *is* part of the test
- Everything written: hypothesis, roles, comms, abort — no improvisation
- Start small; widen blast radius across exercises, never within one
- Stop the moment customers are impacted — bounded, controlled, blameless

## Quick Refs

```
Plan → Pre-brief (-1d) → Execute (day 0) → Debrief (+1d) → Re-test (+90d)

7 steps: Scenario · Hypothesis · Scope · Roles · Schedule · Comms · Rollback
Abort:   error% threshold · customer impact · real incident · unsafe path
Roles:   Facilitator (no help) · IC · Responders · Observers · Scribe
```

## Interview Prep

**Junior**: "What is a Game Day?" — A scheduled, full-team exercise that injects a realistic failure so on-call can practice responding and the team finds gaps before a real incident does.

**Mid**: "Walk me through planning one." — Define a scenario, a numeric falsifiable hypothesis, the blast-radius scope, named roles, an off-peak schedule inside a deploy freeze, a comms plan labeled DRILL, and written stop conditions with a tested abort.

**Senior**: "Why must the hypothesis be falsifiable and the facilitator not help?" — A numeric prediction is the only way the exercise can produce a pass/fail signal, and a facilitator who jumps in masks exactly the gaps the Game Day exists to expose.

**Staff**: "How do you scale Game Days across an org safely?" — Standardize the plan template and abort discipline, start every team at single-service blast radius, gate cross-team and full-org exercises behind maturity, and require action items to close before the +90-day re-test.

## Next Topic

→ [T02 — Running the Exercise](T02-Running.md)
