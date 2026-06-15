# L19/C02/T01 — Availability (The Nines)

## Learning Objectives

- Compute availability
- Compare service levels

## Definition

```
Availability = Uptime / (Uptime + Downtime)
```

E.g.:
```
1440 min/day uptime / 1440 = 100%
```

## The Nines

| Nines | Uptime % | Downtime/year | Downtime/month |
|---|---|---|---|
| 1 | 90% | 36.5 days | 73 hr |
| 2 | 99% | 3.65 days | 7.3 hr |
| 3 | 99.9% | 8.77 hr | 43.8 min |
| 4 | 99.99% | 52.6 min | 4.4 min |
| 5 | 99.999% | 5.26 min | 26.3 sec |
| 6 | 99.9999% | 31.5 sec | 2.6 sec |

## Typical SLOs

- Internal: 99.5-99.9%
- Production: 99.9-99.95%
- Critical: 99.99%
- Mission-critical: 99.999% (rare)

## SLA vs SLO

SLA: customer contract.
SLO: internal target.

Usually: SLO < SLA (buffer).

E.g.:
- SLA: 99.9%
- SLO: 99.95% (buffer for customer penalty)

## Cost

Each "9": ~10× cost.

- 99.9%: standard
- 99.99%: HA infra, multi-AZ
- 99.999%: multi-region, active-active

Justify per service.

## Measurement Window

```
99.9% over 28 days
99.9% over 365 days
```

Different. Specify.

For: rolling 28-day common.

## Calculation

```
Window: 28 days = 40320 min
SLO: 99.9% = 40,279 min uptime allowed
Budget: 40320 - 40279 = ~40 min downtime
```

## Outage Accounting

What counts as outage?
- Total downtime
- Partial (some users)
- Degraded (slow but works)

Define clearly.

## Brief vs Sustained

```
Brief (< 1 min) × many = high count, low budget
Sustained (60 min) × 1 = same budget
```

Both count.

## Real-World

Cloud providers:
- AWS regional: 99.99%+
- Azure: similar
- GCP: similar

But: composing services drops.

## Composing

If A depends on B + C:
```
A_avail = B_avail × C_avail × ...
```

99.9% × 99.9% = 99.8%.

For chained: budget shrinks.

## Single Point of Failure

DB single instance: 99.9% (best).
Multi-AZ DB: 99.99%.
Multi-region: 99.999%.

Each layer: more reliability.

## Dependencies

If app uses 10 services @ 99.9%:
```
0.999^10 = 99.0%
```

10× drop from chain.

Mitigations:
- Independent service failures
- Circuit breakers
- Fallbacks
- Local cache

## Real Availability

For complex systems:
- Hard to measure exactly
- Use multiple SLIs (avail, latency)
- Weighted

## Measuring

```promql
1 - (sum(downtime) / sum(total_time))
```

Or per-request:
```
non-5xx / total
```

(Per-request approach: common.)

## Time-Based vs Request-Based

- Time-based: "down" / "up" over time
- Request-based: % successful

Modern: request-based.

## Active vs Passive

- Active monitoring: synthetic checks
- Passive: real traffic

Both useful.

## Status Pages

Public status:
- statuspage.io
- statuspal
- AWS Service Health

For: customer transparency.

## Tradeoffs

For 99.999% (5 min/year):
- Multi-region
- Database replication
- No single point
- Expensive

Worth it for critical services only.

## Best Practices

- SLO per service
- Justify each "9"
- Composite for chains
- Measure consistently
- Public for SLA

## Common Mistakes

- 99.999% for all (impossible)
- No SLO (no target)
- Different measurement (inconsistent)
- Ignore dependencies (overpromise)

## Quick Refs

```
99%:    3.6 days/year
99.9%:  8.8 hr/year (43 min/mo)
99.99%: 52 min/year (4.4 min/mo)
99.999%: 5 min/year (26 sec/mo)
```

## Interview Prep

**Junior**: "What does 'three nines' mean in downtime?" — 99.9% availability allows about 8.8 hours of downtime per year, or roughly 43 minutes per month; each added nine cuts the allowed downtime by 10x.

**Mid**: "Why is each additional nine so expensive?" — Every nine costs roughly 10x more because you move from single-AZ to multi-AZ to multi-region active-active, and the marginal user value of going from 99.9% to 99.99% rarely justifies that cost outside critical services.

**Senior**: "How does composing dependencies affect availability, and how do you measure it?" — Independent chained dependencies multiply, so ten services at 99.9% yield only 0.999^10 ≈ 99.0%; you counter it with caching, circuit breakers, and fallbacks, and you measure availability request-based (good requests / total) rather than crude time-based up/down.

**Staff**: "How do you set an availability strategy across a portfolio?" — Tier services by business value and assign SLOs accordingly, keep the SLO below the customer-facing SLA as a buffer against penalties, account for dependency composition when promising user-facing numbers, and reserve expensive multi-region active-active only for the few services whose impact justifies five nines.

## Next Topic

→ [T02 — Failure Modes & MTTR/MTBF](T02-Failure-Modes-MTTR.md)
