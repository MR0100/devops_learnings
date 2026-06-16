# L17/C05/T04 — Alert Hygiene

## Learning Objectives

- Reduce alert noise
- Practice good hygiene

## Why

Bad alerts:
- Wake people for nothing
- Erode trust
- Cause burnout
- Real alerts missed

Good alerts:
- Actionable
- Trusted
- Clear

## Principles

### Every Alert Actionable
"What do I do?" Must have clear answer.

### Every Alert Owned
"Who responds?" Single owner.

### Every Alert Reviewed
Postmortem after every page.

## Bad Alert Examples

```
"CPU > 80%"
"Memory > 90%"
"Disk > 85%"
```

No context. No action. Noise.

## Good Alert Examples

```
"Service API: error rate > 5% for 10m"
- Action: investigate API
- Runbook: link
- Owner: backend team
```

Clear.

## SLO-Based

Best: alert when SLO at risk.

```
"Error budget burn rate 14x sustained"
```

Tied to user impact.

(See L17/C08.)

## Severity Discipline

### Critical (Page)
User impact NOW.

### Warning (Ticket)
Will impact if not addressed.

### Info (Log)
Track; no action.

## Wrong Severity

- Page for "disk 85%" → noise
- Warning for "site down" → missed

Calibrate.

## Page Audit

```
Total pages last 30 days: 50
Pages with action: 20 (40%)
Pages auto-resolved: 25 (50%)
False positives: 5 (10%)
```

Goal: > 70% action rate.

## Reduce Noise

### Threshold Adjustment
```yaml
# Was
expr: error_rate > 1%

# Now (less sensitive)
expr: error_rate > 5%
for: 10m
```

### Add Time Window
```yaml
for: 15m
```

Sustained issues only.

### Multi-Window
```yaml
expr: |
  (rate(errors[5m]) > 0.1) AND
  (rate(errors[1h]) > 0.05)
```

Short + long term both confirm.

### Burn Rate
```yaml
expr: burn_rate_1h > 14 AND burn_rate_5m > 14
```

## Group Carefully

```yaml
group_by: [alertname, cluster, service]
```

Same group → one notification.

Don't:
- group_by: [pod]  # too granular
- group_by: []  # too broad

## Inhibit Cascades

```yaml
inhibit_rules:
  - source_matchers: [alertname = NodeDown]
    target_matchers: [severity = warning]
    equal: [node]
```

NodeDown → suppress warnings from same node.

## Silences for Maintenance

Don't fight alerts; silence:
```bash
amtool silence add cluster=stage -d 2h -c "Maintenance"
```

But: remember to remove.

## Postmortem Reviews

For each page:
- Was it actionable? (Yes/No)
- What did responder do?
- Could it have been resolved without paging?
- Should alert be modified?

For: continuous improvement.

## Alert Owner

Per alert:
```yaml
annotations:
  team: backend
  owner: alice@example.com
```

For: clear accountability.

## Runbook

```yaml
annotations:
  runbook_url: 'https://runbooks/api-error-rate'
```

Linked in page. Reduces investigation time.

## Alert Description

```yaml
annotations:
  description: |
    Service {{ $labels.service }} in cluster {{ $labels.cluster }}
    has error rate {{ $value | humanizePercentage }}.
    
    Likely causes:
    - Recent deploy
    - Database issue
    - Upstream service down
    
    Investigation: https://...
```

Specific. Educational.

## Anti-Patterns

### Alert per Resource
```
HighCPU-node1
HighCPU-node2
HighCPU-node3
...
```

Use aggregation:
```yaml
# Alert when 50% of nodes
sum(rate(node_cpu_total[5m]) > 0.8) / count > 0.5
```

### Threshold without `for`
```yaml
expr: error_rate > 0.01
# Fires on spike; flaps
```

Use:
```yaml
for: 5m
```

### No Action
"Investigate" without context.

### Self-Service
Anyone adds any alert; no review.

## On-Call Review Meetings

Weekly:
- Alert noise
- Top noisy alerts
- Action plans

For: continuous improvement.

## Metrics for Alerts

```promql
sum by (alertname) (count(ALERTS{alertstate="firing"}))
```

Top alerts by fire count.

```promql
rate(alertmanager_notifications_total[1d])
```

Notification volume.

## Reducing Pager Load

Steps:
1. Audit current alerts
2. Identify top noisy
3. Fix or tune each
4. Repeat

For: lower MTTA, less burnout.

## Quiet Hours

```yaml
- match: {severity: warning}
  active_time_intervals: [business-hours]
  receiver: slack-only

- match: {severity: warning}
  active_time_intervals: [off-hours]
  receiver: mute
```

Don't page warnings at night.

## Critical Off-Hours

```yaml
- match: {severity: critical}
  receiver: pagerduty
```

Always paged.

## Best Practices

- Actionable only
- Single owner
- Runbook always
- Sensible `for`
- SLO-based
- Multi-window burn rate
- Postmortems
- Audit + tune

## Common Mistakes

- Per-resource alerts (flood)
- No `for` (flapping)
- No runbook
- Page for warning
- No audit cycle

## SLO Alerts (Best)

```yaml
- alert: SLOBurnRateFast
  expr: |
    error_budget_burn_rate_5m > 14 AND error_budget_burn_rate_1h > 14
  for: 2m
  labels:
    severity: critical
```

Specifies user impact directly.

## Quick Refs

```
Hygiene checklist:
- Actionable?
- Owner clear?
- Runbook?
- Severity right?
- For window?
- Group correct?
- Inhibit cascades?
```

## Interview Prep

**Mid**: "Alert noise."

**Senior**: "Alert hygiene."

**Staff**: "Pager culture."

## Next Topic

→ Move to [L17/C06 — OpenTelemetry](../C06/README.md)
