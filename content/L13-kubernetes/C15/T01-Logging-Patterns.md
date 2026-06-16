# L13/C15/T01 — Logging Architecture Patterns

## Learning Objectives

- Pick logging pattern
- Apply for use case

## Three Patterns

| Pattern | Description |
|---|---|
| Node DaemonSet | One agent per node tails all logs |
| Sidecar | One agent per pod |
| App push | App sends directly to backend |

## Node DaemonSet (Recommended)

```
┌─────────────────────────┐
│ Node                    │
│ ┌─────┐ ┌─────┐ ┌─────┐ │
│ │Pod 1│ │Pod 2│ │Pod 3│ │
│ └──┬──┘ └──┬──┘ └──┬──┘ │
│    ↓       ↓       ↓     │
│  /var/log/containers/    │
│         ↓                │
│  ┌──────────────┐        │
│  │ Fluent Bit   │        │
│  │ DaemonSet    │        │
│  └──────┬───────┘        │
└─────────┼────────────────┘
          ↓
   Backend (Loki, ES, S3)
```

App writes to stdout → kubelet collects → /var/log/containers → DaemonSet ships.

### Pros
- One agent per node (efficient)
- App-agnostic
- Standard

### Cons
- Per-pod customization harder
- Agent on every node
- Permission needs (hostPath)

## Sidecar Pattern

```
┌──────────────────────┐
│ Pod                  │
│ ┌──────┐ ┌────────┐  │
│ │App   │ │Sidecar │  │
│ │      │ │(agent) │  │
│ └──┬───┘ └────┬───┘  │
│    ↓ logs    ↓       │
│  shared volume        │
└──────────────────────┘
       ↓
   Backend
```

App writes to volume; sidecar tails + ships.

### Pros
- Per-pod customization
- App-specific parsing
- Decoupled from node

### Cons
- Resource per pod (N × pods × resources)
- More complex
- Doesn't catch crash logs of dead container

## App Push

App sends to backend directly:
- Log to stdout AND push (e.g., HTTP to Datadog)
- App library: e.g., Datadog SDK, fluent-logger

### Pros
- Real-time
- Structured (app knows context)
- Per-app config

### Cons
- App coupled to backend
- Library overhead
- Backend down: lose logs (need queue)

## Hybrid

Common:
- Node DaemonSet: catch-all stdout
- Specific apps: also push to specialized backend
- Sidecar for special cases (legacy file logs)

## Container Log Files

Default location:
```
/var/log/containers/<pod>_<namespace>_<container>-<id>.log
```

Symlinks to:
```
/var/log/pods/<namespace>_<pod>_<id>/<container>/<n>.log
```

Runtime writes JSON or text per line.

## Format

Container Runtime Interface (CRI) format:
```
2024-06-09T10:00:00.000000000Z stdout F <log message>
```

Per line: timestamp, stream, partial/final flag, content.

## DaemonSet (Fluent Bit Example)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels: {app: fluent-bit}
  template:
    metadata:
      labels: {app: fluent-bit}
    spec:
      tolerations:
      - operator: Exists
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.x
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: containers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: config
          mountPath: /fluent-bit/etc
      volumes:
      - name: varlog
        hostPath: {path: /var/log}
      - name: containers
        hostPath: {path: /var/lib/docker/containers}
      - name: config
        configMap: {name: fluent-bit-config}
```

## Multiline Logs

Apps log stack traces over multiple lines:
```
[ERROR] Exception
  at line 1
  at line 2
  at line 3
```

Default: each line separate event.

Parsers join:
```ini
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            cri
    Multiline.parser  java
```

## Structured Logs

App logs JSON:
```json
{"level": "info", "msg": "request handled", "user_id": "123", "duration_ms": 45}
```

DaemonSet parses; sends as structured to backend.

For: queryable fields.

## K8s Metadata Enrichment

DaemonSet adds:
- namespace
- pod
- container
- node
- labels

From K8s API (via kubelet or API server).

## Log Volume

Per pod: stdout volume varies. Common: 1-10 MB/day.

For 10000 pods: 10-100 GB/day. Plan storage.

For verbose apps: 1 TB/day possible.

## Backends

| | Type | Cost |
|---|---|---|
| Loki | Label-indexed | Cheap |
| ELK | Content-indexed | Expensive |
| Datadog | SaaS | Medium-high |
| Splunk | Enterprise | Very expensive |
| CloudWatch | AWS SaaS | Medium |
| S3 + Athena | Lake | Cheap (compute-pay) |

Pick by use case.

## Cost Considerations

Indexing cost dominates:
- Datadog: $0.10/GB ingested
- Loki: cheap (S3 storage)
- ELK: medium

For 100 GB/day: Datadog $300/day = $9k/mo.

Loki: $50-100/mo (S3 storage only).

## Sampling

For high-volume:
- Drop DEBUG in prod
- Sample 10% of high-volume INFO
- All ERRORs

DaemonSet (Vector, Fluent Bit) can filter.

## Pattern Trade-offs

| Pattern | Resource | Customization | Reliability |
|---|---|---|---|
| Node DS | 1× nodes | App-agnostic | High |
| Sidecar | 1× pods | Per-app | Medium |
| App push | None | High | Depends |

Node DS for 90% of cases.

## When Sidecar

- Legacy app logs to file
- App-specific format needs heavy parsing
- Compliance: per-pod isolation

## When App Push

- Real-time critical
- Backend-specific features (e.g., trace correlation)
- App-aware context

## Best Practices

- stdout/stderr (don't write files in app)
- Structured JSON
- Node DaemonSet (Fluent Bit / Vector)
- Loki or S3+Athena for cost
- Datadog/Splunk for ease
- Sample if volume high
- Test log loss

## Common Mistakes

- App writes to file (DaemonSet misses unless mounted)
- DEBUG in prod (cost)
- High-cardinality labels
- No sampling (cost)
- Single backend (no DR)

## Loss Prevention

DaemonSet failures: logs queue in disk; backend issues; retries.

Fluent Bit has built-in disk buffer.

For: durability.

## Multi-Tenant

Per-namespace routing:
- Team A logs → team-A Loki
- Team B logs → team-B Datadog

Routing in DaemonSet.

For: cost attribution + isolation.

## Inspection

```bash
# DaemonSet pods
kubectl get pods -n logging -o wide

# Logs from agent
kubectl logs -n logging fluent-bit-xxx

# Sample container log
kubectl exec -n logging fluent-bit-xxx -- ls /var/log/containers/

# Check parse
kubectl logs my-app | head -1   # raw stdout
# Then in backend: search same content
```

## Quick Refs

```bash
# Install Fluent Bit
helm install fluent-bit fluent/fluent-bit

# Install Loki + Promtail
helm install loki grafana/loki-stack

# Install ELK
helm install elasticsearch elastic/elasticsearch
helm install kibana elastic/kibana
```

## Interview Prep

**Junior**: "Logging in K8s."

**Mid**: "Node DS vs sidecar."

**Senior**: "Logging architecture for 100-team org."

**Staff**: "Cost-optimized logging at PB/day."

## Next Topic

→ [T02 — Fluent Bit / Fluentd / Vector DaemonSets](T02-Log-Agents.md)
