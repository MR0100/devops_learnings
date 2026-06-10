# L15/C06/T03 — Blue/Green Deployment

## Learning Objectives

- Run blue/green
- Pros/cons

## Blue/Green

Two full environments:
- Blue: current live
- Green: new version

Switch traffic atomically:
```
Users → LB → Blue (live)
Users → LB → Green (new)   ← cutover instant
```

## Steps

1. Deploy new version to green
2. Test green
3. Cutover (LB switch)
4. Monitor
5. Keep blue as rollback for window
6. Eventually retire blue

## Pros

- Atomic cutover
- Easy rollback (switch back)
- Test green in isolation
- Zero downtime

## Cons

- 2× resources
- DB compatibility tricky
- Long-lived connections
- Cutover all at once (no canary)

## K8s

```yaml
# Service points to color label
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    color: blue   # switch to green
  ports:
  - port: 80
```

```yaml
# Blue Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
spec:
  selector:
    matchLabels:
      app: myapp
      color: blue
  template:
    metadata:
      labels:
        app: myapp
        color: blue
```

Similarly for green.

Switch:
```bash
kubectl patch service myapp -p '{"spec":{"selector":{"color":"green"}}}'
```

## Argo Rollouts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  strategy:
    blueGreen:
      activeService: myapp-active
      previewService: myapp-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
  template: ...
```

`previewService`: test before promote.
`autoPromotionEnabled`: manual or auto.

## Pre-Cutover Testing

Green has separate service / hostname:
```
blue.myapp.svc.cluster.local
green.myapp.svc.cluster.local
```

Smoke test green; then cutover.

## Database

### Schema Compatible
Both versions work with same schema.

For: typical case.

### Schema Changes
Migrate first; ensure backward compatible:
1. Expand: add new column (both versions OK)
2. Migrate: backfill
3. Both versions use new
4. Contract: remove old column

Multiple deploys.

For: zero-downtime schema.

## Connection Draining

Cutover instant; connections to blue:
- New: go to green
- Existing: stay on blue
- Eventually close

Wait before retiring blue (long-running connections).

## Storage

Persistent volumes shared:
- Blue + green read/write same data
- Must be compatible

Or:
- Each color own data (test data)
- Only after cutover: shared

## Promotion

```bash
# Manual promote
kubectl argo rollouts promote myapp
```

Or auto with analysis.

## Analysis (Argo Rollouts)

```yaml
strategy:
  blueGreen:
    autoPromotionEnabled: true
    prePromotionAnalysis:
      templates:
      - templateName: success-rate
      args:
      - name: service-name
        value: myapp-preview
```

Run tests against green; promote if pass.

## When Blue/Green

- Atomic switch needed
- Easy rollback critical
- 2× resources OK
- DB compatible

## When Not

- Resource constrained (no 2× capacity)
- Stateful with strict consistency
- Massive long-lived connections

## Cost

2× compute during deploy. For: brief.

After cutover: scale down old.

## Cutover Risks

- Both versions briefly serving (race)
- Connection drain
- Mid-deploy abort

Test thoroughly in staging.

## Variations

### Blue/Green at LB
ALB / ELB target groups.

### Blue/Green at DNS
DNS swap (slow due to TTL).

### Blue/Green at K8s Service
Label switch (instant).

For K8s: service approach.

## Long-Tail Cleanup

```
1. Cutover (T+0)
2. Drain blue (T+5min)
3. Scale blue down (T+10min)
4. Delete blue (T+1hr or later)
```

For: rollback window.

## Rollback

```bash
kubectl patch service myapp -p '{"spec":{"selector":{"color":"blue"}}}'
```

Instant.

## Real Examples

### Netflix
Spinnaker; blue/green common.

### Many SaaS
Critical paths.

## Combine with Canary

```
Deploy green
Canary 1% to green
Increase 10% / 50% / 100%
Cutover (full) via LB
```

For: best of both.

## Best Practices

- Pre-promotion analysis
- Connection drain delay
- DB compatibility
- Test in staging
- Rollback rehearsed
- Document each cutover

## Common Mistakes

- DB schema incompatible
- No connection drain
- Forget to scale down old (cost)
- No rollback test

## Quick Refs

```bash
# K8s Service patch
kubectl patch service NAME -p '{"spec":{"selector":{"color":"green"}}}'

# Argo Rollouts
kubectl argo rollouts get rollout NAME
kubectl argo rollouts promote NAME
kubectl argo rollouts abort NAME
```

## Interview Prep

**Mid**: "Blue/green explained."

**Senior**: "DB compatibility."

**Staff**: "Deployment strategy."

## Next Topic

→ [T04 — Canary](T04-Canary.md)
