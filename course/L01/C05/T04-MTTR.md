# L01/C05/T04 — Mean Time to Recovery (MTTR)

## Learning Objectives

- Define MTTR precisely (and distinguish from MTTD, MTTA, MTTF, MTBF)
- Decompose MTTR into its phases
- Identify the phase most worth investing in

## Definitions

- **MTTD** — Mean Time To Detect (when does the system / on-call know?)
- **MTTA** — Mean Time To Acknowledge (when does a human start working?)
- **MTTI** — Mean Time To Identify (when do you know what's broken?)
- **MTTR** — Mean Time To **Repair** (when is service restored to customers?)
- **MTTF** — Mean Time To Failure (between failures)
- **MTBF** — Mean Time Between Failures (similar but includes repair time)

DORA's MTTR is often shorthand for "time from incident start to service restoration".

## Decomposition

```
incident start ── MTTD ──┬── MTTA ──┬── MTTI ──┬── MTTRepair ──> resolved
                detect   ack      identify    fix
```

Each phase has different levers:

| Phase | Lever |
|---|---|
| Detect | Observability, SLO burn alerts, synthetic monitoring |
| Acknowledge | On-call hygiene, paging system reliability |
| Identify | Logs, traces, dashboards, runbooks, chat ops |
| Repair | Automation (auto-rollback, runbook actions), system architecture |

## Benchmarks (DORA 2023)

| Performer | MTTR |
|---|---|
| Elite | < 1 hour |
| High | < 1 day |
| Medium | 1 day to 1 week |
| Low | > 1 week |

## Where MTTR Usually Goes Wrong

In most teams, MTTR is dominated by **MTTI** (figuring out what's broken). Signals:

- "We knew something was wrong at 14:00 but didn't know what until 17:00"
- Runbook says "check logs" but doesn't say which logs
- 3 different teams investigate the same symptom

## Investments by Phase

| Phase | Cheapest Investment | Highest-Impact Investment |
|---|---|---|
| Detect | Add SLO + burn-rate alert | Customer-facing synthetic checks |
| Acknowledge | Redundant paging path | Healthy rotations |
| Identify | Runbooks with diagnosis trees | OpenTelemetry + trace-based debugging |
| Repair | Pre-rehearsed runbooks | Auto-rollback + automated remediation |

## Real-World Example

A team baseline:

| Phase | Time |
|---|---|
| Detect | 8 min (alert delay) |
| Ack | 3 min |
| Identify | 25 min |
| Repair | 6 min |
| **Total MTTR** | **42 min** |

Investments:
- Improve detect: alert on SLO burn instead of single-metric → 8 → 4 min
- Improve identify: trace-based queries + runbook templates → 25 → 10 min
- Auto-rollback for canary failures → repair → 2 min

New MTTR: 4 + 3 + 10 + 2 = 19 min.

## Pitfalls

- **Mean lies**: P50, P90, P99 tell the real story
- **Selection bias**: counting only major incidents inflates MTTR
- **External dependencies**: factor out vendor-caused incidents
- **Severity classification drift**: definitions matter

## Interview Prep

**Mid**: "Define MTTR and its components."

**Senior**: "Our MTTR averages 90 min. How do you decompose and investigate?"

**Staff**: "Design an MTTR-reduction roadmap for a multi-service platform with 30 services."

## Next Topic

→ [T05 — SPACE Framework for Developer Productivity](T05-SPACE-Framework.md)
