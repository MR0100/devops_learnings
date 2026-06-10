# L15/C07/T03 — Automated Rollback Triggers

## Learning Objectives

- Define rollback conditions
- Implement automation

## Why Auto-Rollback

Humans:
- Slow to detect
- Slow to react
- Asleep at night

Auto:
- Detect in seconds
- React in seconds
- Always available

## Conditions

### Error Rate Spike
```promql
sum(rate(http_requests_total{code=~"5..", version="canary"}[1m]))
/
sum(rate(http_requests_total{version="canary"}[1m]))
> 0.05   # 5% errors
```

### Latency Increase
```promql
histogram_quantile(0.99, http_request_duration_seconds{version="canary"})
> baseline * 1.5
```

### Health Check
```promql
up{job="myapp", version="canary"} == 0
```

### Resource Saturation
```promql
container_memory_usage_bytes{pod=~"myapp-canary-.*"} / container_spec_memory_limit_bytes > 0.9
```

### Business Metric
```promql
sum(rate(orders_placed_total{version="canary"}[5m]))
<
sum(rate(orders_placed_total{version="stable"}[5m])) * 0.8
```

## Tools

### Argo Rollouts
AnalysisTemplate triggers rollback.

### Flagger
Configurable thresholds.

### Spinnaker
Canary analysis (Kayenta).

### Custom
Webhook on Prometheus alert.

## Argo Rollouts Example

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate
spec:
  metrics:
  - name: error-rate
    interval: 30s
    successCondition: result[0] <= 0.01
    failureLimit: 3
    provider:
      prometheus:
        address: http://prom:9090
        query: |
          ...
```

If failureLimit exceeded: rollback.

## Multiple Metrics

```yaml
metrics:
- name: error-rate
  ...
- name: latency
  ...
- name: cpu
  ...
```

Any fail: rollback.

For: defense in depth.

## Spike Detection

```promql
# Slow window
rate_long := rate(errors[1h])

# Fast window
rate_short := rate(errors[5m])

# Spike if short much higher than long
rate_short / rate_long > 3
```

For: detect new errors vs baseline.

## False Positives

Auto-rollback on every blip:
- Bad UX
- Stuck in rollback loop

Mitigations:
- Require N consecutive failures
- Minimum sample size
- Holdout period (wait for traffic)

## Blast Radius

Canary 5% errored:
- Rollback affects 5% users for X seconds

For: limited damage.

## Rollback Speed

```
Detection:  30 sec
Rollback:   30 sec
Recovery:   60 sec total
```

For: minimize MTTR.

## Beyond Rollback

### Pause + Investigate
For complex; auto-pause, human decides.

### Auto-Disable Feature Flag
Bug behind flag; auto-off.

### Auto-Scale Down Canary
Reduce % to 0.

For: graduated response.

## Webhooks

```yaml
provider:
  web:
    url: https://my-monitoring/api/canary-health
    jsonPath: "{$.healthy}"
```

Custom logic; can use ML.

## SLO-Based

```yaml
metrics:
- name: error-budget-burn
  successCondition: result[0] < 14  # burn rate
```

Burn through error budget too fast: rollback.

For: SLO-driven.

## Composite

```yaml
- name: composite
  successCondition: |
    errors[0] < 0.05 AND latency[0] < 500
```

Multiple in one.

## Alert vs Rollback

| | Alert | Rollback |
|---|---|---|
| Action | Notify human | Auto-revert |
| Speed | Fast | Fast |
| Reversibility | Easy | Easy if K8s |
| Confidence | Medium | High |

Alert: lower threshold; rollback: higher.

For: tiered response.

## Manual Override

```bash
# Pause auto
kubectl argo rollouts pause myapp

# Override
kubectl argo rollouts promote myapp --skip-current-step
```

For: incidents where auto wrong.

## Notifications on Rollback

```yaml
- on-rollout-aborted:
    serviceSlack:
      channel: alerts
      message: "Rollback triggered for {{.metadata.name}}"
```

For: visibility.

## Track Rollback Rate

```promql
sum(rate(argo_rollouts_aborts_total[1d]))
```

If high: too sensitive or many bad deploys.

## Recovery After Rollback

```
1. Auto-rollback triggers
2. Restore stable
3. Notify team
4. Investigate
5. Fix
6. Redeploy
```

For: deliberate.

## Time-of-Day Rules

```yaml
- only auto-promote weekdays 9-5 ETC
```

Riskier off-hours: more conservative.

For: ops sense.

## Real Examples

### Netflix
Spinnaker canary analysis; auto-rollback common.

### Etsy
Quick rollback culture.

### Google
Auto-rollback at scale.

## Best Practices

- Multi-metric (defense)
- failureLimit > 1 (anti-flake)
- Notify on rollback
- Track rollback rate
- Test rollback regularly
- Document conditions

## Common Mistakes

- Single metric (false alarms)
- Aggressive (rollback every blip)
- Too lenient (real issues persist)
- No notification (silent rollback)
- Stuck in loop (rollback → redeploy → rollback)

## Anti-Loop

```yaml
- if rollback count > 3 in 1 hour: stop auto, page
```

For: prevent infinite loop.

## Chaos Engineering

Test rollback:
- Force inject errors in canary
- Verify auto-rollback triggers
- Verify recovery

For: confidence.

## Quick Refs

```yaml
# Argo Rollouts
analysis:
  templates: [ {templateName: error-rate} ]
  args: [...]

# AnalysisTemplate
metrics:
- name: NAME
  successCondition: result[0] <= TARGET
  failureLimit: 3

# Flagger
analysis:
  metrics:
  - name: NAME
    thresholdRange: {max: TARGET}
```

## Interview Prep

**Mid**: "Auto-rollback."

**Senior**: "Rollback strategy."

**Staff**: "Progressive delivery."

## Next Topic

→ Move to [L15/C08 — Release Engineering](../C08/README.md)
