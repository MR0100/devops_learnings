# L30/C03/T02 — Loki + Grafana

## Learning Objectives

- Build log pipeline
- Cost-effective

## Why Loki (The Core Idea)

Loki's defining design choice is that it **indexes labels, not log content**.
Where Elasticsearch builds a full-text inverted index over every log line (fast
arbitrary search, expensive to store and run), Loki only indexes a small set of
labels and stores the raw log chunks in cheap object storage. You then filter by
label to narrow to a stream and grep within it (`|=`). That's why Loki is
~10× cheaper to operate — and why **label cardinality discipline is everything**:
a high-cardinality label (pod name, request id, trace id) creates a separate
stream per value and destroys the index.

### Rationale & Trade-offs

- **Loki over ELK** — far cheaper storage and ops, "like Prometheus, but for
  logs" (same label model, same Grafana UI). Trade-off: no fast full-text search
  across everything; you must know roughly *which stream* first.
- **S3 backend over local PVs** — durable, cheap, scales independently of nodes.
- **`trace_id` as a log *field*, not a *label*** — keep it in the line (so
  log↔trace correlation works via a derived field) but never as an index label
  (cardinality bomb).

## Architecture

```
Pods → Promtail (DaemonSet) → Loki
                                ↓
                                S3
                                ↑
                              Grafana
```

## Install Loki

```bash
helm install loki grafana/loki-stack \
  --set loki.persistence.enabled=true \
  --set promtail.enabled=true
```

## Loki Config

```yaml
loki:
  storage:
    type: s3
    s3:
      endpoint: s3.amazonaws.com
      bucketName: loki-logs
      region: us-east-1
```

## Promtail

DaemonSet:
```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs: ...
```

## Grafana

Datasource: Loki.

LogQL:
```
{app="api"} |= "error"
{app="api", level="error"} | json | duration > 1000
```

## Multi-Tenant

```yaml
loki:
  config:
    auth_enabled: true
```

Headers:
```
X-Scope-OrgID: team-a
```

## Retention

`limits_config.retention_period` declares *how long* to keep logs — but on its
own it deletes nothing. Enforced retention in Loki is the **compactor's** job:
the compactor must be running with `retention_enabled: true`, and it needs a
`delete_request_store` to track and apply deletions. Without that, the
`retention_period` value is effectively just a query horizon and your S3 bucket
grows forever.

```yaml
limits_config:
  retention_period: 30d          # global default; per-tenant overrides allowed

compactor:
  working_directory: /loki/compactor
  retention_enabled: true        # REQUIRED — turns on deletion
  retention_delete_delay: 2h     # grace window before chunks are removed
  delete_request_store: s3       # REQUIRED when retention_enabled (where delete requests live)
  compaction_interval: 10m
```

Per-tenant / per-stream overrides (e.g. keep audit logs 1y, debug logs 7d):

```yaml
limits_config:
  retention_period: 7d
overrides:
  audit-team:
    retention_period: 365d
```

> Run exactly **one** compactor replica. Two compactors racing on the same
> object store corrupt the index. Verify deletion is actually happening via the
> `loki_compactor_*` metrics, not just by trusting the config.

## Best Practices

- S3 backed (object storage, not local PVs)
- Promtail auto-discovery
- Low cardinality labels (Loki indexes labels, not content)
- Retention enforced via the compactor (`retention_enabled: true`), not just declared
- Single compactor replica
- Per-tenant retention overrides for compliance vs. cost

## Common Mistakes

- High cardinality labels (pod name, request id, trace id as a label — explodes the index)
- Setting `retention_period` but never running the compactor → data never deleted, bucket grows unbounded
- Multiple compactor replicas racing on the same store
- Local storage in prod

## Acceptance Criteria

- Promtail auto-discovers pod logs and ships them to Loki with a small,
  bounded label set
- Logs land in S3, not local disk
- A LogQL query filters by label then greps content (`{app="api"} |= "error"`)
- Retention actually **deletes** old data — verify via `loki_compactor_*`
  metrics, with a per-tenant override demonstrated
- A log line carries `trace_id` as a field (sets up correlation in C03/T04)

## Quick Refs

```bash
helm install loki grafana/loki-stack
```

```
LogQL: {labels} |= "filter"
Index labels (low cardinality), grep content. trace_id = field, NOT label.
Retention deletes only with compactor: retention_enabled + delete_request_store.
One compactor replica.
```

## Interview Prep

**Junior**: "How is Loki different from Elasticsearch for logs?" — Loki indexes
only labels (like Prometheus) and stores the raw log lines in cheap object
storage, where Elasticsearch builds a full-text index over everything. Loki is
much cheaper to run; the trade-off is you filter by label first instead of
searching all text instantly.

**Mid**: "Why does label cardinality matter so much in Loki?" — Each unique
combination of label values is a separate stream and a separate index entry. If
you put something high-cardinality like a pod name, request ID, or trace ID in a
label, you create a huge number of streams and the index explodes — exactly the
cost Loki was designed to avoid. Those values belong *in the log line* as fields,
not as labels.

**Senior**: "How do you actually enforce retention in Loki?" — Setting
`retention_period` alone does nothing — it's just a query horizon. Deletion is
the compactor's job: it must run with `retention_enabled: true` and a
`delete_request_store`, and you run exactly one replica or two of them corrupt
the index. I verify it's working through the `loki_compactor_*` metrics rather
than trusting config, and I use per-tenant overrides so compliance-sensitive
logs (audit) can be kept a year while debug logs expire in days — tuning the
cost/compliance trade-off per stream.

**Staff**: "Logging costs are growing 40% a quarter. How do you get it under
control without losing what matters?" — Logs are the cheapest pillar to overspend
on because volume is unbounded by default. I'd attack it on three axes. First,
cardinality and volume governance: drop or sample chatty/debug logs at the
collector before they ever hit storage, and police labels so the index stays
small. Second, tiered retention by value — short retention for debug, long only
for audit/security, enforced by the compactor with per-tenant overrides. Third,
push teams toward metrics and traces for things they're currently grepping logs
for (a counter is far cheaper than logging every event). The framing for
leadership is unit economics — cost per useful query, not raw GB — and making the
default the cheap path so teams opt *in* to expensive retention, not out of it.

## Next Topic

→ [T03 — OTel Collector Fleet](T03-OTel-Collector.md)
