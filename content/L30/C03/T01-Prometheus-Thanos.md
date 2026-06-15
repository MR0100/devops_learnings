# L30/C03/T01 — Prometheus + Thanos

## Learning Objectives

- Build long-term metrics
- Thanos setup

## Architecture

```
Per-cluster:
- Prometheus + Thanos Sidecar
       ↓
       S3

Global:
- Thanos Store (reads S3)
- Thanos Querier (federates Sidecars + Store)
- Thanos Compactor (downsampling)
```

## Install Prometheus

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
```

## Thanos Sidecar

```yaml
prometheus:
  prometheusSpec:
    thanos:
      objectStorageConfig:
        existingSecret:
          name: thanos-secret
          key: thanos.yaml
```

```yaml
# thanos.yaml
type: S3
config:
  bucket: thanos-metrics
  endpoint: s3.amazonaws.com
  region: us-east-1
```

## Thanos Components

```bash
helm install thanos bitnami/thanos
```

Configure:
- Store
- Querier
- Compactor

## Federation

Querier addresses Sidecars + Store:
```yaml
query:
  stores:
    - thanos-sidecar.cluster-1:10901
    - thanos-sidecar.cluster-2:10901
    - thanos-store-gateway:10901
```

## Why Thanos (The Problem It Solves)

Vanilla Prometheus has two limits this capstone is built to overcome: it stores
metrics on **local disk** (so retention is bounded by the node, and a lost node
loses history) and it's **single-cluster** (no global view). Thanos fixes both
without replacing Prometheus: a sidecar ships TSDB blocks to **S3** for
effectively unlimited, cheap retention, and the Querier **fans out** across many
Prometheis plus the object store to give one global PromQL view.

### Rationale & Trade-offs

- **Thanos sidecar (upload) vs Thanos Receive (remote-write)** — sidecar keeps
  Prometheus as the source of truth and is simplest for the demo; Receive
  centralizes ingestion (good for short-lived/edge Prometheis) but you operate a
  stateful write tier. Sidecar for this project.
- **Thanos vs Mimir** — Thanos is the natural bolt-on to existing Prometheus;
  Mimir (also Grafana Labs) is multi-tenant-native and scales further with more
  operational machinery. Mention Mimir as the "next size up."
- **Downsampling is for speed, not just storage** — a 1-year-range dashboard
  querying raw 15s data is slow and huge; 5m/1h rollups make long-range queries
  fast. Raw data is still there for recent, high-resolution debugging.

## Retention

```yaml
compactor:
  retention:
    raw: 30d
    5m: 90d
    1h: 1y
```

Downsampling keeps three resolutions: raw for recent high-fidelity debugging,
5m and 1h rollups so a year-long dashboard query stays fast and cheap. The
Compactor also dedupes and compacts blocks — run exactly **one** Compactor per
bucket (two will corrupt each other).

## Grafana

Datasource: Thanos Querier.

Queries: PromQL same.

## Multi-Cluster

Each cluster: Prometheus + Sidecar.
Central: Querier + Store.

For: global view.

## Best Practices

- S3 backed
- Compaction
- Multi-region S3 replication
- HA Querier

## Common Mistakes

- No object storage
- No compaction
- Single Querier (SPOF)

## Acceptance Criteria

- Prometheus in each cluster ships blocks to S3 via the sidecar
- One Thanos Querier returns a global view across clusters + the Store gateway
- A query older than local Prometheus retention still returns data (proves S3
  history works)
- Exactly one Compactor runs; downsampled resolutions are visible in long-range
  queries

## Quick Refs

```bash
helm install kube-prometheus-stack ...   # Prometheus + sidecar
helm install thanos ...                   # Store + Querier + Compactor
```
```
Sidecar → S3 (long retention)   Querier fans out (global view)
Compactor: downsample + dedup, ONE per bucket
Thanos = bolt-on to Prometheus; Mimir = next size up (multi-tenant native)
```

## Interview Prep

**Junior**: "Why isn't plain Prometheus enough for long-term metrics?" —
Prometheus stores data on local disk, so retention is limited and a lost node
loses history, and one Prometheus only sees its own cluster. Thanos adds cheap
long-term storage in S3 and a global view across many Prometheus instances.

**Mid**: "How does Thanos give long retention and a global view?" — A sidecar
next to each Prometheus uploads its TSDB blocks to S3, so history lives in cheap
object storage instead of on the node. The Thanos Querier then fans out queries
across all the sidecars plus a Store gateway that reads S3, so one PromQL query
sees every cluster and all of history. A Compactor downsamples old data so
long-range queries stay fast.

**Senior**: "Thanos sidecar vs Receive, and Thanos vs Mimir?" — Sidecar keeps
Prometheus as the source of truth and just uploads blocks — simplest, and great
when Prometheus is long-lived. Receive accepts remote-write into a central
stateful tier, which is better for short-lived or edge Prometheis that can't
hold blocks long enough to upload, at the cost of operating that write tier.
Thanos vs Mimir: Thanos is the incremental bolt-on to an existing Prometheus
estate; Mimir is multi-tenant-native and scales further but is more machinery.
I'd reach for Mimir when I have many tenants and very high cardinality; Thanos
when I'm extending Prometheus I already run.

**Staff**: "How do you scale this to millions of active series without it
falling over or bankrupting you?" — The thing that kills Prometheus at scale
isn't sample rate, it's **cardinality** — unbounded label values (user IDs,
request IDs) blow up the head block. So the first lever is governance: cardinality
limits, relabeling to drop high-cardinality labels, and recording rules to
pre-aggregate. Then shard ingestion (functional sharding by team/workload, or
Mimir's horizontal scaling) so no single Prometheus holds everything. On cost,
lifecycle-tier the S3 blocks and lean on downsampling so year-long queries don't
scan raw data. The staff move is treating cardinality as a budgeted resource
with owners, not a thing you discover when Prometheus OOMs.

## Next Topic

→ [T02 — Loki + Grafana](T02-Loki-Grafana.md)
