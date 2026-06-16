# L13/C09 — Application Patterns

## Topics

- **T01 Init Containers** — Run before main containers. Use for: DB migrations, fetching configs, waiting for dependencies.
- **T02 Sidecars** — Containers running alongside main. Use for: log shippers, service mesh proxies, secret injectors. Dedicated sidecar API: alpha 1.28, on-by-default beta 1.29, GA 1.33 (lifecycle handled).
- **T03 Ambassadors & Adapters** — Variants of sidecars. Ambassador proxies external services; adapter normalizes output.
- **T04 Graceful Shutdown & PreStop Hooks** — `terminationGracePeriodSeconds` (default 30s). Pre-stop hook runs before SIGTERM. Order: preStop → SIGTERM → wait → SIGKILL.
- **T05 Health Probes** — `liveness` (restart on fail), `readiness` (remove from Service endpoints), `startup` (delay other probes until app is up).

## Probe Configuration Wisdom

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3       # 3*10=30s before restart
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
  periodSeconds: 5
  failureThreshold: 1        # immediate removal from endpoints
startupProbe:                # for slow-start apps (Java)
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30       # 30*10=300s grace
  periodSeconds: 10
```

### Probe Anti-Patterns

- Same endpoint for liveness and readiness — readiness fail = restart cascade
- Liveness depending on DB — DB blip restarts every pod
- Initial delay too short → restart loop during startup
- Liveness too aggressive → restart storms under load

## Graceful Shutdown Sequence

```
1. Pod marked Terminating; endpoints controller removes from Service
2. preStop hook runs (e.g., sleep 5 to let in-flight finish)
3. SIGTERM sent to PID 1
4. App should: stop accepting, drain, close connections
5. After terminationGracePeriodSeconds → SIGKILL
```

## Sidecar Native API (alpha 1.28, beta 1.29, GA 1.33)

```yaml
spec:
  initContainers:
  - name: log-shipper
    image: fluent-bit:latest
    restartPolicy: Always     # ← makes this a sidecar
```

## Interview Themes

- "Difference between liveness, readiness, startup probes"
- "How do you ensure zero-downtime deploys?"
- "What's the new sidecar API and why was it added?"
- "PreStop hook — when to use?"
