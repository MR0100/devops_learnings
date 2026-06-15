# L13/C09/T03 — Ambassadors & Adapters

## Learning Objectives

- Apply ambassador / adapter patterns
- Distinguish from generic sidecar

## Variants of Sidecar

### Sidecar
General: enhance / extend app.

### Ambassador
Proxy to external service. App talks to localhost; ambassador forwards.

### Adapter
Normalize app's output (often metrics, logs) to standard format.

## Ambassador Pattern

App talks to `localhost`; ambassador handles external complexity.

```yaml
containers:
- name: app
  image: my-app
  env:
  - name: REDIS_URL
    value: "redis://localhost:6379"
- name: redis-ambassador
  image: redis-proxy
  args: ['--upstream=redis-prod.aws-cluster.com:6379']
```

App connects to `localhost:6379`; ambassador forwards.

Benefits:
- App doesn't know real Redis location
- Ambassador handles auth, failover, retry
- Switch Redis without app change

## Use Cases

### Database Proxy
- Connection pooling
- Failover between primary/replicas
- Auth handling (IAM, certs)

E.g., RDS Proxy as sidecar; app connects local.

### Service Discovery
- Ambassador discovers backend via Consul/etcd
- App talks to fixed endpoint
- Routing dynamic

### Multi-Region Failover
- Ambassador chooses region (latency/health)
- App unaware

## Adapter Pattern

Transform app's output to standard format.

Example: App emits text logs; adapter parses → structured JSON for Datadog.

```yaml
containers:
- name: app
  image: legacy-app   # logs plain text
- name: log-adapter
  image: logstash
  args: ['-f', '/etc/logstash/parse.conf']
  volumeMounts:
  - name: logs
    mountPath: /var/log
```

Adapter:
- Reads /var/log
- Parses
- Emits JSON to backend

App unchanged.

## Common Adapter Uses

### Metrics Normalization
- App emits proprietary metrics
- Adapter converts to Prometheus format
- Prometheus scrapes adapter

### Log Format
- Legacy app: text logs
- Adapter: structured logs

### Protocol Translation
- App speaks HTTP/1
- Adapter accepts HTTP/2 → proxies as HTTP/1

## Sidecar vs Ambassador vs Adapter

| | Sidecar | Ambassador | Adapter |
|---|---|---|---|
| Direction | Mixed | Outbound | Inbound or transform |
| Role | Generic helper | Proxy outbound | Normalize output |
| Example | Log shipper | DB proxy | Format converter |

All same K8s mechanism; different intent.

## Real Implementations

### Cloud SQL Auth Proxy (GCP)
```yaml
- name: cloud-sql-proxy
  image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.x
  args:
  - "--port=5432"
  - "my-project:us-central1:my-instance"
```

App connects to localhost:5432; proxy auth + connects to Cloud SQL.

Ambassador pattern.

### Envoy as Ambassador
Full proxy:
- Load balance
- Retries
- Circuit breaker
- mTLS

### Linkerd Proxy
Smaller; Rust-based.

### Filebeat Adapter
Reads app logs; transforms; sends to ELK.

### Telegraf
Metrics adapter; multi-source to InfluxDB.

## Compose Patterns

App + Ambassador + Sidecar:
```yaml
containers:
- name: app
- name: db-ambassador        # outbound DB proxy
- name: log-shipper          # generic sidecar
- name: metrics-adapter      # transforms metrics
```

Multiple sidecars; each focused.

## When Ambassador

- App speaks simple (localhost)
- External complexity hidden
- Auth/routing centralized

## When Adapter

- App can't be changed (legacy)
- Need standard output format
- Mixed apps; standardize

## When Sidecar (Generic)

- Cross-cutting (logs, metrics)
- Doesn't fit ambassador/adapter

## Avoid

- Ambassador for cluster-wide service (use Service)
- Adapter doing too much (split)
- Many ambassadors (resource overhead)

## Resource Concerns

Each sidecar = 50-200 MB RAM typical.

For 10000 pods × 3 sidecars = 6 TB RAM just sidecars.

Optimize:
- DaemonSet for cluster-wide
- Lightweight sidecars
- Service Mesh consolidates some

## eBPF Alternative

Cilium / similar: handle some sidecar functions in kernel:
- mTLS
- Load balancing
- Observability

Without per-pod sidecar overhead.

For: scale-conscious deployments.

## Real-World Example

E-commerce app:
```yaml
spec:
  initContainers:
  - name: istio-proxy
    restartPolicy: Always   # mesh sidecar
    image: istio/proxyv2
  - name: cloudsql-proxy
    restartPolicy: Always   # ambassador
    image: cloudsql-proxy
  - name: vault-agent
    restartPolicy: Always   # secret syncer (sidecar)
    image: vault-agent
  containers:
  - name: app
    image: my-app
  - name: log-adapter
    image: fluent-bit       # log adapter
```

Multiple sidecars: each focused.

## Lifecycle

For native sidecars (alpha 1.28, beta 1.29, GA 1.33):
- Sidecars start first
- App starts after all sidecars Ready
- Termination reverse

App can depend on sidecars (proxy, secrets, mesh) being ready.

## Common Mistakes

- Sidecar fails: app should fail too (or not?)
- Health check covers only app (sidecar dies silently)
- Over-engineering (many sidecars when 1 enough)
- App tightly coupled to sidecar config

## Best Practices

- Single responsibility per sidecar
- Health check covers critical
- Resource limits
- Document each sidecar's purpose
- Independent updates possible
- Standardize across team

## Operations

```bash
# Container logs (specify container)
kubectl logs my-pod -c ambassador
kubectl logs my-pod -c adapter

# Pod has sidecars
kubectl describe pod my-pod
# Containers: app, sidecar1, sidecar2
```

## Quick Refs

```yaml
# Ambassador
containers:
- name: app
  env: [{name: SERVICE_URL, value: "http://localhost:8080"}]
- name: ambassador
  image: my-proxy
  args: ['--target=external.example.com:443']

# Adapter
containers:
- name: app
  # writes /var/log/app.log
- name: adapter
  image: log-parser
  volumeMounts:
  - name: logs
    mountPath: /var/log
```

## Interview Prep

**Mid**: "Ambassador pattern."

**Senior**: "Sidecar vs adapter."

**Staff**: "Sidecar architecture at 10000-pod scale."

## Next Topic

→ [T04 — Graceful Shutdown & PreStop Hooks](T04-Graceful-Shutdown.md)
