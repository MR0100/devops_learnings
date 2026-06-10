# L13/C09/T02 — Sidecars

## Learning Objectives

- Use sidecars correctly
- Use native sidecar API (1.29+)

## Sidecar

Container alongside main app in same pod:
- Shares network, IPC, volumes
- Helper functions
- Common: log shipper, proxy, secret syncer

## Why Sidecars

Separation of concerns:
- App focuses on business logic
- Sidecar handles cross-cutting (logs, mesh, secrets)

vs library:
- Sidecar language-agnostic
- Update independently
- Smaller app image

## Classic Pattern

```yaml
spec:
  containers:
  - name: app
    image: my-app:v1
    volumeMounts:
    - name: logs
      mountPath: /var/log
  - name: log-shipper
    image: fluent/fluent-bit
    volumeMounts:
    - name: logs
      mountPath: /var/log
  volumes:
  - name: logs
    emptyDir: {}
```

App writes logs; sidecar reads + ships.

## Common Sidecars

### Log Shipper
Fluent Bit / Vector / Filebeat:
- Read /var/log
- Parse, enrich
- Send to backend (Loki, ES, S3)

### Service Mesh Proxy
Istio: envoy sidecar:
- Intercepts traffic in/out
- mTLS, routing, observability

Auto-injected by mesh.

### Secret Syncer
Vault Agent:
- Authenticates to Vault
- Fetches secrets
- Writes to shared volume

### Database Proxy
- PgBouncer / RDS Proxy local
- Connection pooling
- Failover

### Metrics Exporter
- Custom Prom exporter
- Convert app metrics to Prom format

## Lifecycle Problem (Classic)

In K8s < 1.28:
- Sidecar starts with app
- App finishes; sidecar doesn't know
- Pod stays "running" with just sidecar
- Or: pod terminates; sidecar killed mid-flush

Fix attempts:
- Init container as sidecar (hack)
- App signals sidecar
- Awkward

## Native Sidecar (1.28+)

Init container with `restartPolicy: Always`:
```yaml
spec:
  initContainers:
  - name: log-shipper
    image: fluent/fluent-bit
    restartPolicy: Always   # makes it a sidecar
    volumeMounts:
    - name: logs
      mountPath: /var/log
  containers:
  - name: app
    image: my-app
    volumeMounts:
    - name: logs
      mountPath: /var/log
  volumes:
  - name: logs
    emptyDir: {}
```

Behavior:
- Sidecar starts FIRST (before app)
- Pod Ready when sidecar Ready + app Ready
- On termination: SIGTERM to app first; sidecar last
- Sidecar can flush before exiting

For new K8s: use this.

## Sidecar Order

Sidecars (initContainers with restartPolicy: Always) start before app containers.

Multiple sidecars: sequential.

App containers: after all sidecars Ready.

For: dependencies (mesh proxy must be ready before app traffic).

## Termination Order

For graceful shutdown:
1. SIGTERM to app containers
2. App drains
3. App exits
4. SIGTERM to sidecars
5. Sidecars finish (flush logs, etc.)
6. Pod fully terminated

vs classic: app and sidecar terminate together (mess).

## Use Cases

### Mesh + App
```yaml
initContainers:
- name: istio-proxy
  restartPolicy: Always
  ...
containers:
- name: app
  ...
```

App ready only after mesh proxy ready.

### App + Vault Agent
```yaml
initContainers:
- name: vault-agent
  restartPolicy: Always
  command: ['vault', 'agent', '-config=/etc/vault/config.hcl']
  volumeMounts:
  - name: secrets
    mountPath: /vault/secrets
containers:
- name: app
  volumeMounts:
  - name: secrets
    mountPath: /etc/secrets
  ...
```

Agent fetches secrets; app reads.

## Resources

Sidecar = extra resources per pod:
```yaml
initContainers:
- name: sidecar
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
```

Sum across all containers for pod's request.

## Anti-Pattern: Heavy Sidecar

Envoy sidecar: 50-100 MB RAM × N pods × clusters = big.

For 10000 pods: 500 GB+ RAM just for sidecars.

Alternatives:
- Cilium service mesh (eBPF, no sidecar)
- Reduce coverage

## Sidecar Anti-Patterns

- App-specific logic (use library)
- One sidecar doing too many things (split)
- Tight coupling (independent fail OK)

## Logging Architecture

```
App stdout/stderr → kubelet → /var/log/containers/...
                              ↓
                       Sidecar (or DaemonSet) reads
                              ↓
                       Backend (Loki, Datadog)
```

DaemonSet preferred (one per node vs one per pod). Sidecar for per-pod custom processing.

## Mesh Sidecar Specifics

Envoy (Istio):
- Intercepts traffic via iptables
- mTLS to other pods
- HTTP routing, retries
- Observability

App unaware.

For Linkerd: linkerd-proxy similar.

For Cilium: eBPF; no sidecar (in mesh mode).

## DaemonSet vs Sidecar

| | Sidecar | DaemonSet |
|---|---|---|
| Scope | Per pod | Per node |
| Resource | Per pod (N × resources) | Per node (1 × resources) |
| Customization | Per workload | Cluster-wide |
| Logs | Pod-specific | All pods on node |

For logs: DaemonSet (cheaper).
For mesh: sidecar (per-pod identity).
For secrets per workload: sidecar.

## Probes

App probes don't auto-include sidecars.

For sidecar-dependent app:
```yaml
readinessProbe:
  exec:
    command: ['sh', '-c', 'curl -f http://localhost:15021/healthz/ready']
```

Custom probe checking sidecar too.

Or container-level probes per sidecar (newer K8s).

## Termination Grace

```yaml
terminationGracePeriodSeconds: 60
```

Time for graceful shutdown of all containers.

For mesh: sidecar may need time to drain connections.

## PreStop Hooks

```yaml
lifecycle:
  preStop:
    exec:
      command: ['sleep', '30']
```

Delay before SIGTERM. Allows time for LB to drain pod.

## Common Mistakes

- Sidecar for cluster-wide task (use DaemonSet)
- No resource limits (oversized)
- Sidecar fail = app fail (no health independence)
- Pre-1.28 sidecar lifecycle issues

## Best Practices

- Use native sidecar (1.28+)
- One responsibility per sidecar
- Resources sized
- Independent health
- Termination order respected
- Use Helm/Kustomize for injection

## Auto-Injection

Istio admission webhook auto-injects sidecar:
```yaml
metadata:
  namespace: my-ns
  labels:
    istio-injection: enabled
```

All pods in namespace get sidecar.

For: per-namespace mesh adoption.

## Migration Pre-1.28 → Sidecar API

Old:
```yaml
containers:
- name: app
- name: sidecar
```

New:
```yaml
initContainers:
- name: sidecar
  restartPolicy: Always
containers:
- name: app
```

Cleaner termination.

## When NOT Sidecar

- App + cross-cutting can be solved with shared library
- Cluster-wide (DaemonSet better)
- Stateless function (might be different deployment)

## Quick Refs

```yaml
# Classic
containers:
- name: app
- name: sidecar

# Native (1.28+)
initContainers:
- name: sidecar
  restartPolicy: Always
containers:
- name: app
```

## Interview Prep

**Mid**: "Sidecar use cases."

**Senior**: "Native sidecar API."

**Staff**: "Mesh sidecar at scale."

## Next Topic

→ [T03 — Ambassadors & Adapters](T03-Ambassador-Adapter.md)
