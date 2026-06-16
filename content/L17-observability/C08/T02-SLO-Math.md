# L17/C08/T02 — SLO Math & Rolling Windows

## Learning Objectives

- Compute SLO compliance
- Use rolling windows

## SLO

Service Level Objective: target for SLI.

Example:
```
99.9% availability over 28 days
```

## Error Budget

If SLO = 99.9%, error budget = 0.1%.

Per:
- Day: 0.1% × 86400 sec = 86.4 sec
- Month: 0.1% × 2.6M sec = 43.2 min

Budget for errors.

## Common Targets

| Target | Downtime/Month | Use |
|---|---|---|
| 99% | 7.2 hours | non-critical |
| 99.5% | 3.6 hours | internal |
| 99.9% | 43 min | standard |
| 99.95% | 21 min | important |
| 99.99% | 4 min | critical |
| 99.999% | 26 sec | rare |

Higher = more expensive.

## Compliance

```promql
sum_over_time(success[28d])
/
sum_over_time(total[28d])
```

Result: actual SLI over period.

If ≥ 99.9%: compliant.
Else: budget exhausted.

## Rolling Window

28-day sliding window common.

Each day:
- Today's data added
- 29-days-ago dropped

For: continuous view.

## Recording Rules

```yaml
- record: sli:availability:ratio_28d
  expr: |
    sum_over_time(
      sum(rate(http_requests_total{code!~"5.."}[5m]))[28d:5m]
    )
    /
    sum_over_time(
      sum(rate(http_requests_total[5m]))[28d:5m]
    )
```

Precomputed.

## Burn Rate

How fast budget consumed:
```
burn_rate = current_error_rate / slo_error_budget_target
```

If SLO 99.9% (0.1% error allowed), and current error 1%:
```
burn_rate = 1% / 0.1% = 10x
```

Budget burning 10x normal.

For: alerts.

## Multi-Window Burn Rate

Better than threshold:
```yaml
# Fast burn
- alert: SLOBurnRateFast
  expr: |
    burn_rate_1h > 14
    AND
    burn_rate_5m > 14
  for: 2m
```

14x burn means budget gone in 2 days. Page now.

```yaml
# Slow burn
- alert: SLOBurnRateSlow
  expr: |
    burn_rate_6h > 6
    AND
    burn_rate_30m > 6
  for: 15m
```

6x burn: budget gone in 5 days.

## Burn Rate Table

Google SRE book:
| Long window | Short window | Burn rate | Time to exhaust |
|---|---|---|---|
| 1 hr | 5 min | 14.4x | 2 days |
| 6 hr | 30 min | 6x | 5 days |
| 24 hr | 2 hr | 3x | 10 days |
| 3 days | 6 hr | 1x | 30 days |

For: progressive severity.

## Alerts by Severity

```yaml
- alert: BurnRateFast (P0)
  expr: burn_rate_1h > 14 AND burn_rate_5m > 14
  for: 2m
  labels: { severity: critical }

- alert: BurnRateSlow (P1)
  expr: burn_rate_6h > 6 AND burn_rate_30m > 6
  for: 15m
  labels: { severity: warning }
```

## Per Endpoint SLO

Maybe:
- `/api/checkout`: 99.95%
- `/api/analytics`: 99%

Different criticality.

## Error Budget Policy

When budget exhausted:
- Stop releases
- Postmortems
- Reliability work prioritized

When budget healthy:
- Move fast
- Take risks

Self-policing.

## SLO Calculator

For:
- Target → time budget
- Time budget → target

Useful for planning.

## Multi-Indicator SLO

Composite:
```
99.9% availability AND p99 < 500ms
```

Tricky to compute. Often: separate SLOs.

## Window Choice

| Window | Pros | Cons |
|---|---|---|
| 28 days | smooth | slow change |
| 7 days | responsive | noisy |
| 1 day | very responsive | very noisy |

For: 28 days standard.

## Calendar vs Rolling

### Calendar (e.g. month)
- Resets monthly
- Predictable

### Rolling (e.g. 28 days)
- Smooth
- Less manipulable

Most: rolling.

## Resetting

Some orgs:
- Monthly: budget resets
- Quarterly review

For: business cycles.

## Examples

### 99.9% availability, 28 days
- Budget: 43 min outage
- Burn rate 14x: ~3 min sustained outage = ~1% budget

### 99.95% latency, 28 days
- Budget: 0.05% of requests slow
- For 1M requests/day: 500 can be slow daily

## Visualize

Burn rate over time:
```
burn rate
   ↑
14 ────────  (page threshold)
6  ────────  (warn threshold)
1  ────────  (normal)
   →
   time
```

Above 1: consuming faster than budget.

## SLO Doc

For each service:
- SLO target
- SLI definition
- Owner
- Burn rate alerts
- Policy

## Tools

- Sloth (generate SLO config)
- Pyrra (K8s SLOs)
- OpenSLO (spec)
- Nobl9 (commercial)
- DataDog SLOs

## Sloth Example

```yaml
version: prometheus/v1
service: my-app
slos:
  - name: requests-availability
    objective: 99.9
    description: API availability
    sli:
      events:
        error_query: |
          sum(rate(http_requests_total{code=~"5.."}[{{.window}}]))
        total_query: |
          sum(rate(http_requests_total[{{.window}}]))
    alerting:
      page_alert:
        labels: { severity: critical }
      ticket_alert:
        labels: { severity: warning }
```

Generates burn rate rules + alerts.

## Best Practices

- Single SLI per SLO
- Sloth or similar (multi-window auto)
- Document each
- Quarterly review
- Error budget policy enforced
- Track per-service compliance

## Common Mistakes

- 99.999% for everything (impossible / expensive)
- Single threshold alert (use multi-window)
- No policy (budget meaningless)
- Change SLO without process

## Quick Refs

```
Error budget = 1 - SLO
Burn rate = current_error / budget_rate

Multi-window:
- 1h/5m: 14x → page
- 6h/30m: 6x → warn

28 days rolling typical
```

## Interview Prep

**Mid**: "SLO math."

**Senior**: "Burn rate."

**Staff**: "Error budget policy."

## Next Topic

→ [T03 — Burn Rate Alerts](T03-Burn-Rate-Alerts.md)
