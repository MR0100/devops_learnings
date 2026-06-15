# L18/C03/T01 — Loki Architecture

## Learning Objectives

- Install Loki
- Understand model

## Loki

Log aggregator (Grafana):
- Index labels only (not content)
- Cheap
- LogQL
- S3-backed

## Why Cheap

Vs ELK:
- ES indexes full content
- Loki indexes only metadata
- Storage 10-100× less

## Components

- **Distributor**: receives, validates
- **Ingester**: in-memory + WAL → S3
- **Querier**: reads ingesters + storage
- **Compactor**: index compaction
- **Querier-frontend**: query splitting
- **Index gateway**: index queries

## Install

```bash
helm install loki grafana/loki-stack \
  --set loki.persistence.enabled=true \
  --set promtail.enabled=true
```

## Storage

```yaml
storage:
  type: s3
  s3:
    bucket: loki
    region: us-east-1
    endpoint: s3.amazonaws.com
```

Chunks + index in S3.

## Promtail

Log shipper:
```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
```

Per-node DaemonSet.

## Labels

Like Prometheus:
```
{app="api", env="prod"}
```

Index small (only labels).

For cardinality: critical to keep low.

## Log Lines

Each line: timestamp + content (string).

Content NOT indexed; only labels.

For: cheap.

## Query

```
{app="api"} |= "error"
```

Filter content at query time.

## Streams

Unique labels = stream:
```
{app="api", instance="pod-1"}
{app="api", instance="pod-2"}
```

Two streams.

## Cardinality

- Low cardinality labels: app, env, namespace
- High cardinality (in content): trace_id, user_id

Putting high-cardinality in labels: bad. Massive stream count.

## Architecture Modes

### Monolithic
Single binary; small.

### Microservices
Distributors, ingesters, queriers separate.

For scale.

### SSD (Simple Scalable Deployment)
Middle ground; read/write groups.

## Multi-Tenant

```
X-Scope-OrgID: team-a
```

Per-tenant isolation.

## Retention

```yaml
limits_config:
  retention_period: 30d

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h
```

For: cost.

## Compactor

Merges index files. Cleans deleted.

```yaml
compactor:
  retention_enabled: true
  retention_delete_delay: 2h
```

## Performance

Loki queries:
- Filter by label first (cheap)
- Then content (linear scan)

Fast for label-focused.

Slow for "find string across all":
- Use specific labels first

## Vs ELK

| | Loki | ELK |
|---|---|---|
| Index | labels only | full-text |
| Cost | low | high |
| Query | LogQL filters | DSL rich |
| Search | by label | by content |
| Scale | huge | medium |

## Storage Backends

- S3
- GCS
- Azure Blob
- Local FS
- Cassandra (legacy)

S3 common.

## Multi-Region

Per-region Loki; central query.

## Best Practices

- Low cardinality labels
- Promtail for K8s
- S3 backend
- Compactor enabled
- Per-tenant if many teams

## Common Mistakes

- High cardinality labels (stream explosion)
- ELK queries (different model)
- Too many label values

## Quick Refs

```yaml
# Promtail
clients: [...]
scrape_configs: [...]

# Loki
storage: s3
limits: retention

# Query
{label="value"} |= "filter"
```

## Interview Prep

**Junior**: "What is Loki?" — A log aggregation system from Grafana that indexes only labels (not log content) and stores compressed chunks in object storage, making it much cheaper than full-text systems like Elasticsearch.

**Mid**: "Why is Loki cheaper than ELK?" — ELK builds an inverted index over every field, which is storage- and compute-heavy, whereas Loki indexes just a small set of labels and keeps raw content as cheap S3 chunks, filtering content at query time instead of indexing it.

**Senior**: "What is a stream and why does label cardinality matter?" — A stream is a unique combination of label values, and every distinct combination creates a separate stream; putting high-cardinality data like `trace_id` or `user_id` in labels explodes stream count, blows up the index, and OOMs ingesters, so those belong in the log line, not labels.

**Staff**: "How do you run Loki at scale?" — Use the microservices (or SSD) deployment to scale distributors/ingesters/queriers independently, keep labels low-cardinality, back it with S3 plus a compactor for retention, isolate teams with multi-tenancy (`X-Scope-OrgID`), and design queries label-first so content scans stay bounded.

## Next Topic

→ [T02 — LogQL](T02-LogQL.md)
