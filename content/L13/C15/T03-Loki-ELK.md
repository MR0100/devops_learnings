# L13/C15/T03 — Loki & ELK on K8s

## Learning Objectives

- Choose between Loki and ELK
- Operate each

## Loki

Grafana's log aggregation:
- Index only labels (not content)
- Cheap (S3 storage)
- Grafana integration
- LogQL query language

## ELK

Elasticsearch + Logstash/Fluentd + Kibana:
- Full-text indexing
- Powerful queries
- Expensive at scale
- Mature ecosystem

## Comparison

| | Loki | ELK |
|---|---|---|
| Indexing | Labels only | Content (full-text) |
| Storage | Cheap (S3) | Expensive (SSD) |
| Query | LogQL | Lucene |
| Cost | Low | High |
| Scale | Easy | Complex |
| Full-text | grep-like | Native |
| Aggregation | Limited | Powerful |

For: log volume + cost-conscious → Loki.
For: rich search needed → ELK.

## Loki Architecture

```
Logs (from agents)
   ↓
Distributor (validates, sharding)
   ↓
Ingester (writes chunks)
   ↓
Storage (S3 chunks + BoltDB index)
   ↑
Querier (reads + LogQL)
   ↑
Grafana
```

## Loki Install

```bash
helm install loki grafana/loki-stack \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=100Gi \
  -n logging --create-namespace
```

Or for production: `loki-distributed` chart (multi-component).

## Promtail / Fluent Bit

Promtail: Grafana's log agent (DaemonSet).

Or Fluent Bit with Loki output.

## Sending Logs

Fluent Bit:
```ini
[OUTPUT]
    Name        loki
    Match       *
    host        loki-gateway
    port        3100
    labels      job=fluentbit, $kubernetes['namespace_name'], $kubernetes['pod_name']
```

## Labels Important

Loki indexes labels. Choose carefully:
- `namespace`: good
- `pod_name`: high cardinality (each pod creates index series)

For high cardinality: increases costs.

Typical:
- namespace
- app
- container
- level (info/warn/error)

Avoid:
- pod_name (unless few pods)
- request_id (very high)

## LogQL

```
# All logs from namespace
{namespace="prod"}

# Filter
{namespace="prod"} |= "ERROR"

# Pipeline
{namespace="prod"} |= "ERROR" | json | line_format "{{ .level }} {{ .msg }}"

# Aggregations
sum by (app) (count_over_time({namespace="prod"} |= "ERROR" [5m]))

# Rate
rate({namespace="prod"}[5m])
```

## Use in Grafana

Data source: Loki.

Explore view: live query.

Dashboard: log panels.

## Cost

For 1 TB/day logs:
- Loki: ~$300-500/mo (S3 + Loki compute)
- Datadog: ~$10,000/mo (ingestion)
- Splunk: $20,000+/mo

Loki cheap when volume high.

## Trade-offs

Loki good for:
- High volume
- Cost-sensitive
- Grafana stack
- Simple queries

Loki limited for:
- Complex aggregations
- Full-text search heavy
- Real-time alerting on content

## ELK

```bash
# Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --set replicas=3 \
  --set resources.requests.memory=8Gi

# Kibana
helm install kibana elastic/kibana

# Logstash (or use Fluent Bit / Fluentd → ES directly)
helm install logstash elastic/logstash
```

## ES Cluster

For production:
- 3+ master nodes (quorum)
- N data nodes (storage + query)
- Optional: ingest nodes, coordinator nodes

Heavy resources:
- 8-32 GB memory per node
- SSD storage
- 1-100 nodes typical

## Sending Logs to ES

Fluent Bit:
```ini
[OUTPUT]
    Name      es
    Match     *
    Host      elasticsearch
    Port      9200
    Index     kube-logs-%Y.%m.%d
    Replace_Dots On
```

Daily index rotation.

## Kibana

Dashboard + query UI:
- Discover: search
- Visualize: charts
- Dashboard: combine
- Lens: drag-drop

For: rich log analytics.

## Lucene Query

```
namespace:prod AND level:ERROR
namespace:prod AND status:[500 TO 599]
@timestamp:[2024-06-09T00:00:00 TO 2024-06-09T23:59:59]
```

Full-text + structured.

## Index Lifecycle

For ES:
- Hot: latest, fast SSD
- Warm: older, slower
- Cold: archive, slow disk
- Delete: after retention

ILM (Index Lifecycle Management) automates.

## Cost

ELK at scale:
- Storage: hot SSD expensive
- Memory: ES wants RAM
- 1 TB/day: ~$5000-10000/mo self-hosted

## OpenSearch

AWS fork of Elasticsearch (after license change). Compatible.

Managed via OpenSearch Service.

## Hybrid

Some teams:
- Loki for general (cheap)
- ELK for specific (audit, security)

Or:
- Recent in ELK (1 month)
- Archive in S3 (1 year)

## Backup

Loki: chunks in S3 (already durable).
ELK: snapshot to S3 via repository.

## Multi-Tenant

Loki tenancy:
- X-Scope-OrgID header
- Per-tenant rate limits
- Per-tenant retention

For: SaaS log platform.

ES tenancy: per-index access controls (X-Pack security).

## Retention

Loki:
```yaml
limits_config:
  retention_period: 720h    # 30 days
```

ES via ILM:
- Delete after 30 days
- Or transition to S3 cold

## Monitoring

Loki self-metrics:
- loki_ingester_chunks_created_total
- loki_request_duration_seconds

ES self-metrics via Prometheus exporter.

## Cardinality

Loki: low-cardinality labels critical.
ES: anything in document; query freely.

For unknown structure: ES easier.

## Choosing

For new K8s:
- Try Loki first (cheap, simple)
- ELK if Loki doesn't fit

For existing ELK: keep.

## Cost Optimization

Loki:
- Compress
- Sample
- S3 lifecycle (Glacier old data)
- Limit retention

ELK:
- ILM tiering
- Index per type (better compression)
- Snapshot + delete

## Common Mistakes

- Loki with high-cardinality labels (defeats purpose)
- ES single-node (no HA)
- No retention (storage forever)
- Wrong agent (Logstash heavy)
- No alerts on index sizes

## Best Practices

- Loki for K8s logs (default)
- 3+ ES nodes if used
- ILM tiering
- Retention policy
- Per-team namespace isolation
- Monitor backends
- Backup configured

## Quick Refs

```bash
# Loki
helm install loki grafana/loki-stack

# Query
http://grafana/explore (Loki data source)
{namespace="prod"} |= "ERROR"

# ES
helm install elasticsearch elastic/elasticsearch
helm install kibana elastic/kibana

# Query in Kibana
namespace:prod AND level:ERROR
```

## Interview Prep

**Mid**: "Loki vs ELK."

**Senior**: "Log retention strategy."

**Staff**: "Logging platform at PB scale."

## Next Topic

→ Move to [L13/C16 — Multi-Cluster](../C16/README.md)
