# L25/C03/T02 — CPU / Memory Exhaustion

## Learning Objectives

- Inject resource chaos
- Verify limits

## CPU

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: cpu-stress
spec:
  mode: one
  selector:
    namespaces: [prod]
  stressors:
    cpu:
      workers: 2
      load: 90   # 90% load
  duration: '5m'
```

For: tests HPA, alerts.

## Memory

```yaml
spec:
  stressors:
    memory:
      workers: 2
      size: '500MB'
```

For: OOM detection, limits.

## Linux stress-ng

Manual:
```bash
stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 60s
```

## What to Test

### HPA
Does it scale up?

### Alerts
CPU > 80% → alert?

### Throttling
K8s limits enforced?

### OOM
Pod restarted?

### Cascading
Other pods OK or affected?

## Resource Limits

Without:
- Memory: OOMKilled
- CPU: throttled

With limits set: graceful.

## QoS

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

Guaranteed / Burstable / BestEffort.

## Node Resource

Use up node resources:
- Tests pod eviction
- Node Pressure

## Tests

- Eviction policy
- Pod priority
- Reschedule

## Best Practices

- Limit blast (one pod)
- Watch alerts
- Verify auto-handle
- Document findings

## Common Mistakes

- No resource limits set
- Cluster-wide chaos (cascading)
- Skip observation

## Quick Refs

```yaml
StressChaos:
  stressors:
    cpu: { workers, load }
    memory: { workers, size }
```

## Interview Prep

**Mid**: "Resource chaos."

**Senior**: "Verify limits."

## Next Topic

→ [T03 — Disk I/O Saturation](T03-Disk-IO.md)
