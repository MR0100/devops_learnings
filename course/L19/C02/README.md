# L19/C02 — Reliability Math

## Topics

- **T01 Availability (the Nines)** — Quantifying uptime
- **T02 Failure Modes & MTTR/MTBF** — How failures compose
- **T03 Composing SLOs Across Services** — Multi-service math

## Availability Math

```
Availability = uptime / (uptime + downtime)
```

| Nines | Per year | Per month (30d) | Per week | Per day |
|---|---|---|---|---|
| 99% | 3.65 days | 7.2 hours | 1.68 hours | 14.4 min |
| 99.5% | 1.83 days | 3.6 hours | 50.4 min | 7.2 min |
| 99.9% | 8.76 hours | 43.8 min | 10.1 min | 1.44 min |
| 99.95% | 4.38 hours | 21.9 min | 5.04 min | 43.2 sec |
| 99.99% | 52.6 min | 4.38 min | 1.01 min | 8.64 sec |
| 99.995% | 26.3 min | 2.19 min | 30.2 sec | 4.32 sec |
| 99.999% | 5.26 min | 26.3 sec | 6.05 sec | 0.864 sec |

Each nine costs ~10× more to achieve. Past 99.99%, you fight clock skew and network jitter; past 99.999% you're fighting laws of physics.

## Cost vs Reliability

Approximate engineering investment:
- 99.5% → standard practice (HA components, monitoring)
- 99.9% → multi-AZ, automated failover, on-call
- 99.95% → SRE team, error budget, sophisticated testing
- 99.99% → multi-region, cells, custom infrastructure
- 99.999% → very few products need this

## Pick the Right Target

Anchor to **user perception** + **business cost**:
- E-commerce checkout: 99.95% (downtime = lost orders)
- Internal HR tool: 99% (annoying but tolerable)
- Pacemaker firmware: 99.9999%+ (life-critical)
- Photo sharing: 99.9% (users tolerate)

## MTTR and MTBF

- **MTTR** (Mean Time To Recovery): time from incident start → resolved
- **MTBF** (Mean Time Between Failures): typical gap between incidents
- **MTTD** (Mean Time To Detect): incident start → first alert
- **MTTI** (Mean Time To Investigate): alert → root cause identified

```
Availability ≈ MTBF / (MTBF + MTTR)

If MTBF = 30 days, MTTR = 30 min:
30 days = 43200 minutes
Availability = 43200 / (43200 + 30) = 99.93%
```

You can improve availability by:
- Increasing MTBF (fewer failures)
- Decreasing MTTR (faster recovery)

Often easier to decrease MTTR. Build automated rollback, runbooks, observability.

## Failure Modes

### Serial vs Parallel Components

**Serial (any one fails = system fails)**:
```
A (99.9%) → B (99.9%) → C (99.9%)
P(system up) = 0.999³ = 99.7%
```

Worse than the weakest component.

**Parallel (redundant; both fail = system fails)**:
```
A (99.9%)
   } If either up, system up
A' (99.9%)

P(system up) = 1 - (0.001 × 0.001) = 1 - 0.000001 = 99.9999%
```

Two nines bought via redundancy.

### Cell Pattern

```
[ Cell 1 (1/10 of users) ]
[ Cell 2 (1/10 of users) ]
...
[ Cell 10 (1/10 of users) ]
```

Cell failure = 1/10 user impact, not 100%. Used heavily at Amazon and others.

## Composing SLOs

If A depends on B and C:
```
A_max = B_SLO × C_SLO
```

Example: A needs 99.9%; depends on B (99.9%) and C (99.99%).
```
A_max = 0.999 × 0.9999 = 0.9989 = 99.89%
```

A can't hit its target. Solutions:
- Cache responses (reduce dep on B)
- Fallback path when B unavailable (graceful degradation)
- Make A async (eventual consistency)
- Increase B's SLO (cost!)

## Concurrent Requests

```
P(at least one of N requests succeeds) = 1 - (1 - p)^N
```

If p = 99.9% per call, and you make 10 parallel calls and need all to succeed:
```
P(all succeed) = 0.999^10 = 99.0%
```

So 10 calls to a 99.9% service has 99.0% success rate. Two nines worse than individual call.

Implication: hide some failures (cache, retry, fallback) to maintain composed reliability.

## Tail Latency Matters

If p99 latency = 100 ms, and you fan out to 100 services:
```
P(at least one slow) ≈ 1 - 0.99^100 = 63%
```

63% of requests have ≥1 slow leg. Hedge requests, use canceller, set tight timeouts.

## Practical Calculations

### How Many Failures Allowed?
99.9% over 30 days = 43 min downtime allowed.

If you have 100K requests/day, with 99.9% success = 100 failures/day allowed = 3000 errors/30d.

### Burn Rate
Right now, what error rate would burn entire budget in time T?
```
Burn rate × SLO error rate × time = budget
```

For 99.9% over 30 days, budget = 0.001 × 30d = 43 min.
To burn in 2 days at constant rate: 43 min / 2 days = 14.4× burn rate.

This is the 14.4 number in Google SRE burn-rate alerts.

## Interview Themes

- "Math: 99.9% across 3 deps each 99.9%?"
- "Why is MTTR easier to improve than MTBF?"
- "Cell architecture — what does it solve?"
- "Tail latency at fan-out — strategies"
- "Pick a reliability target — how?"
