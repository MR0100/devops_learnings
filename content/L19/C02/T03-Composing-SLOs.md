# L19/C02/T03 — Composing SLOs Across Services

## Learning Objectives

- Compose SLOs
- Account for dependencies

## Problem

User-facing service depends on N internal services.

User availability:
```
≤ min(dependencies)
```

Or product:
```
≈ product of independent dependencies
```

## Math

Independent failures:
```
P(all up) = P(A) × P(B) × P(C)
```

For 99.9% each, 3 chained:
```
0.999^3 = 99.7%
```

For 10 chained:
```
0.999^10 = 99.0%
```

For 100:
```
0.999^100 = 90.5%
```

Compounds.

## Implications

If user wants 99.9%:
- Each dep must be > 99.9% (much higher)
- Or fewer deps
- Or fallbacks

## SLO Hierarchy

```
User SLO: 99.9%
   └─ Frontend SLO: 99.95%
       └─ Backend SLO: 99.95%
           └─ DB SLO: 99.99%
           └─ Cache SLO: 99.99%
       └─ Auth SLO: 99.99%
```

Each layer: tighter SLO to compose.

## Compute Required

For user 99.9%:
- Single dep at 99.95% (some buffer)
- Two deps: each 99.98%
- 10 deps: each 99.99%+

## Reduce Dependencies

Architectural choices:
- Cache reads (don't hit DB)
- Async writes (queue, retry later)
- Local fallback
- Circuit breakers

For: reduce dependency count.

## Fallbacks

If service down:
- Use cached data
- Show default
- Skip non-essential

For: improve effective availability.

```
P(user up) = P(critical_deps) + P(fallback) × (1 - P(critical_deps))
```

Effective higher.

## Critical vs Non-Critical

Auth: critical (no fallback).
Recommendations: not critical (skip if down).

For: design distinguishes.

## Latency Budget

Similar to availability budget:
- User-facing: 100 ms p99
- Each service: smaller budget

```
100ms total = 30ms frontend + 50ms backend + 20ms DB
```

For: chained budgets.

## Latency Math

p99 of pipeline:
```
p99_total ≈ sqrt(sum of squared service p99s)
```

(Not literal; depends on parallelism.)

For: rough estimate.

## Multi-Region

Region A 99.9% AND Region B 99.9%:
```
1 - (1 - 0.999)(1 - 0.999) = 99.9999%
```

Active-active multi-region: massive uplift.

## DNS Failover

For: multi-region with failover.

Time to detect + DNS TTL:
- 30s TTL + 30s detect = 1 min
- Customer experience: 1 min outage

For: real-world matters.

## Tracking Dependencies

For each service:
- Direct dependencies
- SLO of each
- Computed required SLO

Doc.

## SLO Negotiation

Service A wants 99.95% user SLO.
Dependency B promises 99.9%.

Either:
- A invests in resilience (fallback)
- B improves SLO

For: discussion + action.

## Service Catalog

List:
- Service
- SLO
- Owner
- Dependencies

For: track.

## Internal SLAs

Between teams:
- Backend team to frontend team
- DB team to backend
- Specific commitments

## Composite SLI

For user journey (multiple services):
```
"User can checkout" = frontend up AND backend up AND payment up
```

Compute as one SLI:
```promql
(frontend_up AND backend_up AND payment_up) / total_attempts
```

For: user-perspective metric.

## Real-User SLO

Tracks user-visible outcomes:
- Pages loaded
- Checkouts complete
- Searches successful

Not internal.

## Examples

### Simple
Service has 2 deps.
- Each 99.99%
- Compose: 99.98%
- User SLO: 99.9% (with buffer)

### Complex
Service has 10 deps (some critical, some not).
- Critical: must be up
- Non-critical: fallback exists

Compute effective.

## Best Practices

- Map dependencies
- SLO per service
- User SLO ≤ critical chain
- Fallbacks for non-critical
- Communicate SLOs
- Update on architecture change

## Common Mistakes

- Ignore dependencies
- Promise same SLO as user
- No fallbacks
- Don't update on architecture change

## Tooling

- Service catalog (Backstage)
- Dependency map (Datadog, Honeycomb)
- SLO tracker

## Quick Refs

```
N deps: 0.999^N for availability
SLO of dep > SLO of user (composition)
Fallback: improve effective
Critical: no fallback
```

## Interview Prep

**Junior**: "If a service depends on two backends at 99.9% each, what's its ceiling?" — For independent dependencies you multiply, so 0.999 × 0.999 ≈ 99.8% is the best the dependent service can do before adding any resilience.

**Mid**: "Why must a dependency's SLO be higher than the user-facing SLO?" — Because availability compounds down the chain — ten dependencies at 99.9% give only ~99.0% — so to hit a 99.9% user SLO each critical dependency must be tighter (often 99.99%+) or you must cut the number of dependencies.

**Senior**: "How do you hit a user SLO that the raw dependency math won't allow?" — Distinguish critical from non-critical dependencies and add fallbacks for the non-critical ones (cached data, defaults, skipping features), since a fallback raises effective availability above the naive product; for critical paths like auth you instead invest in redundancy or renegotiate the dependency's SLO.

**Staff**: "How do you manage SLO composition across an org?" — Maintain a service catalog mapping each service's SLO, owner, and dependencies, derive required dependency SLOs from the user-facing target, formalize them as internal SLAs between teams, and re-run the composition whenever architecture changes — using multi-region active-active where the 1 − (1−a)(1−b) uplift is worth it.

## Next Topic

→ Move to [L19/C03 — On-Call](../C03/README.md)
