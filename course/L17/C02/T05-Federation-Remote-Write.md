# L17/C02/T05 — Federation & Remote Write

## Learning Objectives

- Scale Prometheus horizontally
- Aggregate metrics

## Federation

Hierarchical Prom:
```
Global Prom
   ↓ scrapes /federate
Cluster Prom A    Cluster Prom B
   ↓ scrapes targets    ↓
Targets               Targets
```

## /federate

```yaml
- job_name: 'federate'
  metrics_path: '/federate'
  params:
    'match[]':
      - '{job="api"}'
      - '{job="db"}'
  honor_labels: true
  static_configs:
    - targets:
      - 'prom-cluster-a:9090'
      - 'prom-cluster-b:9090'
```

Cluster Proms exposes data; global pulls.

For: aggregate views.

## Limits

Federation:
- Limited bandwidth
- Synchronous (slow)
- All-or-nothing per scrape

For massive scale: Remote Write better.

## Remote Write

Stream samples to remote:
```yaml
remote_write:
  - url: http://thanos-receive/api/v1/receive
    queue_config:
      max_samples_per_send: 10000
      capacity: 100000
```

For: long-term, cross-cluster.

## Remote Write Receivers

- Thanos Receive
- Cortex / Mimir
- VictoriaMetrics
- Prometheus (with remote_read enabled)
- Various cloud services (AMP, GMP)

## AMP (Amazon Managed Prometheus)

```yaml
remote_write:
  - url: https://aps-workspaces.us-east-1.amazonaws.com/workspaces/WS/api/v1/remote_write
    sigv4:
      region: us-east-1
```

AWS-managed; cheap. For: cloud-native.

## GMP (Google Managed Prometheus)

```yaml
- url: https://monitoring.googleapis.com/v1/projects/PROJ/location/global/prometheus/api/v1/write
```

For: GCP.

## Throughput

Single Prom remote write:
- 100k-1M samples/sec typical
- Tune queue_config for throughput

## Failure Handling

```yaml
queue_config:
  capacity: 100000
  max_samples_per_send: 10000
  batch_send_deadline: 5s
  max_shards: 200
```

Backoff + retry built-in.

## Network Cost

Cross-region:
- Egress charges
- ~1-2 GB/day per million samples (compressed)

For: budget.

## Remote Read

Query remote:
```yaml
remote_read:
  - url: http://thanos-querier/api/v1/read
    read_recent: false
```

For: long-term history queries.

## Use Remote Only

If everything remote:
- Local TSDB small (just WAL)
- All queries via remote
- Higher latency

## Hybrid

Common:
- Local: recent (24h-30d)
- Remote: long-term (years)

Querier merges.

## Thanos Sidecar

Alternative to remote write:
```
Prometheus + Sidecar
   ↓ Sidecar uploads blocks to S3 (every 2h)
```

For: object storage backed.

## Sidecar vs Remote Write

| | Sidecar | Remote Write |
|---|---|---|
| Latency | 2h delay | real-time |
| Network | block upload | continuous |
| Storage | S3 (compressed) | varies |
| Use case | Long-term archive | Multi-cluster + real-time |

## Cortex / Mimir

Multi-tenant Prom:
- Receives via remote write
- Stores in object storage
- Queries via API

For: managed Prom-as-a-service.

Cortex → Mimir (rename; Grafana Labs).

## VictoriaMetrics

Drop-in Prom replacement:
- Faster
- Less memory
- Same query language
- Cluster version

For: scale.

## Choose Long-Term

| | Thanos | Mimir | VictoriaMetrics |
|---|---|---|---|
| Architecture | Sidecar + Store + Querier | Multi-component | Single binary or cluster |
| Storage | S3 etc. | S3 etc. | Local or remote |
| Multi-tenant | Limited | Yes | Yes |
| Maturity | High | Growing | High |

## Scrape & Forward

Lightweight Prom:
```
Agent Prom (scrape only)
   ↓ remote write
Long-term backend
```

`--enable-feature=agent`: agent mode.

For: edge collectors.

## Multi-Cluster Pattern

```
Cluster A: Prom + sidecar
Cluster B: Prom + sidecar
Cluster C: Prom + sidecar
       ↓ all upload to S3
Thanos Store reads S3
Thanos Querier ← user queries
```

Global view.

## Federation Pattern (Older)

```
Global Prom federates A, B, C
But: limited to aggregated metrics
```

For aggregate dashboards only.

## Best Practices

- Remote write for long-term + cross-cluster
- Hot local + cold remote
- Tune queue_config
- Monitor remote write metrics
- Agent mode for edge

## Common Mistakes

- Federation for full data (use remote write)
- No backpressure handling
- Single point: long-term storage
- No remote = lose data after retention

## Quick Refs

```yaml
# Federation
- job_name: federate
  params:
    'match[]': [...]
  static_configs:
    - targets: [prom1:9090, prom2:9090]

# Remote write
remote_write:
  - url: ENDPOINT
    queue_config: {...}

# Agent mode
--enable-feature=agent
```

## Interview Prep

**Mid**: "Federation."

**Senior**: "Remote write."

**Staff**: "Prom at scale."

## Next Topic

→ [T06 — Thanos, Cortex, Mimir for Long-Term Storage](T06-Thanos-Cortex-Mimir.md)
