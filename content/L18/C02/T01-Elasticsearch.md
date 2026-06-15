# L18/C02/T01 — Elasticsearch Architecture

## Learning Objectives

- Operate Elasticsearch
- Understand indexes

## ES

Search engine + analytics:
- Distributed
- Schema-flexible (JSON)
- Full-text search
- Aggregations

## Components

- **Master node**: cluster state
- **Data node**: stores + searches
- **Coordinating node**: routes queries
- **Ingest node**: pre-processing

For: one cluster, multiple roles.

## Install

```bash
helm install elasticsearch elastic/elasticsearch
```

Or:
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8
```

## Index

```bash
curl -X PUT localhost:9200/my-index \
  -H 'Content-Type: application/json' \
  -d '{
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings": {
      "properties": {
        "message": { "type": "text" },
        "level": { "type": "keyword" },
        "timestamp": { "type": "date" }
      }
    }
  }'
```

## Shards

Index split into N shards:
- Spread across data nodes
- Each shard: independent Lucene index
- Replicas for HA

## Mappings

Field types:
- text (analyzed; for search)
- keyword (exact; for aggregation)
- date, integer, boolean, etc.

## Indexing

```bash
curl -X POST localhost:9200/my-index/_doc \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Hello world",
    "level": "info",
    "timestamp": "2026-01-01T00:00:00Z"
  }'
```

## Search

```bash
curl -X POST localhost:9200/my-index/_search \
  -d '{
    "query": {
      "match": { "message": "hello" }
    }
  }'
```

## Aggregations

```json
{
  "aggs": {
    "by_level": {
      "terms": { "field": "level" }
    }
  }
}
```

For: group + count.

## ILM (Index Lifecycle Management)

```
Hot   → Warm   → Cold   → Delete
SSD     HDD     S3       (gone)
```

For: cost-effective retention.

## Hot/Warm/Cold

```yaml
"policy": {
  "phases": {
    "hot": {
      "actions": {
        "rollover": { "max_size": "50GB", "max_age": "7d" }
      }
    },
    "warm": {
      "min_age": "7d",
      "actions": {
        "shrink": { "number_of_shards": 1 },
        "forcemerge": { "max_num_segments": 1 }
      }
    },
    "cold": {
      "min_age": "30d",
      "actions": {
        "freeze": {}
      }
    },
    "delete": {
      "min_age": "90d",
      "actions": { "delete": {} }
    }
  }
}
```

For: auto tier.

## Cluster Health

```bash
curl localhost:9200/_cluster/health
```

- green: all good
- yellow: replicas missing
- red: primary shards missing

## Memory

Heap:
- 50% of host RAM (max 32 GB)
- Off-heap for Lucene

For 64 GB host: 32 GB heap.

## Disk

Estimate:
- Raw logs × ~1.2 (indexing overhead)
- ~~~replica factor (HA)~~~

For 1 GB raw with 1 replica: ~2.4 GB.

## Logstash / Beats

(See L18/C02/T02 for Logstash and Beats.)

## Ingestion

Apps → Logstash / Beats / Fluent Bit → Elasticsearch.

## Queries

```
match:        full text
term:         exact (keyword)
range:        numeric/date
bool:         AND/OR/NOT compose
wildcard:     pattern
fuzzy:        typos
```

## Kibana

(See L18/C02/T03.)

UI for ES.

## Cost

Self-host:
- Cluster: $1000+/mo (3 nodes)
- Storage: per GB

Cloud:
- Elastic Cloud: per node/hour
- AWS OpenSearch: per node/hour

Often: cheaper than Datadog but more ops.

## Alternatives

- OpenSearch (AWS fork after license)
- Quickwit
- ZincSearch (Go, lighter)

## Best Practices

- Daily indices (rolling)
- ILM for tier
- Snapshot to S3
- Shard size: 30-50 GB ideal
- HA: replicas + nodes spread
- Monitor cluster health

## Common Mistakes

- Too many shards
- No ILM (disk fills)
- Single-node prod (no HA)
- Heap > 32 GB (counterproductive)
- No snapshot

## Snapshots

```bash
curl -X PUT localhost:9200/_snapshot/s3_backup \
  -d '{
    "type": "s3",
    "settings": { "bucket": "es-backup" }
  }'

curl -X PUT localhost:9200/_snapshot/s3_backup/snapshot_1
```

For: backup.

## Quick Refs

```bash
# Cluster
GET /_cluster/health
GET /_nodes
GET /_cat/indices

# Index
PUT /index
PUT /index/_doc

# Search
POST /index/_search
GET /index/_count

# ILM
PUT /_ilm/policy/X
```

## Interview Prep

**Junior**: "What is Elasticsearch?" — A distributed search and analytics engine that stores JSON documents in inverted indices, giving fast full-text search and aggregations, commonly used as the log store in the ELK stack.

**Mid**: "Explain shards and replicas." — An index is split into primary shards (each an independent Lucene index) to spread data and parallelize work, and each primary can have replica shards on other nodes for high availability and read throughput; a yellow cluster means replicas are unassigned, red means a primary is missing.

**Senior**: "How does ILM control retention cost?" — Index Lifecycle Management rolls indices through hot→warm→cold→frozen→delete phases, moving older data to cheaper tiers (SSD→HDD→object storage) and shrinking/force-merging along the way, so you pay premium storage only for recent, actively-searched data.

**Staff**: "What breaks Elasticsearch at scale and how do you prevent it?" — Shard explosion (too many small shards bloats cluster state), oversized heap (keep ≤32 GB to stay under compressed-oops), unbounded indices without ILM, and missing snapshots; fix with ~30–50 GB target shards, data streams, dedicated hot/warm node tiers, and S3 snapshots for disaster recovery.

## Next Topic

→ [T02 — Logstash & Beats](T02-Logstash-Beats.md)
