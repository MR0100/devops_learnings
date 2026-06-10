# L25/C03/T01 — Network Latency & Loss

## Learning Objectives

- Inject network faults
- Find resilience gaps

## Why

Network is unreliable in real:
- Cross-region latency
- Cross-AZ blips
- Brief partitions

Test app handles.

## Latency

Add fixed delay:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
spec:
  action: delay
  mode: all
  selector:
    namespaces: [prod]
  delay:
    latency: '100ms'
    correlation: '50'
    jitter: '20ms'
  duration: '5m'
```

## Tests

- Timeouts: do they fire?
- Retries: do they happen?
- Circuit breakers: do they trip?
- Cache: serves stale?

## Loss

```yaml
spec:
  action: loss
  loss:
    loss: '10'   # 10% packet loss
```

## Tests

- TCP retransmits
- Throughput drop
- Connection failures

## Duplication

```yaml
spec:
  action: duplicate
  duplicate:
    duplicate: '20'   # duplicate 20% of packets
```

For: idempotency check.

## Corruption

```yaml
spec:
  action: corrupt
  corrupt:
    corrupt: '5'
```

## Partition

```yaml
spec:
  action: partition
  direction: from
  target:
    namespaces: [other-ns]
```

Block traffic between selectors.

## Use Cases

### Slow Downstream
Service B slow → service A:
- Timeout?
- Retry storm?
- Cascading failure?

### Region Latency
Cross-region 200ms → app:
- Multi-region client handles?

### Cell Network
Mobile users with high latency.

## Linux tc

Manual:
```bash
tc qdisc add dev eth0 root netem delay 100ms 20ms
```

For: outside K8s.

## Verify

During chaos:
- Latency metrics (yours, downstream)
- Errors
- Throughput
- Customer impact

## Stop

```bash
kubectl delete networkchaos test
```

## Best Practices

- Start small (1 pod)
- Reasonable duration
- Monitor closely
- Verify auto-recovery

## Common Mistakes

- Too aggressive (real outage)
- No monitoring (don't see impact)
- Forget to stop

## Quick Refs

```yaml
NetworkChaos:
  action: delay / loss / partition / corrupt
  mode: one / all / fixed-percent
  selector: ...
```

## Interview Prep

**Mid**: "Network chaos."

**Senior**: "Find timeouts."

## Next Topic

→ [T02 — CPU / Memory Exhaustion](T02-Resource-Chaos.md)
