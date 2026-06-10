# L19/C02/T02 — Failure Modes & MTTR/MTBF

## Learning Objectives

- Track failure metrics
- Improve recovery

## MTBF

Mean Time Between Failures:
```
MTBF = total_uptime / number_of_failures
```

For 10 failures in 100 days uptime: MTBF = 10 days.

Higher = better.

## MTTR

Mean Time To Recover:
```
MTTR = total_downtime / number_of_failures
```

For 10 failures, 50 min downtime: MTTR = 5 min.

Lower = better.

## MTTD

Mean Time To Detect:
```
MTTD = total_detection_lag / failures
```

How long between failure starts and discovery.

Lower = better.

## MTTA

Mean Time To Acknowledge:
```
MTTA = total_ack_lag / pages
```

Time from page to engineer ack.

Lower = better (5 min target).

## MTTI

Mean Time To Investigate.

## MTTF

Mean Time To Failure (one-shot devices).

## Availability

```
Availability = MTBF / (MTBF + MTTR)
```

Example: MTBF 100 hr, MTTR 1 hr:
```
100 / 101 = 99%
```

Higher MTBF + lower MTTR = higher avail.

## Improving Each

### MTBF (reduce failures)
- Better testing
- Chaos engineering
- Code quality
- Code review
- Architecture
- Resilience patterns

### MTTR (recover faster)
- Auto-rollback
- Auto-healing (K8s)
- Better monitoring
- Runbooks
- On-call training
- Game days

### MTTD (detect faster)
- Monitoring coverage
- Synthetic checks
- Alert thresholds

### MTTA (ack faster)
- Better paging
- Clear escalation
- Healthy on-call

## DORA Metrics

Industry standard:
- Deployment frequency
- Lead time for changes
- Change failure rate
- MTTR (Time to restore)

For: DevOps maturity.

## Failure Modes

### Hardware
- Disk
- Network
- Power

Mitigation: replicas, multi-AZ.

### Software
- Bugs
- Memory leaks
- Race conditions

Mitigation: testing, gradual rollout.

### Capacity
- Disk full
- CPU saturated
- Memory exhausted

Mitigation: autoscale, alerts.

### Configuration
- Wrong setting
- Drift

Mitigation: IaC, GitOps.

### Human
- Wrong command
- Skipped step

Mitigation: automation, sandboxes.

### Cascading
One failure → many.

Mitigation: circuit breakers, bulkheads.

### Dependent
External service down.

Mitigation: retries, fallbacks.

## Failure Mode Analysis

For each failure:
- Why?
- How detected?
- How recovered?
- How to prevent?

For: postmortem.

## FMEA

Failure Mode Effects Analysis:
- List potential failures
- Severity, probability, detection
- Score
- Prioritize mitigation

For: proactive.

## Track

```
Per service:
  MTBF: 30 days
  MTTR: 15 min
  MTTD: 2 min
  MTTA: 4 min
```

Trend: improving?

## Anti-Patterns

### Long MTTR
- No runbook
- Unknown system
- Poor monitoring

### Long MTTD
- No alerts
- Wrong thresholds
- Customer reports first (bad)

### Short MTBF
- No testing
- Skip postmortems
- Repeat failures

## Recovery Patterns

### Fail Fast
Detect quickly; act.

### Fail Open
Default to allow; for non-critical.

### Fail Closed
Default to deny; for security.

### Graceful Degradation
Reduced features; core works.

### Bulkhead
Isolate failures.

### Circuit Breaker
Stop calling failing service.

## DR Metrics

### RPO
Recovery Point Objective: data loss tolerable.

### RTO
Recovery Time Objective: time to recover.

(See L27.)

## Best Practices

- Track metrics
- Goal-set
- Postmortem each
- Action items
- Trend reports

## Common Mistakes

- No tracking
- Only count outages
- Same root cause repeatedly
- No action items

## Quick Refs

```
Availability = MTBF / (MTBF + MTTR)
MTBF: increase (less failures)
MTTR: decrease (faster recovery)
MTTD: decrease (faster detection)
MTTA: decrease (faster ack)

DORA:
- Deploy frequency
- Lead time
- Change failure rate
- MTTR
```

## Interview Prep

**Junior**: "MTTR vs MTBF."

**Mid**: "DORA metrics."

**Senior**: "Improve metrics."

**Staff**: "Reliability KPIs."

## Next Topic

→ [T03 — Composing SLOs Across Services](T03-Composing-SLOs.md)
