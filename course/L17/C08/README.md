# L17/C08 — SLI, SLO, Error Budgets

## Topics

- **T01 Defining Good SLIs** — Choose the right metric
- **T02 SLO Math & Rolling Windows** — How to compute
- **T03 Burn Rate Alerts** — Multi-window pattern
- **T04 Error Budget Policies** — Action when budget runs out

## Definitions

- **SLI**: Service Level Indicator — a measurement (e.g., success ratio of HTTP requests)
- **SLO**: Service Level Objective — a target for the SLI (e.g., 99.9% over 30 days)
- **SLA**: Service Level Agreement — a contractual promise (usually less strict than SLO)
- **Error Budget**: 100% - SLO. The amount of "allowable badness" before consequences.

## Good SLIs

### Tied to User Experience
- Successful HTTP requests / total
- p99 latency under 200 ms
- Search results returned correctly

### Bad SLIs
- CPU utilization (irrelevant to user)
- Bytes processed per second (not customer-visible)

### The Categories
- **Availability**: ratio of successful requests
- **Latency**: requests faster than threshold
- **Quality**: response was useful (e.g., search returned non-empty)
- **Freshness**: data is recent enough
- **Correctness**: output matches expected
- **Throughput**: capacity sustained
- **Durability**: data not lost

Pick 1-3 that matter most for the user.

## Defining the SLI Precisely

Bad: "How fast is the service?"
Good:
```
SLI: Percentage of HTTP requests to /api/v1/checkout returning
     a 2xx or 3xx response within 500 ms over a rolling 30-day window
```

Specifies: metric, endpoint, success criteria, time window.

## SLO Targets

| Nines | Downtime / month |
|---|---|
| 99% | 7.2 hours |
| 99.5% | 3.6 hours |
| 99.9% | 43.2 min |
| 99.95% | 21.6 min |
| 99.99% | 4.32 min |
| 99.999% | 26 sec |

Each nine costs ~10× more to achieve. Pick the lowest that meets business need.

### Common Mistakes
- Chasing too many nines (cost vs value)
- Same SLO for all services regardless of importance
- SLO without an Error Budget Policy (no teeth)

## Error Budget

```
Error budget = 100% - SLO
99.9% SLO → 0.1% error budget
Over 30 days: ~43 minutes of allowable bad time
Or: ~1000 failed requests per 1,000,000
```

### Burning the Budget
Each failure consumes budget. When budget is gone, you've failed the SLO for the window.

## Burn Rate

How fast you'd exhaust the budget at the current rate.

```
Burn rate = current error rate / SLO error rate

E.g., SLO is 99.9% (0.001 error rate allowed)
      Current error rate is 0.005 (0.5%)
      Burn rate = 0.005 / 0.001 = 5×

A burn rate of 5× exhausts a 30-day budget in 6 days.
```

## Multi-Window Burn Rate Alerts

Google SRE pattern (SRE Workbook Ch 5):

```
Page if:
  - 1h burn rate > 14.4×  AND
  - 5m burn rate > 14.4×
  → Exhausting 30d budget in 2d; act now

Ticket if:
  - 6h burn rate > 6×  AND
  - 30m burn rate > 6×
  → Slower burn but real; investigate

(Ignore single windows — flap-filter via two windows)
```

PromQL:
```promql
- alert: ErrorBudgetBurnFast
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      / sum(rate(http_requests_total[1h]))
    ) > (14.4 * 0.001)
    and
    (
      sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m]))
    ) > (14.4 * 0.001)
  for: 2m
  labels: { severity: page }
```

Far fewer false positives than threshold alerts.

## Error Budget Policy

Defined in writing; agreed by eng, product, leadership.

```
If Error Budget is healthy (>50%):
  Normal operation; deploy frequently; experiment.

If Error Budget is below 25%:
  Slow down deploys; require extra review; focus on reliability work.

If Error Budget is exhausted (<0):
  Halt feature work; freeze deploys to bug fixes only.
  Hold blameless retros until budget restored.

If Error Budget exhausted for 2 consecutive periods:
  Escalate to leadership; major reliability investment.
```

This is the only thing that gives SLOs teeth. Without a policy, SLOs are theater.

## Composing SLOs

If service A depends on B (SLO 99.9%) and C (SLO 99.99%):

```
Max possible A availability = 99.9% × 99.99% = 99.89%
```

A's SLO can't exceed this without mitigation (caching, fallback, etc.).

Cross-service SLO management is hard. Strategies:
- Higher SLO for critical dependencies
- Cache to reduce dependency on slow systems
- Graceful degradation when deps fail

## Practical Setup

```
1. Pick top 3 user journeys (e.g., login, checkout, search)
2. Define SLI for each (success rate, latency)
3. Set SLO (start conservative, e.g., 99.5%)
4. Implement burn rate alerts
5. Write Error Budget Policy
6. Get exec/product buy-in
7. Quarterly review (raise or lower SLO based on data)
```

## Tools

- **Sloth** — generate Prometheus rules from SLO YAML
- **OpenSLO** — vendor-neutral SLO spec
- **Grafana SLO plugin**
- **Nobl9** — commercial SLO platform
- **Datadog SLOs**, **Honeycomb BubbleUp + SLO**

## Interview Themes

- "Define SLI, SLO, SLA"
- "What makes a good SLI?"
- "Walk me through multi-window burn rate"
- "Error Budget Policy — why?"
- "Compose SLOs across services"
- "Common SLI categories"
