# L13/C09/T04 — Graceful Shutdown & PreStop Hooks

## Learning Objectives

- Configure graceful shutdown
- Use preStop properly

## Why Graceful Shutdown

When pod terminates:
- In-flight requests interrupted
- Connections dropped
- Data lost (writes mid-process)

Graceful = drain + finish + close.

## Termination Sequence

```
1. Pod marked for deletion (DeletionTimestamp)
2. Endpoint removal: kube-proxy / LB stops routing to pod
3. PreStop hook executes
4. SIGTERM sent to all containers
5. terminationGracePeriodSeconds countdown
6. SIGKILL if still running
7. Pod removed
```

Key: app must catch SIGTERM and finish cleanly.

## terminationGracePeriodSeconds

```yaml
spec:
  terminationGracePeriodSeconds: 60
```

Default: 30 seconds.

Time between SIGTERM and SIGKILL.

For:
- Long-running requests: increase
- Quick to drain: smaller

## SIGTERM Handler

App must handle:
```python
import signal
import sys

def handle_sigterm(signum, frame):
    # Stop accepting new
    server.stop_accepting()
    # Wait for in-flight
    server.wait_for_inflight(timeout=25)
    # Close
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
```

Without: SIGTERM ignored; SIGKILL after grace; abrupt.

## Go Example

```go
sigs := make(chan os.Signal, 1)
signal.Notify(sigs, syscall.SIGTERM)

go func() {
    <-sigs
    ctx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
    defer cancel()
    server.Shutdown(ctx)
    os.Exit(0)
}()
```

http.Server.Shutdown gracefully drains.

## Pre-Stop Hook

```yaml
lifecycle:
  preStop:
    exec:
      command: ['/bin/sh', '-c', 'sleep 15']
```

Runs BEFORE SIGTERM.

For:
- Wait for LB to deregister
- Custom cleanup
- API call to drain

## Common preStop

### Sleep (LB Drain)
```yaml
preStop:
  exec:
    command: ['sleep', '15']
```

For 15s, pod keeps serving in-flight; LB notices removal.

### HTTP Endpoint
```yaml
preStop:
  httpGet:
    path: /shutdown
    port: 8080
```

App's /shutdown does cleanup.

### Drain Custom
```yaml
preStop:
  exec:
    command: ['./drain.sh']
```

Custom script.

## Why preStop Sleep

Race between:
- Pod gets DeletionTimestamp
- Endpoint controller removes from Service
- kube-proxy updates iptables
- LB stops sending

LB may send to "dying" pod for ~10s.

Sleep 15s in preStop: pod alive; serves these requests.

Then SIGTERM; drain in-flight; exit.

## Total Time

```
preStop (15s)
  + SIGTERM (app drains, e.g., 30s)
  + terminationGracePeriodSeconds (60s)
```

Total: up to 60s for graceful.

terminationGracePeriodSeconds includes preStop time.

## PDB

PodDisruptionBudget protects from voluntary disruptions:
```yaml
spec:
  minAvailable: 2   # at least 2 must be available
  selector:
    matchLabels:
      app: web
```

Voluntary: drain, kubectl delete.
Involuntary: node crash (PDB doesn't apply).

## Drain Process

```bash
kubectl drain my-node
```

Internally:
1. Cordon node
2. Evict pods one by one (PDB respected)
3. Wait for graceful shutdown each
4. Node empty

## Anti-Patterns

### Ignore SIGTERM
```python
# BAD
while True:
    serve_request()
```

SIGTERM ignored; SIGKILL kills; in-flight lost.

### Long Shutdown Without Time
```python
def handle_sigterm():
    sleep(60)   # but grace is 30s
```

SIGKILL before done.

### No PreStop for LB-Aware
Cloud LB takes seconds to deregister; pod must serve those.

## Best Practices

- SIGTERM handler always
- terminationGracePeriodSeconds enough for slow shutdown
- preStop sleep for LB drain (15-30s)
- Test shutdown in staging
- PDB for HA
- Log shutdown events

## Example: Production Web

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
  - name: web
    lifecycle:
      preStop:
        exec:
          command: ['sleep', '15']
    readinessProbe:
      httpGet: {path: /ready, port: 8080}
```

App SIGTERM:
- Stop accepting new
- Wait for in-flight (max 30s)
- Exit

Total grace: 60s (15 preStop + ~30 drain + buffer).

## ReplicaSet Behavior

Rolling update:
- New pod ready
- Old pod marked for termination
- Old pod drains (preStop + SIGTERM)
- New pod takes traffic

Zero downtime if graceful + readiness probe works.

## StatefulSet

Reverse order during update. Same shutdown sequence.

For DBs: extra care; checkpoint before exit.

## Job

```yaml
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 30
      containers:
      - name: job
        ...
```

Same handling.

## Custom Drain Logic

For complex (consumer drain):
```python
def shutdown():
    # Stop consuming
    consumer.pause()
    # Wait for in-flight messages
    wait_for_acks(timeout=20)
    # Disconnect
    consumer.close()
```

For Kafka consumer.

## Sidecar Shutdown

With native sidecar (1.28+):
- App SIGTERM first
- App drains
- Sidecar SIGTERM
- Sidecar flushes (logs, metrics)

For log shipper: flushes pending logs before exit.

## SIGKILL Aftermath

If app hits SIGKILL:
- TCP RST to clients (no FIN)
- Data buffers unflushed
- DB connections leaked
- File descriptors leaked

Kernel cleans up; but app state inconsistent.

## Container Restart Behavior

For restartPolicy: Always:
- Container died → restart
- Pod stays
- New container with same SA, volumes

Different from pod restart (kubelet recreates pod).

## Operations

```bash
# Trigger graceful delete
kubectl delete pod my-pod

# Watch
kubectl get pod my-pod -w

# Force (skip graceful)
kubectl delete pod my-pod --force --grace-period=0
```

Force only for stuck pods.

## Cloud LB Drain

ALB / NLB:
- Deregister target group
- Drain timeout (configurable)
- Stop new connections
- Existing connections finish

K8s pod preStop should outlast this drain window.

For LB drain 30s: preStop sleep 30+s.

## Testing

Spin up; delete:
```bash
kubectl delete pod my-pod
# Check logs for "received SIGTERM"
# Check requests in-flight finish
# Check pod terminates cleanly
```

If sees errors: increase grace period or fix shutdown logic.

## Common Mistakes

- SIGTERM ignored (forced)
- grace too short (SIGKILL)
- No preStop (LB sends to dying)
- Tight test (don't catch issues until prod)

## PDB + Graceful

PDB tracks "ready" pods. Pod terminating but not yet gone: NOT ready.

If PDB minAvailable=2 and 2 ready + 1 terminating: drain blocks until terminating done.

## SIGKILL Reasons

- terminationGracePeriodSeconds expired
- `--force` delete
- Node failure (kubelet unreachable)
- Container OOM kill

App might catch SIGTERM but exceed time.

## Quick Refs

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ['sleep', '15']
```

```python
# Python SIGTERM
signal.signal(signal.SIGTERM, lambda s, f: graceful_shutdown())
```

## Interview Prep

**Mid**: "Graceful shutdown in K8s."

**Senior**: "PreStop sleep purpose."

**Staff**: "Zero downtime deploy mechanics."

## Next Topic

→ [T05 — Health Probes](T05-Health-Probes.md)
