# L13/C15 — Logging in K8s

## Topics

- **T01 Logging Architecture Patterns** — Node-level (DaemonSet), sidecar (per pod), or app push (direct from app to backend).
- **T02 Fluent Bit / Fluentd / Vector DaemonSets** — Tail /var/log/containers; parse; enrich with K8s metadata; ship to backend.
- **T03 Loki & ELK on K8s** — Loki indexes only labels (cheap); ELK indexes content (powerful but expensive).

## Logging Patterns

```
Pattern 1: Node DaemonSet (recommended)
┌─────────────────────┐
│  Pod 1   Pod 2  ... │
│   ↓       ↓         │
│   stdout → kubelet  │
│   ↓                 │
│   /var/log/containers/...
│   ↓                 │
│   Fluent Bit DS     │ → Loki / ES / S3
└─────────────────────┘

Pattern 2: Sidecar
Container [main] [log-shipper] → ...

Pattern 3: App push
App → backend directly (no shipper)
```

Node DaemonSet is the dominant pattern. One agent per node tails all pod logs.

## Fluent Bit Config Highlights

```ini
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            cri
    Tag               kube.*
    Refresh_Interval  5

[FILTER]
    Name                kubernetes
    Match               kube.*
    Merge_Log           On
    Keep_Log            Off
    K8S-Logging.Parser  On

[OUTPUT]
    Name   loki
    Match  *
    Url    http://loki:3100/loki/api/v1/push
    Labels job=fluent-bit, $kubernetes['namespace_name']
```

## Loki vs ELK Tradeoffs

| | Loki | ELK / OpenSearch |
|---|---|---|
| Index | Labels only | Full text |
| Cost | Low (S3/object storage) | High (search infra) |
| Query | LogQL (PromQL-like) | KQL / Lucene |
| Use | High-volume, label-driven queries | Full-text investigations |

## Common Issues

- High-cardinality labels (e.g., user_id as label) blow up Loki index → keep labels for low-cardinality only
- Multiline logs (Java stack traces) → configure multiline parser
- Log loss on node restart → buffer to disk; configure max retries
- Backend overload → throttling, retries, DLQ-equivalent

## Interview Themes

- "Compare Loki, ELK, and cloud-native logging"
- "How do you avoid log loss?"
- "Multi-line logs — how does Fluent Bit parse them?"
- "Why is logging expensive at scale?"
