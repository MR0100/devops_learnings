# L17/C03/T04 — Alerting Rules

## Learning Objectives

- Write alerts
- Avoid common mistakes

## Alert Rule

```yaml
groups:
  - name: alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{code=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "Error rate is {{ $value | humanizePercentage }}"
          runbook: "https://example.com/runbooks/high-error-rate"
```

## Fields

### alert
Name.

### expr
PromQL; fires when returns series.

### for
Duration condition must hold. Avoids flapping.

### labels
Added to alert.

### annotations
Human-readable; for routing + notification.

## Lifecycle

```
inactive → expr matches → pending (for duration) → firing → expr no longer matches → resolved
```

## Group Eval Interval

Same as recording rules:
```yaml
groups:
  - name: NAME
    interval: 30s
    rules: ...
```

## Common Alerts

### Error Rate
```yaml
- alert: ErrorRate
  expr: |
    sum by (service) (rate(http_requests_total{code=~"5.."}[5m]))
    /
    sum by (service) (rate(http_requests_total[5m]))
    > 0.05
  for: 10m
  labels:
    severity: warning
```

### Latency
```yaml
- alert: HighLatency
  expr: |
    histogram_quantile(0.99,
      sum by (le, service) (rate(http_duration_bucket[5m]))
    ) > 1
  for: 10m
```

### Pod Restart
```yaml
- alert: PodRestarting
  expr: |
    rate(kube_pod_container_status_restarts_total[15m]) > 0
  for: 15m
```

### Disk Full
```yaml
- alert: DiskFull
  expr: |
    predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0
  for: 30m
```

### CPU Saturation
```yaml
- alert: CPUHigh
  expr: |
    100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 15m
```

## Severity

```yaml
labels:
  severity: critical    # page
  severity: warning     # ticket
  severity: info        # log
```

For: routing decisions.

## Severity Levels

- `critical`: page (immediate)
- `warning`: ticket (next day)
- `info`: log (track)

## Burn Rate Alerts (SLO)

```yaml
- alert: SLOBurnRateFast
  expr: |
    error_budget_burn_rate_1h > 14 AND
    error_budget_burn_rate_5m > 14
  for: 2m
  labels:
    severity: critical
```

Multi-window burn rate for SLO violations. (See L17/C08.)

## For Duration

Avoid flapping:
```yaml
for: 5m
```

Must hold for 5 min before firing.

Too short: noisy.
Too long: slow detection.

For RED metrics: 5-10m typical.
For paging: shorter for criticals.

## Labels

```yaml
labels:
  severity: critical
  team: backend
  service: api
```

Used by Alertmanager for routing.

## Templating

```yaml
annotations:
  summary: "{{ $labels.service }} error rate {{ $value | humanizePercentage }}"
  description: |
    Service {{ $labels.service }} in cluster {{ $labels.cluster }} 
    has error rate {{ $value | humanizePercentage }} > 5%.
```

`$labels`: alert labels.
`$value`: evaluated expression value.

## Runbooks

```yaml
annotations:
  runbook_url: "https://runbooks.example.com/{{ $labels.alertname }}"
```

For: link in alert notification.

## Multi-Window Multi-Burn-Rate

Better than single threshold:
```yaml
- alert: SLOBurnRate
  expr: |
    (sli:burn_rate:1h > (14 * (1 - 0.999)))
    and
    (sli:burn_rate:5m > (14 * (1 - 0.999)))
```

Fast burn AND consistent.

For: SLO alerts (less noisy).

## Validate

```bash
promtool check rules alerts.yml
```

Tests:
```bash
promtool test rules tests.yml
```

```yaml
# tests.yml
rule_files:
  - alerts.yml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{code="500"}'
        values: '0 0 0 100 200 300 400'
      - series: 'http_requests_total{code="200"}'
        values: '0 0 0 0 0 0 0'
    alert_rule_test:
      - eval_time: 6m
        alertname: HighErrorRate
        exp_alerts:
          - exp_labels:
              severity: critical
            exp_annotations:
              summary: ...
```

## Limits

```yaml
groups:
  - name: limits
    limit: 100
    rules: ...
```

Max alerts per evaluation. For: prevent floods.

## Good Alerts

- Actionable (clear what to do)
- Unique (not redundant)
- Owner clear
- Runbook linked
- Severity appropriate

## Bad Alerts

- "CPU > 80%" without context
- Multiple alerts for same condition
- No runbook
- Wrong severity (page for warning)
- Flapping

## Alert Hygiene

Track:
- Alert frequency
- MTTA (mean time to ack)
- Action rate (% leading to action)

Tune: false positives → adjust threshold or `for`.

(See L17/C05.)

## Best Practices

- Multi-window burn rate (SLO)
- Reasonable for duration
- Severity routing
- Runbooks always
- Test rules
- Track noise

## Common Mistakes

- Threshold without `for`
- Page for non-actionable
- No runbook
- High cardinality alerts (one per pod)
- No testing

## Quick Refs

```yaml
- alert: NAME
  expr: PROMQL
  for: DURATION
  labels:
    severity: critical|warning|info
  annotations:
    summary: ...
    description: ...
    runbook_url: ...
```

```bash
promtool check rules FILE.yml
promtool test rules FILE.yml
```

## Interview Prep

**Mid**: "Alert basics."

**Senior**: "Multi-window burn rate."

**Staff**: "Alert strategy."

## Next Topic

→ Move to [L17/C04 — Grafana](../C04/README.md)
