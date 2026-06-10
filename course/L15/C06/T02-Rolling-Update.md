# L15/C06/T02 — Rolling Update

## Learning Objectives

- Configure rolling update
- Tune parameters

## Rolling Update

Replace pods incrementally:
```
Old: ███
        ↓ start one new
Old: ██ New: █
        ↓ stop one old
Old: █  New: ██
        ↓ continue
Old:    New: ███
```

Zero downtime (mostly).

## K8s Default

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
```

## Parameters

### maxSurge
Extra pods allowed during update.
- 0: never exceed replicas
- 25%: temporarily 125%
- 1: one extra pod

### maxUnavailable
Pods that can be down.
- 0: never below replicas (need surge)
- 25%: 75% always up
- 1: one allowed down

## Strategies

### Surge Only (Safest)
```yaml
maxSurge: 25%
maxUnavailable: 0
```

Add new before removing old. Slower but no capacity reduction.

### Replace Quick
```yaml
maxSurge: 0
maxUnavailable: 25%
```

Replace existing. Capacity dips.

### Default
```yaml
maxSurge: 25%
maxUnavailable: 25%
```

Balance.

## Trigger

```yaml
- run: kubectl set image deploy/myapp myapp=NEWIMAGE
# Or:
- run: kubectl apply -f deploy.yaml
# (with new image)
```

K8s controller handles rolling.

## Watch

```bash
kubectl rollout status deploy/myapp
kubectl get pods -w
```

## Pause / Resume

```bash
kubectl rollout pause deploy/myapp
# Update settings, no rollout
kubectl rollout resume deploy/myapp
```

For: change without immediate rollout.

## Rollback

```bash
kubectl rollout undo deploy/myapp
kubectl rollout undo deploy/myapp --to-revision=3
kubectl rollout history deploy/myapp
```

For: revert.

## Health Checks Critical

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

Without readinessProbe: K8s thinks pod ready immediately. Traffic goes to not-ready pod.

For: readiness gates rollout.

## startupProbe

For slow-starting apps:
```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
# Tolerates 5 min startup
```

Separate from readiness.

## livenessProbe

Restart unhealthy:
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  periodSeconds: 30
```

Caution: too aggressive → restart loop.

## PreStop Hook

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 30; nginx -s quit"]
```

Drain connections before termination.

## Termination Grace Period

```yaml
spec:
  terminationGracePeriodSeconds: 60
```

K8s sends SIGTERM; waits N seconds; then SIGKILL.

App should handle SIGTERM:
- Stop accepting new
- Drain existing
- Exit

## Connection Draining

LB / ingress:
- Remove pod from rotation
- Wait existing connections
- Pod gracefully exits

Without: in-flight requests dropped.

## Velocity

Total time:
```
TotalTime = (replicas / batchSize) × (pull + startup + ready)
```

For 10 replicas, batch 2, 30s each step: ~150 sec.

Tune batch + startup.

## Image Pull Speed

Affects rolling:
- Pre-pulled or cached: fast
- Cold pull: slow

For: pre-warm images.

## Failure Handling

If new version fails health:
- K8s pauses
- Doesn't kill old
- Operator investigates

```bash
kubectl describe pod NEW_POD
kubectl logs NEW_POD
```

## Progress Deadline

```yaml
spec:
  progressDeadlineSeconds: 600
```

If not progressed in N seconds: rollout failed.

```bash
kubectl rollout status deploy/myapp
# Returns non-zero on failure
```

## Surge vs Capacity

```
replicas: 10
maxSurge: 25%
# Max pods during: 12

maxUnavailable: 25%
# Min ready during: 7
```

For: tune to traffic + resources.

## Rolling for HA

Multi-AZ:
- Surge into each AZ
- Lose one AZ during: still capacity

For: maxUnavailable accounts for AZ failure.

## Deployment vs StatefulSet

### Deployment
Rolling update default.

### StatefulSet
Sequential by default:
- Update pod-N
- Wait ready
- Update pod-(N-1)
- ...

For: ordered state.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
```

Partition: only update pods >= partition. For phased rollout.

## DaemonSet

Per-node:
```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
```

Update one node at a time.

## Best Practices

- readinessProbe always
- terminationGracePeriodSeconds tuned
- PreStop hook for connection drain
- progressDeadlineSeconds set
- Test rollback
- Monitor during rollout

## Common Mistakes

- No readiness probe (404s during rollout)
- Aggressive liveness probe (restart loop)
- Long-running connections (drained ungracefully)
- maxUnavailable too high (capacity dip)
- No rollback test

## Beyond Rolling

For zero risk: canary or blue/green.

Rolling: best default; sufficient for most.

## Quick Refs

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0

readinessProbe: ...
lifecycle:
  preStop: ...
terminationGracePeriodSeconds: 60
```

```bash
kubectl rollout status deploy/X
kubectl rollout pause/resume deploy/X
kubectl rollout undo deploy/X
kubectl rollout history deploy/X
```

## Interview Prep

**Junior**: "What's rolling update."

**Mid**: "maxSurge vs maxUnavailable."

**Senior**: "Zero-downtime techniques."

**Staff**: "Rollout strategies."

## Next Topic

→ [T03 — Blue/Green](T03-Blue-Green.md)
