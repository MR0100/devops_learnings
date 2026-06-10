# L30/C05/T02 — Graceful Spot Interruption Handling

## Learning Objectives

- Handle spot evictions
- Graceful shutdown

## Spot Interruption

AWS:
- 2-min warning
- Via metadata
- Or via EventBridge

## Karpenter

Listens to interruption events:
```yaml
spec:
  settings:
    interruptionQueue: my-queue
```

Provisioned SQS receives events. Karpenter:
- Cordons node
- Schedules new node
- Drains old

## Pod Grace

```yaml
spec:
  terminationGracePeriodSeconds: 60
```

For: handle SIGTERM.

## App Handling

```python
import signal

def handle_sigterm(sig, frame):
    # Stop accepting new requests
    server.stop_accepting()
    # Drain
    server.wait_for_inflight()
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
```

For: clean shutdown.

## PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
```

For: maintain availability.

## Stateful

For stateful pods on spot:
- Risk
- Use persistent volumes
- Plan for restart

For: usually avoid.

## Monitor

```promql
karpenter_interruptions_total
```

Track eviction rate:
- < 1%: OK
- > 5%: investigate (instance type pool)

## Spot Diversification

(See T01.)

Diverse types → lower eviction.

## Best Practices

- Karpenter interruption handling
- Graceful shutdown
- PDB
- Diverse types
- Stateless on spot
- Monitor

## Common Mistakes

- No graceful shutdown
- Stateful on spot
- One instance type
- No PDB

## Quick Refs

```
Karpenter: interruption queue
App: SIGTERM handler
K8s: PDB + terminationGracePeriodSeconds
```

## Next Topic

→ [T03 — Cost Dashboards](T03-Cost-Dashboards.md)
