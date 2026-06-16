# L01/C05/T04 — Mean Time to Recovery (MTTR)

## Learning Objectives

- Define MTTR precisely and distinguish it from MTTD, MTTA, MTTI, MTTF, and MTBF
- Compute each metric from raw incident timestamps using the standard formulas
- Decompose MTTR into phases and identify the phase most worth investing in
- Read MTTR distributions (not just the mean) to avoid being misled by averages

## Prerequisites

The DORA four (L01/C01/T05) and a basic incident lifecycle. MTTR is the reliability-side DORA metric; the other three (DF, LT, CFR) measure flow.

## Definitions

- **MTTD** — Mean Time To **Detect** (when does the system / on-call first know?)
- **MTTA** — Mean Time To **Acknowledge** (when does a human start working?)
- **MTTI** — Mean Time To **Identify** (when do you know *what* is broken?)
- **MTTR** — Mean Time To **Recover/Repair** (when is service restored to customers?)
- **MTTF** — Mean Time To **Failure** (average uptime before a *non-repairable* unit dies)
- **MTBF** — Mean Time **Between Failures** (average full cycle: uptime + repair, for repairable systems)

DORA's MTTR is shorthand for "time from incident start to service restoration" — the customer-visible outage duration. The "R" is best read as **Recovery** (restore service), not necessarily a permanent fix; the root-cause fix can land later.

A frequent source of confusion: **MTTF** describes things you replace (a disk, a fan), while **MTBF** describes things you repair and return to service. They are not the same metric with a different name.

## The Formulas

```
MTTD  =  Σ (detect_time − incident_start)        / number_of_incidents
MTTA  =  Σ (ack_time    − detect_time)           / number_of_incidents
MTTI  =  Σ (identify_time − ack_time)            / number_of_incidents
MTTR  =  Σ (restore_time − incident_start)        / number_of_incidents

MTTF  =  Σ (operating_time_until_failure)         / number_of_failures
MTBF  =  total_operational_time                    / number_of_failures
       =  MTTF + MTTR     (for a repairable system)

Availability  =  MTBF / (MTBF + MTTR)  =  MTTF / (MTTF + MTTR)
```

Note MTTR is measured from **incident start**, not from detection — the clock includes the time you didn't even know you were down.

## Worked Numbers

**MTTF / MTBF example.** A service runs for 30 days and suffers 3 incidents. Total operational time = 720 hours; total repair time across the 3 incidents = 6 hours.

```
MTTR  = 6 h / 3            = 2 hours
MTBF  = 720 h / 3          = 240 hours
MTTF  = MTBF − MTTR        = 238 hours   (pure uptime per failure)
Availability = MTBF / (MTBF + MTTR) = 240 / 242 = 0.99173 ≈ 99.17%
```

To hit higher availability you can either **raise MTBF** (fail less often) or **lower MTTR** (recover faster). At a 240h MTBF, cutting MTTR from 2h to 20min lifts availability from 99.17% to **99.86%** — recovery speed often moves the needle more cheaply than chasing zero failures.

**The "nines" intuition** (annual downtime budget):

| Availability | Downtime / year | Downtime / 30 days |
|---|---|---|
| 99% | 3.65 days | 7.2 hours |
| 99.9% | 8.77 hours | 43.2 minutes |
| 99.95% | 4.38 hours | 21.6 minutes |
| 99.99% | 52.6 minutes | 4.32 minutes |
| 99.999% | 5.26 minutes | 25.9 seconds |

## Decomposition

```
incident start ── MTTD ──┬── MTTA ──┬── MTTI ──┬── MTTRepair ──> resolved
                detect    ack       identify    fix
└──────────────────────── MTTR (whole bar) ──────────────────────┘
```

Each phase has different levers, and they rarely respond to the same investment:

| Phase | Lever |
|---|---|
| Detect (MTTD) | Observability, SLO burn-rate alerts, synthetic / customer-facing monitoring |
| Acknowledge (MTTA) | On-call hygiene, redundant paging paths, escalation policy |
| Identify (MTTI) | Logs, traces, dashboards, runbooks with diagnosis trees, ChatOps |
| Repair (MTTRepair) | Auto-rollback, runbook automation, system architecture (cells, feature flags) |

## Benchmarks (DORA)

DORA's elite tier reports a "time to restore service" of under one hour.

| Performer | Time to restore |
|---|---|
| Elite | < 1 hour |
| High | < 1 day |
| Medium | 1 day to 1 week |
| Low | > 1 week |

## Where MTTR Usually Goes Wrong

In most teams, MTTR is dominated by **MTTI** — figuring out *what* is broken — not by the repair itself. Tell-tale signals:

- "We knew something was wrong at 14:00 but didn't know what until 17:00"
- The runbook says "check logs" but not *which* logs or *what to look for*
- Three different teams independently investigate the same symptom
- The fix, once known, took 90 seconds (a rollback) — the other 2 hours were diagnosis

This is why trace-based debugging and good runbooks usually beat faster deploy tooling: you can't repair what you can't locate.

## Investments by Phase

| Phase | Cheapest Investment | Highest-Impact Investment |
|---|---|---|
| Detect | Add an SLO + burn-rate alert | Customer-facing synthetic checks |
| Acknowledge | Redundant paging path | Healthy rotations (no alert fatigue) |
| Identify | Runbooks with diagnosis trees | OpenTelemetry + trace-based debugging |
| Repair | Pre-rehearsed runbooks | Auto-rollback + automated remediation |

## Real-World Example

A team's baseline incident profile:

| Phase | Time |
|---|---|
| Detect | 8 min (alert delay) |
| Ack | 3 min |
| Identify | 25 min |
| Repair | 6 min |
| **Total MTTR** | **42 min** |

Targeted investments:

- **Detect**: alert on SLO burn-rate instead of a single noisy metric → 8 → 4 min
- **Identify** (the dominant phase): trace-based queries + runbook diagnosis templates → 25 → 10 min
- **Repair**: auto-rollback on canary failure → 6 → 2 min

```
New MTTR = 4 (detect) + 3 (ack) + 10 (identify) + 2 (repair) = 19 min
```

A **55% reduction**, and notice the biggest single win (15 min) came from attacking the *largest* phase, MTTI — not from the cheapest-looking one.

## Reading the Distribution, Not the Mean

The "M" in MTTR hides the most operationally useful information.

- **Means lie**: one 6-hour outage and ninety-nine 5-minute blips can yield a "healthy" mean that masks a catastrophic tail. Track **P50, P90, P99** alongside the mean
- **Prefer the median for typical behavior**, the P99 for worst-case planning
- A bimodal distribution (lots of fast recoveries + a cluster of very slow ones) usually means you have two distinct failure classes that need separate runbooks

## Pitfalls

- **Mean lies** — always report P50 / P90 / P99 next to the average
- **Selection bias** — counting only SEV1s inflates MTTR; counting auto-recovered blips deflates it. State your inclusion rule
- **External dependencies** — decide explicitly whether vendor-caused outages count, and be consistent
- **Severity classification drift** — if "SEV2" quietly redefines over quarters, your MTTR trend is measuring definitions, not reality
- **Clock-start ambiguity** — from incident *start* or from *detection*? They differ by exactly MTTD. Pick one and document it
- **Goodhart's Law** — once MTTR is a target, teams resolve incidents on paper early or downgrade severity; pair it with Change Failure Rate so gaming one harms the other

## Common Mistakes

- **Optimizing the cheapest phase instead of the biggest** — shaving the 6-min repair when the 25-min identify phase owns the outage
- **Confusing recovery with root-cause fix** — MTTR ends at *service restored*; the permanent fix can follow asynchronously
- **Tracking only the mean** — no percentiles, so the painful tail is invisible to leadership
- **No agreed clock-start** — different responders measure from detection vs. incident start, making trends meaningless
- **Ignoring MTBF** — driving MTTR to zero while incidents grow more frequent; availability depends on *both*
- **Manual heroics over automation** — fixing the same incident by hand weekly instead of shipping auto-rollback

## Best Practices

- **Decompose before you optimize** — measure MTTD/MTTA/MTTI/MTTRepair separately; you can't fix a blended number
- **Attack the dominant phase** — usually MTTI; invest in tracing and diagnosis-tree runbooks first
- **Automate the recovery, not just the alert** — auto-rollback and runbook automation collapse the repair phase
- **Report percentiles** — P50 and P99 of recovery, never the bare mean, in reliability reviews
- **Pair MTTR with CFR** — to prevent gaming; fast recovery of frequent breakage is not health
- **Run game days** — rehearsed incidents expose where the clock actually goes and shrink real MTTI

## Quick Refs

```
Acronym map (in incident order):
  MTTD → detect      MTTA → acknowledge
  MTTI → identify    MTTR → recover (the customer-visible bar)
  MTTF → uptime before a non-repairable unit fails
  MTBF → full cycle  = MTTF + MTTR  (repairable systems)

Key identities:
  MTBF         = MTTF + MTTR
  Availability = MTBF / (MTBF + MTTR) = MTTF / (MTTF + MTTR)
  MTTR clock starts at INCIDENT START (includes MTTD)

Quick lever: usually MTTI dominates → invest in tracing + runbooks first.
```

## Interview Prep

**Junior**: "What is MTTR and how is it different from MTBF?"
- MTTR is the mean time to recover service after an incident starts; MTBF is the mean time between failures (uptime plus repair) — MTTR measures how fast you bounce back, MTBF measures how often you fall over.

**Mid**: "Define MTTR and its phases, and write the availability formula."
- MTTR breaks into detect (MTTD), acknowledge (MTTA), identify (MTTI), and repair, measured from incident start to service restored; availability = MTBF / (MTBF + MTTR), so cutting MTTR raises availability without reducing failure frequency.

**Senior**: "Our MTTR averages 90 minutes. How do you decompose and investigate?"
- I'd split it into MTTD/MTTA/MTTI/MTTRepair from timestamps and look at percentiles, expecting MTTI to dominate; then I'd target the largest phase — typically tracing and diagnosis-tree runbooks for identify, plus auto-rollback for repair — and verify with P50/P99, not the mean.

**Staff**: "Design an MTTR-reduction roadmap for a multi-service platform with 30 services."
- Standardize incident timestamps and SLO burn alerts across all services so MTTR is measurable and comparable, instrument every service with OpenTelemetry for trace-based MTTI reduction, ship a platform-level auto-rollback and runbook-automation capability so repair is near-instant, and govern with P50/P99 MTTR paired with Change Failure Rate to prevent gaming — sequencing the investment toward whichever phase dominates the aggregate distribution.

## Next Topic

→ [T05 — SPACE Framework for Developer Productivity](T05-SPACE-Framework.md)
