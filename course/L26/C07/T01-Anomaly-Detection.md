# L26/C07/T01 — Anomaly Detection

## Learning Objectives

- Detect cost spikes
- Auto-alert

## Why

Cloud bills:
- Surprise spikes
- Forgotten resources
- Misconfigured

For: catch early; act.

## Methods

### Threshold
Spend > $X/day → alert.

Simple but rigid.

### Trend
Spend > average + 2σ.

### ML
Anomaly detection (AWS Cost Anomaly Detection, etc.).

## AWS Cost Anomaly Detection

```bash
aws ce create-anomaly-monitor --anomaly-monitor ...
```

ML-based:
- Detect spikes
- SNS notification

Free.

## Cost Categories

```bash
aws ce create-cost-category-definition ...
```

For: grouping resources for monitoring.

## Vantage

Anomaly detection built-in.

## CloudHealth

Similar.

## Datadog Cloud Cost

Integrated.

## Custom

```sql
SELECT day, SUM(cost) AS daily
FROM cur
GROUP BY day
```

Compare:
- Today vs avg(last 30 days)
- > 1.5x: anomaly

## Alerts

Slack / PagerDuty / email.

## Examples

- New service launched (expected)
- Forgotten dev cluster (waste)
- Compromised account (security)
- Bug (infinite loop launching instances)

## Response

For each:
- Identify
- Investigate
- Fix or accept

## Best Practices

- Daily granularity
- Per-team
- Per-service
- Auto-investigate suggestions
- Runbook for high-cost anomalies

## Common Mistakes

- No anomaly detection
- Too noisy (alert fatigue)
- No owner (anomalies ignored)

## Quick Refs

```bash
aws ce create-anomaly-monitor
aws ce create-anomaly-subscription

# Vantage / CloudHealth: in UI
```

## Interview Prep

**Mid**: "Cost anomaly."

**Senior**: "Detection."

**Staff**: "FinOps automation."

## Next Topic

→ [T02 — Forecasting & Budgets](T02-Forecasting-Budgets.md)
