# L17/C02/T04 — Prometheus Storage (TSDB, WAL)

## Learning Objectives

- Understand TSDB
- Tune storage

## TSDB

Time-series DB:
- Series = unique (name + labels)
- Samples = (timestamp, value)
- Stored in blocks

## Blocks

```
/var/lib/prometheus/
├─ 01ABC.../          # 2-hour block
│   ├─ chunks/
│   ├─ index
│   ├─ meta.json
│   └─ tombstones
├─ 01DEF.../
├─ wal/               # Write-Ahead Log
└─ queries.active
```

## WAL

Write-Ahead Log:
- Append-only
- Recent samples
- Replayed on restart

For: crash recovery.

## Compaction

Small blocks merged into larger:
- 2h → 6h
- 6h → 24h
- 24h → 5d

For: efficient storage + queries.

## Retention

```yaml
--storage.tsdb.retention.time=30d
--storage.tsdb.retention.size=100GB
```

Default: 15d.

Set both; first hit triggers delete.

## Disk Usage

Per series: ~1-2 bytes/sample compressed.

Estimate:
```
samples/sec = series × 1/scrape_interval
bytes/day = samples/sec × 86400 × 2 bytes
```

For 100k series, 15s interval, 30d:
```
100000 × (1/15) × 86400 × 30 × 2 = ~35 GB
```

## Resource Sizing

For 1M series:
- ~10-15 GB RAM (in-memory)
- ~100 GB disk (30d)
- Few CPU cores

For 10M series: shard.

## Memory

Memory dominated by:
- Series count
- Recent samples (WAL replay)

Tune:
- Reduce cardinality
- Sample less frequently
- Drop unused metrics

## Cardinality Issues

```bash
# Top series
curl localhost:9090/api/v1/label/__name__/values | jq

# Count
curl 'localhost:9090/api/v1/query?query=topk(10, count by (__name__) ({__name__=~".+"}))'
```

For: find offenders.

## Series Churn

When pods restart often: new pod_name → new series.

Old series: still indexed for retention.

For: high churn = high memory.

Mitigate:
- Drop pod label
- Use deployment label

## Backup

Snapshot:
```bash
curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot
# Output: snapshots/SNAP_NAME
```

Copy snapshot to S3.

Restore: copy back.

## Block Compaction

```bash
# Manual
prom-compact   # via promtool

# Auto
Prom does it
```

## Snapshots

```bash
ls /var/lib/prometheus/snapshots/
```

Each: point-in-time copy. Useful for backup.

## Remote Read / Write

```yaml
remote_write:
  - url: http://thanos-receive/api/v1/receive

remote_read:
  - url: http://thanos-querier/api/v1/read
```

For: long-term off Prom local.

## Local vs Remote

| | Local | Remote |
|---|---|---|
| Latency | fast | slow |
| Retention | 15-30 days typical | months/years |
| Cost | disk + ops | storage + network |
| Reliability | one Prom | distributed |

Use both: short hot local + long remote.

## Thanos Sidecar

```
Prometheus + Thanos Sidecar
   ↓ uploads blocks to S3
Thanos Store reads S3
Thanos Querier merges Sidecar + Store
```

For: long-term + global view.

## Disk Type

SSD recommended:
- Random reads (queries)
- Random writes (multiple shards)

HDD: ok for cold (Thanos S3).

## tmpfs

Don't put TSDB on tmpfs (RAM disk): loses on restart.

## Restart

WAL replay can be slow:
- ~minutes for high series count
- During replay: no queries

Tools: --storage.tsdb.wal-segment-size.

## Tuning

```yaml
--storage.tsdb.min-block-duration=2h
--storage.tsdb.max-block-duration=24h
--storage.tsdb.wal-compression
```

## Out-of-Order

Old Prom: rejected.
New (2.39+): allows configurable OOO window.

```yaml
storage:
  tsdb:
    out_of_order_time_window: 10m
```

## Best Practices

- Local 15-30d
- Remote long-term (Thanos / Mimir / Cortex)
- Cardinality monitoring
- Backup snapshots
- SSD disk
- Sized for series count
- WAL replay tested

## Common Mistakes

- HDD for hot Prom
- No retention limit (fills disk)
- Skip remote (no long-term)
- High cardinality (OOM)

## Quick Refs

```bash
# Retention
--storage.tsdb.retention.time=15d

# Snapshot
curl -XPOST /api/v1/admin/tsdb/snapshot

# Cardinality
GET /api/v1/status/tsdb
```

## Interview Prep

**Mid**: "Prometheus storage."

**Senior**: "Long-term storage."

**Staff**: "TSDB scaling."

## Next Topic

→ [T05 — Federation & Remote Write](T05-Federation-Remote-Write.md)
