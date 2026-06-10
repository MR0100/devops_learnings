# L25/C03/T03 — Disk I/O Saturation

## Learning Objectives

- Inject disk chaos
- Find bottlenecks

## IOChaos

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: IOChaos
metadata:
  name: disk-delay
spec:
  action: latency
  mode: one
  selector: ...
  volumePath: /data
  path: '/data/**/*'
  delay: '100ms'
  duration: '5m'
```

For: tests file I/O resilience.

## Action Types

- latency: add I/O latency
- fault: return errors
- mistake: corrupt data

## Tests

- DB performance
- Cache miss handling
- Log write impact

## fio

Manual benchmark + load:
```bash
fio --filename=test --size=1G --iodepth=64 --rw=randwrite --bs=4k --numjobs=4 --time_based --runtime=60
```

## Disk Full

```bash
fallocate -l 10G /tmp/big
```

Tests:
- Detection
- Alerts
- App graceful

## NoSpace Error

```yaml
spec:
  action: fault
  errno: 28   # ENOSPC
```

## Best Practices

- Test in dev
- Watch app behavior
- Verify retries
- Storage class plays role

## Quick Refs

```yaml
IOChaos:
  action: latency / fault / mistake
  volumePath / path
  delay / errno
```

## Interview Prep

**Senior**: "Disk chaos."

## Next Topic

→ [T04 — Pod / Node Kills](T04-Pod-Node-Kills.md)
