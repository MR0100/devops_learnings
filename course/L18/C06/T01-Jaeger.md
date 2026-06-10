# L18/C06/T01 — Jaeger

## Learning Objectives

- Use Jaeger
- Set up production

## Jaeger

CNCF; tracing backend:
- Distributed
- Storage: Cassandra, ES, in-memory
- UI for trace search
- OpenTracing compatible (legacy)

## Install

```bash
helm install jaeger jaegertracing/jaeger
```

K8s Operator:
```bash
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/...
```

## Components

- **jaeger-agent**: receives spans (per-host or sidecar) — deprecated in newer versions
- **jaeger-collector**: receives + processes
- **jaeger-query**: query API + UI
- **jaeger-ingester**: from Kafka
- **storage**: Cassandra / ES

## Architecture

```
App → Collector → Storage
                       ↓
         Jaeger UI ← Query
```

Or:
```
App → Agent → Collector → Kafka → Ingester → Storage
```

## Send Traces

OTel:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger-collector:4317
```

Native Jaeger:
```python
from jaeger_client import Config
config = Config(
    config={
        'sampler': {'type': 'const', 'param': 1},
        'local_agent': {'reporting_host': 'jaeger-agent'}
    },
    service_name='my-app'
)
tracer = config.initialize_tracer()
```

(Legacy; prefer OTel.)

## UI

```bash
kubectl port-forward svc/jaeger-query 16686:16686
```

http://localhost:16686

## Search

By:
- Service
- Operation
- Duration
- Tags
- Time range

## Trace View

- Waterfall (spans timeline)
- Service map (auto)
- Logs in span
- Tags

## Storage

### Cassandra
- Production default historically
- Heavy

### Elasticsearch
- Common
- ELK integration

### In-Memory
- Dev only

### Badger
- Embedded; single-node

For prod: Cassandra or ES.

## Retention

```bash
# Cassandra: TTL on tables
ALTER TABLE traces WITH default_time_to_live = 604800;   # 7 days

# ES: ILM policy
```

## Performance

For 1M traces/day:
- Cassandra: 3-5 nodes
- ES: 3 nodes (heavy disk)

## Sampling

Jaeger remote sampling:
- Central config
- Per-service rate
- Adjust without restart

```json
{
  "service_strategies": [
    {
      "service": "api",
      "type": "probabilistic",
      "param": 0.1
    }
  ]
}
```

## Adaptive Sampling

Auto-tune based on traffic.

## OTel Compatibility

OTel can export to Jaeger via OTLP.

Jaeger receives OTLP (recent versions).

For: vendor-neutral.

## Future

Jaeger v2 redesign:
- More on OTel
- Streamlined

## When Jaeger

- OSS
- K8s
- Want UI
- OTel-compatible

## When Tempo Better

- S3 storage (cheaper)
- LGTM stack
- Cost-conscious

## When Honeycomb / Datadog

- Hosted
- Rich query

## Best Practices

- OTel SDK (not Jaeger native)
- Collector buffers
- Sample (1-5% prod)
- ES/Cassandra HA
- Backup storage

## Common Mistakes

- 100% sampling (cost)
- In-memory in prod
- Single-node storage
- Jaeger native SDK (use OTel)

## Compared

| | Jaeger | Tempo |
|---|---|---|
| Storage | Cassandra/ES | S3 |
| Cost | medium | low |
| UI | own | Grafana |
| K8s | strong | strong |

## Quick Refs

```bash
# K8s install (Operator)
kubectl apply -f jaeger-operator.yaml
kubectl apply -f jaeger-instance.yaml

# UI port
16686
```

## Interview Prep

**Mid**: "What's Jaeger."

**Senior**: "Storage choice."

**Staff**: "Tracing platform."

## Next Topic

→ [T02 — Zipkin](T02-Zipkin.md)
