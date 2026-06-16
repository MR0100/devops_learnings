# L17/C08/T03 — Burn Rate Alerts

## Learning Objectives

- Write burn rate alerts
- Avoid common pitfalls

## Why Burn Rate

Threshold-based alerts:
- "Error rate > 1%" → noisy, flapping
- Doesn't tie to user impact

Burn rate:
- Tied to SLO
- Measures budget consumption
- Multi-window reduces flake

## Formula

```
burn_rate = (current_error_rate) / (1 - SLO_target)
```

If SLO = 99.9% (error budget = 0.001):
- Current 0.01% errors → burn_rate = 0.1 (under budget)
- Current 1% errors → burn_rate = 10 (10x budget)

## Multi-Window Alert

```yaml
- alert: SLOBurnRateFast
  expr: |
    (
      slo:error_budget:burn_rate_1h > 14
      AND
      slo:error_budget:burn_rate_5m > 14
    )
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Service consuming budget 14x normal"
```

Long + short window. Both must agree.

## Standard Burn Rate Pairs

| Long | Short | Rate | Budget Time |
|---|---|---|---|
| 1h | 5m | 14.4x | 2 days |
| 6h | 30m | 6x | 5 days |
| 24h | 2h | 3x | 10 days |
| 3d | 6h | 1x | 30 days |

## Severity Tiers

```yaml
- alert: FastBurn       # 1h/5m 14x
  labels: severity=critical

- alert: SlowBurn       # 6h/30m 6x
  labels: severity=warning

- alert: VerySlowBurn   # 24h/2h 3x
  labels: severity=info
```

## Recording Rules

```yaml
groups:
  - name: slo
    interval: 30s
    rules:
      - record: slo:error_budget:burn_rate_5m
        expr: |
          (
            sum(rate(http_requests_total{code=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          )
          /
          (1 - 0.999)   # SLO target

      - record: slo:error_budget:burn_rate_1h
        expr: |
          (
            sum(rate(http_requests_total{code=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          )
          /
          (1 - 0.999)
```

## Templated SLO

```yaml
- record: slo:availability:burn_rate_5m
  expr: |
    label_replace(
      (sum by (service) (rate(http_requests_total{code=~"5.."}[5m]))
        /
       sum by (service) (rate(http_requests_total[5m]))
      ) / 0.001,
      "slo", "0.999", "", ""
    )
```

Per service.

## Latency Burn Rate

```yaml
- record: slo:latency:burn_rate_5m
  expr: |
    1 - (
      sum(rate(http_request_duration_bucket{le="0.5"}[5m]))
      /
      sum(rate(http_request_duration_count[5m]))
    )
```

Then burn rate from that.

## Pyrra

```yaml
apiVersion: pyrra.dev/v1alpha1
kind: ServiceLevelObjective
metadata:
  name: my-app
spec:
  target: "99.9"
  window: 28d
  indicator:
    ratio:
      errors:
        metric: http_requests_total{code=~"5.."}
      total:
        metric: http_requests_total
```

Auto-generates rules + alerts.

## Sloth

```bash
sloth generate -i sloth.yaml > prometheus-rules.yaml
```

Same idea; CLI.

## Alert Wording

```
summary: "SLO burn for {{ $labels.service }}: 14x rate"
description: |
  Error budget consumed at 14x normal rate.
  Budget will be exhausted in 2 days at current rate.
  
  Current error rate: {{ $value | humanizePercentage }}
  SLO: 99.9%
  
  Runbook: {{ .Annotations.runbook_url }}
```

For: actionable.

## False Positives

Burn rate handles:
- Transient spikes (1m fine; 5m + 1h required)
- Aggregation noise

For: lower than threshold alerts.

## Tuning

If too many fires:
- Adjust SLO (was too tight?)
- Adjust burn rate threshold
- Add filters

If too few fires:
- SLO might be too lenient
- Or service truly stable

## Per-Service

```promql
sum by (service) (rate(errors[5m])) / sum by (service) (rate(total[5m]))
```

Per service burn rates.

Each in own alert.

## Multiple SLOs

Per service:
- availability: 99.9%
- latency: 99% under 500ms

Each: own burn rate alert.

## Alert Output

```
[FIRING] SLO Burn Rate (api)
Service api consuming error budget at 14x rate.
Will exhaust in 2 days.
```

Clear; actionable.

## Tying to Action

```
Critical burn → page → on-call investigates
```

Runbook:
1. Check recent deploy
2. Check upstream services
3. Rollback if needed

## Lower Burn Rate

For non-critical:
```yaml
- alert: SlowBurn (P2)
  expr: burn_rate_24h > 3
  for: 1h
  severity: warning
```

Track during business hours.

## Best Practices

- Multi-window
- Sloth / Pyrra
- Recording rules
- Per service
- Runbook in annotation
- Severity by speed
- Track alert rate (tune)

## Common Mistakes

- Single window (flake)
- Burn rate without SLO basis
- Page for slow burn (not urgent)
- Wrong filter (excludes errors)
- Too many SLOs (alert sprawl)

## OpenSLO

Open spec:
```yaml
apiVersion: openslo/v1
kind: SLO
metadata:
  name: my-app
spec:
  service: my-app
  objectives:
    - target: 0.999
      sli:
        ratioMetric:
          counter: true
          good:
            metricSource:
              type: prometheus
              spec: { query: ... }
          total:
            metricSource: ...
```

For: portability.

## Real Usage

Companies adopting SLO/burn rate:
- Google (origin)
- Spotify
- Datadog (commercial)
- Many fintech

## Quick Refs

```yaml
# Burn rate alert
- alert: SLOBurnRate
  expr: |
    burn_rate_LONG > THRESH
    AND
    burn_rate_SHORT > THRESH
  for: SHORT
  labels: { severity: ... }

# Recording rule
- record: slo:error_budget:burn_rate_5m
  expr: error_rate_5m / (1 - SLO)
```

```bash
# Tools
sloth generate
pyrra
```

## Interview Prep

**Mid**: "Burn rate alert."

**Senior**: "Multi-window burn."

**Staff**: "SLO alert design."

## Next Topic

→ [T04 — Error Budget Policies](T04-Error-Budget-Policies.md)
