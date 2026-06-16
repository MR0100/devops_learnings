# L17/C02/T06 — Thanos, Cortex, Mimir for Long-Term Storage

## Learning Objectives

- Compare long-term solutions
- Choose for use case

## Need

Prometheus alone:
- 15-30 day retention
- Per-cluster scope
- Limited HA

Long-term solutions add:
- Years retention
- Global view (multi-cluster)
- HA
- Multi-tenancy

## Thanos

Open source; Improbable origin:
- Sidecar (upload to S3)
- Store Gateway (read from S3)
- Querier (federate)
- Receive (remote write target)
- Compactor (block compaction in S3)
- Ruler (rules at global level)

## Architecture

```
Prom + Thanos Sidecar → S3 (blocks)
                    ↑
              Thanos Store
                    ↑
              Thanos Querier ← user queries
                    ↑
              Multiple Sidecars + Stores
```

## Install

```bash
helm install thanos bitnami/thanos \
  --set objstore.config-from-secret=thanos-config \
  --set query.enabled=true
```

## Object Storage

```yaml
type: s3
config:
  bucket: thanos-metrics
  endpoint: s3.amazonaws.com
  region: us-east-1
```

Stores blocks; cheap.

## Querier

Aggregates:
- Sidecars (recent)
- Stores (S3 historical)

```yaml
spec:
  containers:
  - name: querier
    args:
      - query
      - --store=sidecar-prom-1:10901
      - --store=sidecar-prom-2:10901
      - --store=store-gateway:10901
```

## Cortex

Multi-tenant Prom:
- Distributors (write path)
- Ingesters (memory + WAL)
- Store Gateway (S3 read)
- Queriers
- Compactor
- Alertmanager (multi-tenant)

For: Prom as a service.

## Mimir

Cortex fork by Grafana Labs:
- Simpler ops
- Faster queries
- Better multi-tenancy

Replacing Cortex in many shops.

## Comparison

| | Thanos | Cortex/Mimir | VictoriaMetrics |
|---|---|---|---|
| Architecture | Sidecar | Multi-component | Single binary |
| Storage | S3 (blocks) | S3 (chunks) | Local + cluster |
| Multi-tenancy | Limited | Strong | Strong |
| Ingest model | Block-based | Remote write | Remote write |
| Query speed | Medium | Fast | Very fast |
| Ops complexity | Medium | High | Low |

## Choose

### Thanos
- Existing Prom + want long-term
- Sidecar friendly
- OK with 2h ingestion delay

### Mimir
- Multi-tenant
- Need Prom-as-a-service
- Have ops team

### VictoriaMetrics
- Simpler ops
- High perf
- Less ecosystem

For: starting fresh: VictoriaMetrics often. Existing Prom: Thanos.

## Thanos Compactor

```bash
thanos compact \
  --data-dir=/data \
  --objstore.config-file=config.yaml \
  --retention.resolution-raw=14d \
  --retention.resolution-5m=90d \
  --retention.resolution-1h=1y
```

Downsamples blocks for long retention queries.

## Downsampling

```
Raw:  15s samples (14 days)
5m:   5min samples (90 days)
1h:   1hr samples (1 year)
```

For: fast historical queries.

## Mimir Tenant

```yaml
# Per tenant
X-Scope-OrgID: team-a
```

Distributors route per tenant. Storage isolated.

## Mimir Storage Backend

S3, GCS, Azure Blob, Swift.

## Query Performance

Mimir / VictoriaMetrics use parallel querying:
- Split time range
- Parallel ingester queries
- Merge results

For: fast.

## Cost

### Object Storage
$0.02/GB/mo (S3)

For 1 TB: $20/mo.

### Compute
Querier / Store: per-CPU.

For: significant at scale.

## HA

Multiple replicas:
- Thanos Querier: stateless
- Mimir queriers: stateless
- Ingesters: stateful (replication factor 3)

## Sidecar Issues

- Tied to Prom (1:1)
- 2h delay for S3 visibility
- Doubles work per Prom instance

## Receive (Thanos)

Alternative to Sidecar:
```yaml
remote_write:
  - url: http://thanos-receive/api/v1/receive
```

Push to Receive; closer to Mimir model.

## Multi-Cluster Pattern

```
Cluster A: Prom + Sidecar → S3
Cluster B: Prom + Sidecar → S3
Central: Querier reads all Sidecars + Store
```

Global query.

## Multi-Tenant Pattern (Mimir)

```
Team A:  Prom → remote_write → Mimir (tenant-a)
Team B:  Prom → remote_write → Mimir (tenant-b)

Query: Per tenant or admin global
```

## Best Practices

- Object storage for long-term
- Compactor for downsampling
- Multi-cluster: Thanos Sidecar or Mimir remote-write
- Multi-tenant: Mimir
- Backup S3 (versioning)

## Common Mistakes

- No downsampling (slow historical)
- Single replica (no HA)
- No multi-tenancy when needed
- Mix systems (cost)

## Monitoring the Monitor

Prom monitors Prom + Thanos + Mimir.
Backup monitoring tool.

For: avoid blind spots.

## AMP / GMP

Cloud-managed:
- AMP: AWS managed Prom (uses Cortex)
- GMP: GCP managed (uses Monarch internals)

For: avoid ops.

## Quick Refs

```bash
# Thanos
thanos sidecar
thanos store
thanos query
thanos compact
thanos receive

# Mimir
mimir -config.file=mimir.yaml

# VictoriaMetrics
vminsert
vmstorage
vmselect
```

## Interview Prep

**Mid**: "Long-term Prom."

**Senior**: "Thanos vs Mimir."

**Staff**: "Metrics platform."

## Next Topic

→ Move to [L17/C03 — PromQL](../C03/README.md)
