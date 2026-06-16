# L15/C06/T04 — Canary Deployment

## Learning Objectives

- Run canary
- Use auto-promotion

## Canary

Small % of traffic to new version. Monitor. Increase if healthy.
```
T+0:   1% to new
T+5m: 5% to new
T+15m: 25% to new
T+30m: 50% to new
T+60m: 100% to new
```

## Pros

- Limited blast radius
- Real production traffic
- Auto-rollback possible

## Cons

- Slow rollout
- Tooling complex
- Stateful tricky

## Argo Rollouts Canary

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  strategy:
    canary:
      steps:
      - setWeight: 1
      - pause: { duration: 5m }
      - setWeight: 5
      - pause: { duration: 5m }
      - setWeight: 25
      - pause: { duration: 10m }
      - setWeight: 50
      - pause: { duration: 10m }
      - setWeight: 100
  template: ...
```

Pause: hold before next step. Manual or auto.

## Service Mesh Canary

Istio:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  http:
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 95
    - destination:
        host: myapp
        subset: v2
      weight: 5
```

5% to v2.

## Flagger

CNCF; automates canary:
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: success-rate
      thresholdRange:
        min: 99
      interval: 1m
```

Flagger:
- Increases weight
- Checks metrics
- Rollback if SLO violated

## Metric Analysis

Argo Rollouts AnalysisTemplate:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
  - name: success-rate
    interval: 30s
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prom:9090
        query: |
          sum(rate(http_requests_total{code!~"5.."}[1m])) / sum(rate(http_requests_total[1m]))
```

Auto: continue or rollback.

## Header-Based Canary

```yaml
http:
- match:
  - headers:
      x-canary:
        exact: "true"
  route:
  - destination:
      host: myapp
      subset: v2
- route:
  - destination:
      host: myapp
      subset: v1
```

For: opt-in beta testers.

## User-Based Canary

Hash user ID for sticky routing:
```yaml
http:
- route:
  - destination: ...
  retries:
    ...
  hashPolicy:
  - header: x-user-id
```

Same user always same version.

## Cookie / Geo

```yaml
match:
  headers:
    cookie:
      regex: ".*canary=true.*"
```

Or geographic via header.

## Rollout Modes

### Manual
Engineer promotes each step.

### Auto
Metrics drive.

### Hybrid
Auto until critical %; manual after.

## Service Mesh + Argo

Argo Rollouts uses Istio:
```yaml
strategy:
  canary:
    canaryService: myapp-canary
    stableService: myapp-stable
    trafficRouting:
      istio:
        virtualService:
          name: myapp
        destinationRule:
          name: myapp
          canarySubsetName: canary
          stableSubsetName: stable
    steps:
    - setWeight: 5
    - pause: {duration: 5m}
    ...
```

Argo manipulates VirtualService weights.

## Rollback

```bash
kubectl argo rollouts abort myapp
```

Or auto on analysis failure.

## Pre-Promotion

```yaml
analysis:
  templates:
  - templateName: success-rate
  startingStep: 2
```

Skip first step; analyze after weight 5%.

## Shadow / Mirror

Canary + mirror:
- 5% real traffic to v2
- 100% mirrored to v2-shadow

Both monitored. Mirror = no user impact.

## Capacity

Need:
- Stable: 100% capacity
- Canary: 5% capacity (extra)

For: surge during canary.

## Long-Running

Some canaries: hours-days (slow user rollout).

For: low-risk features.

## A/B vs Canary

| | Canary | A/B |
|---|---|---|
| Goal | safe rollout | feature variant test |
| Duration | hours | weeks |
| Audience | random % | targeted segment |
| Tooling | flagger / argo | LaunchDarkly etc. |

## When Canary

- Critical service
- New version risky
- Strong observability
- Real-traffic testing valuable

## When Not

- Tiny service (overkill)
- Stateful boundaries
- No metrics
- Resource-constrained

## Best Practices

- Use Flagger or Argo Rollouts
- Metric-based auto-promotion
- Auto-rollback on SLO violation
- Reasonable step sizes
- Pre-promotion analysis
- Monitor + alert

## Common Mistakes

- No metric gating (just timer)
- Rollout too fast (no time to detect)
- No auto-rollback
- Stateful issues (DB writes from v1 + v2)
- Long canaries blocking deploys

## Operator Patterns

### Slow Canary
Hours; for big risk.

### Fast Canary
Minutes; for trusted changes.

### Per-Region
Canary in us-east-1 only; full rollout other regions later.

## Metric Examples

```promql
# Success rate
sum(rate(http_requests_total{code!~"5.."}[1m])) / sum(rate(http_requests_total[1m]))

# Latency p99
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))

# Custom business
sum(rate(orders_placed_total[5m])) by (version)
```

## Real Examples

### Netflix
Spinnaker canary; standard.

### Google
Canary releases; Borg internal.

### Many cloud-native
Argo Rollouts / Flagger.

## Quick Refs

```yaml
# Argo Rollouts
strategy:
  canary:
    steps:
    - setWeight: N
    - pause: { duration: T }

# Flagger
analysis:
  metrics:
  - name: success-rate
    thresholdRange: { min: 99 }
```

```bash
kubectl argo rollouts get rollout NAME --watch
kubectl argo rollouts promote NAME
kubectl argo rollouts abort NAME
```

## Interview Prep

**Mid**: "What's canary."

**Senior**: "Auto-promotion."

**Staff**: "Canary strategy."

## Next Topic

→ [T05 — Shadow Deployments](T05-Shadow-Deployments.md)
