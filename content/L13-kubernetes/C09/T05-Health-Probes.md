# L13/C09/T05 — Health Probes

## Learning Objectives

- Configure 3 probe types
- Avoid common pitfalls

## Three Probes

### Liveness
"Is container alive?"
- Failure → kubelet restarts container
- Detect deadlock, hang

### Readiness
"Can container serve traffic?"
- Failure → removed from Service endpoints
- Re-add when passes
- Use: warming up, dependency unavailable

### Startup
"Has container started?"
- Disables liveness + readiness until passes
- Use: slow-start apps (Java with -Xmx 8GB)

## Probe Types

```yaml
# HTTP GET
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    httpHeaders:
    - name: Custom-Header
      value: awesome

# TCP
livenessProbe:
  tcpSocket:
    port: 8080

# Exec command in container
livenessProbe:
  exec:
    command: ['/bin/sh', '-c', 'curl -f http://localhost:8080/healthz']

# gRPC (1.24+)
livenessProbe:
  grpc:
    port: 9090
    service: my.service.v1.HealthCheck
```

## Configuration

```yaml
livenessProbe:
  httpGet: {path: /healthz, port: 8080}
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1
```

- `initialDelaySeconds`: wait before first probe
- `periodSeconds`: between probes
- `timeoutSeconds`: probe timeout
- `failureThreshold`: consecutive failures = unhealthy
- `successThreshold`: consecutive successes = healthy

## Effective Delay

For liveness:
```
failure detected after: failureThreshold × periodSeconds = 3 × 10 = 30s
restart after: failure detected + small delay
```

For app crash detection: 30s typical.

## Liveness Implementation

App's /healthz:
- Check internal state
- Return 200 if alive
- Return 500 if dead

Don't check external (DB):
- DB blip → restart loop
- Liveness should be self-only

```python
@app.get("/healthz")
def healthz():
    if app_is_alive():
        return {"status": "ok"}
    return Response(status=500)
```

## Readiness Implementation

```python
@app.get("/readyz")
def readyz():
    if not db.ping():
        return Response(status=503)
    if cache_warming:
        return Response(status=503)
    return {"status": "ready"}
```

Can fail (transient); pod removed from endpoints; re-added when passes.

## Startup Probe

For slow-start (Java with massive heap):
```yaml
startupProbe:
  httpGet: {path: /healthz, port: 8080}
  failureThreshold: 30
  periodSeconds: 10
```

30 × 10 = 5 min for startup. Liveness/readiness paused until passes.

For Spring Boot, .NET, large JVMs: startup probe critical.

## Common Pitfalls

### Liveness Checks External
```python
@app.get("/healthz")
def healthz():
    db.execute("SELECT 1")   # BAD
    return "ok"
```

DB blip → liveness fails → container restart → new container also fails → CrashLoopBackOff.

Liveness: app internal only.

### Same Probe Path
```yaml
livenessProbe:
  httpGet: {path: /healthz}
readinessProbe:
  httpGet: {path: /healthz}
```

If liveness needs DB (wrong) and DB down: app restarts AND not ready. Conflated.

Use different paths.

### Aggressive Timeouts
```yaml
timeoutSeconds: 1
```

Slow app under load → probe times out → restart → makes worse.

Use 3-5s.

### No Startup Probe for Slow Start
Liveness initialDelaySeconds: 30 may not be enough for Java with 8 GB heap.

Use startup probe.

## Probe Flow

```
Container starts
  ↓
startupProbe (until success)
  ↓
livenessProbe + readinessProbe (continuous)
```

## Network Probe Sidecar

For complex (DB + cache + external):
- Sidecar checks dependencies
- App's readiness checks sidecar
- Decoupled

Or use service mesh.

## Examples

### Web Service
```yaml
startupProbe:
  httpGet: {path: /healthz, port: 8080}
  failureThreshold: 30
  periodSeconds: 10

livenessProbe:
  httpGet: {path: /healthz, port: 8080}
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet: {path: /readyz, port: 8080}
  periodSeconds: 5
  failureThreshold: 1
```

### Java Spring Boot
```yaml
startupProbe:
  httpGet: {path: /actuator/health/liveness, port: 8080}
  failureThreshold: 60
  periodSeconds: 10

livenessProbe:
  httpGet: {path: /actuator/health/liveness, port: 8080}
livenessProbe:
  httpGet: {path: /actuator/health/readiness, port: 8080}
```

Spring Boot 2.3+ has dedicated endpoints.

### Worker (No HTTP)
```yaml
livenessProbe:
  exec:
    command: ['./check-alive.sh']
```

App writes /tmp/healthy file; script checks.

### gRPC
```yaml
livenessProbe:
  grpc:
    port: 50051
```

For gRPC services with health protocol.

## Liveness Restart

```bash
kubectl describe pod my-pod
# Last State: Terminated
# Reason: Error
# Exit Code: 137 (SIGKILL)
# Events: Liveness probe failed
```

For: identify probe-driven restarts.

## ReadinessGates

Beyond probes; signal readiness from external:
```yaml
spec:
  readinessGates:
  - conditionType: cloud.google.com/load-balancer-neg-ready
```

Pod Ready only when external (LB) confirms.

For: precise traffic routing.

## Termination + Probes

During pod termination:
- Probes stop
- Pod marked NotReady
- Removed from endpoints

Plus preStop hook.

## Failure During Probe

```bash
# Logs
kubectl describe pod my-pod | grep -A 5 Events
# Events: Liveness probe failed: HTTP probe failed with statuscode: 500
```

Check app logs for crash.

## Best Practices

- All 3 probes for production
- Startup for slow-start
- Liveness internal only
- Readiness checks dependencies
- Different paths
- Reasonable thresholds
- Test in staging

## Best Practices

- Startup probe: failureThreshold high enough for max start time
- Liveness: ~30s detection (3 × 10s)
- Readiness: faster detection (~5s)
- Don't restart on transient (use readiness)

## Common Mistakes

- Same endpoint for all 3 (defeats purpose)
- Liveness checks DB → CrashLoopBackOff
- No probes → traffic to broken pods
- Aggressive timeouts
- Missing startup probe (Java)

## Anti-Patterns

- Wrap shell in liveness: slow, brittle
- Probe runs as root (privilege escalation)
- Probe paths require auth (probes fail)

## Probe Authentication

Probes don't auth. If endpoint requires:
- Probe path public
- Or use exec with auth

Generally: /healthz and /readyz public.

## Resource Cost

Probes consume resources:
- Every periodSeconds
- For each container
- Across all pods

For 1000 pods × probes every 5s: high traffic.

For: keep periodSeconds reasonable (5-10s).

## Container Probe (1.27+)

Probe per container, not just pod. For sidecar:
```yaml
spec:
  containers:
  - name: app
    livenessProbe: ...
  - name: sidecar
    livenessProbe: ...
```

Sidecar dies: sidecar restarts.

## Inspection

```bash
# Probe failures
kubectl describe pod my-pod | grep -i probe

# Health endpoint
kubectl exec my-pod -- curl localhost:8080/healthz
```

## Quick Refs

```yaml
livenessProbe:
  httpGet: {path: /healthz, port: 8080}
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet: {path: /readyz, port: 8080}
  periodSeconds: 5
  failureThreshold: 1

startupProbe:
  httpGet: {path: /healthz, port: 8080}
  failureThreshold: 30
  periodSeconds: 10
```

## Interview Prep

**Junior**: "Three probe types."

**Mid**: "Why separate liveness + readiness."

**Senior**: "Liveness checking DB — why bad."

**Staff**: "Probe strategy for distributed app."

## Next Topic

→ Move to [L13/C10 — Helm](../C10/README.md)
