# L18/C02 — ELK Stack

## Topics

- **T01 Elasticsearch Architecture** — Distributed search engine
- **T02 Logstash & Beats** — Ingestion pipeline
- **T03 Kibana** — UI
- **T04 Index Lifecycle Management (ILM)** — Hot/warm/cold tiers

## ELK / Elastic Stack

E (Elasticsearch) + L (Logstash) + K (Kibana). Plus B (Beats — lightweight shippers).

```
Apps + logs files
   ↓
[Beats / Fluent Bit / Vector]
   ↓
[Logstash] (optional; parse, enrich, transform)
   ↓
[Elasticsearch] (store + index)
   ↓
[Kibana] (query + visualize)
```

## Elasticsearch Architecture

Built on Lucene. Distributed, sharded.

### Concepts
- **Index**: collection of documents
- **Shard**: piece of an index (data, by hash of _id)
- **Replica**: copy of a shard for HA + read scaling
- **Node**: an Elasticsearch process
- **Cluster**: many nodes

### Document
JSON; arbitrary structure (with optional schema/mapping):
```json
{
  "@timestamp": "2026-06-09T12:00:00Z",
  "service": "payments",
  "level": "error",
  "user_id": 42,
  "message": "card declined"
}
```

### Indexing
On write, every field is indexed for search (inverted index for text, doc values for aggregation).

### Querying
- Full-text search (analyzed text fields)
- Term queries (exact match)
- Range queries (numbers, dates)
- Aggregations (group by, histograms, percentiles)

```json
GET logs-*/_search
{
  "query": {
    "bool": {
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1h"}}},
        {"term": {"service": "payments"}},
        {"term": {"level": "error"}}
      ]
    }
  },
  "aggs": {
    "by_error": {
      "terms": {"field": "error.keyword"}
    }
  }
}
```

### Sizing
- ~50 GB per shard is the rule of thumb
- 1-2× shard count of nodes
- 1 replica for redundancy
- Hot tier: NVMe, indexed; warm: spinning/cheap SSD; cold: S3-backed (frozen tier with searchable snapshots)

## Logstash

JVM-based ingestion + transformation. Inputs → filters → outputs.

```ruby
input {
  beats { port => 5044 }
}

filter {
  if [type] == "nginx" {
    grok { match => { "message" => "%{COMBINEDAPACHELOG}" } }
    date { match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ] }
  }
  geoip { source => "clientip" }
}

output {
  elasticsearch {
    hosts => ["http://es:9200"]
    index => "nginx-%{+YYYY.MM.dd}"
  }
}
```

Heavy. Many teams skip it: Beats / Fluent Bit ship directly to Elasticsearch.

## Beats

Lightweight shippers (Go):
- **Filebeat** — log files
- **Metricbeat** — system metrics
- **Packetbeat** — network packets
- **Auditbeat** — audit logs
- **Winlogbeat** — Windows events
- **Heartbeat** — uptime monitoring

```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths: ['/var/log/containers/*.log']
  processors:
    - add_kubernetes_metadata:
        host: ${NODE_NAME}

output.elasticsearch:
  hosts: ['https://es:9200']
  username: filebeat
  password: ${ES_PASSWORD}
```

## Kibana

UI for:
- Discover (search logs)
- Visualize (charts)
- Dashboard (assembled charts)
- Lens (drag-drop chart builder)
- Alerting
- Maps (geo)
- Machine learning (anomaly detection)

## Index Lifecycle Management (ILM)

Manage tiers of data automatically:

```json
{
  "policy": {
    "phases": {
      "hot":  { "actions": { "rollover": {"max_size": "50gb", "max_age": "1d"} } },
      "warm": { "min_age": "7d",  "actions": { "shrink": {"number_of_shards": 1}, "forcemerge": {"max_num_segments": 1} } },
      "cold": { "min_age": "30d", "actions": { "freeze": {} } },
      "delete": { "min_age": "90d", "actions": { "delete": {} } }
    }
  }
}
```

Hot (fast, expensive) → warm (slower, cheaper) → cold (frozen, cheapest) → delete.

## OpenSearch

AWS fork of Elasticsearch (after Elastic changed license to SSPL).
- API-compatible with older Elasticsearch
- AWS-managed: OpenSearch Service
- OpenSearch Dashboards = Kibana fork

Most companies on AWS now use OpenSearch instead of Elastic stack.

## When ELK / OpenSearch

- Need full-text search
- Complex queries beyond label filtering
- Existing investment
- Compliance requires it

## When Not (vs Loki)

- High volume + need search → ELK
- High volume + label filtering enough → Loki (much cheaper)
- Mix: route some logs to ELK (errors, audit), some to Loki (debug, info)

## Common Issues

- **Cluster red** (missing primary shards) — disk full, node lost
- **Cluster yellow** (missing replicas) — single node or replication broken
- **Slow queries** — too many fields, wrong shard count, no ILM tier
- **High disk usage** — no ILM, no rollover, retention too long
- **Mapping explosion** — dynamic field creation from high-cardinality JSON

## Operating

- Always have at least one master-eligible majority quorum
- Use dedicated master nodes (3 minimum for HA)
- Hot nodes: NVMe SSD
- Reserve memory for filesystem cache (half heap, half OS)
- Heap: 50% of RAM, max 31 GB (compressed oops)

## Interview Themes

- "Elasticsearch sharding strategy"
- "ELK vs Loki — when each?"
- "Index Lifecycle Management — explain"
- "Cluster yellow — what's wrong?"
- "Sizing for 100 GB/day of logs"
