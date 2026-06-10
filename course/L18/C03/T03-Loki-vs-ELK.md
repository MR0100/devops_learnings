# L18/C03/T03 — Cost Tradeoffs vs ELK

## Learning Objectives

- Compare Loki and ELK cost
- Choose by use case

## Loki Cost

- Storage: 10-100× cheaper (S3, no full-text index)
- Compute: less RAM
- Query: depends

For 1 TB logs:
- ELK: ~$300+/mo (indexed)
- Loki: ~$30/mo (S3 chunks)

## ELK Cost

- Storage: ES needs disk + index overhead (~1.2× raw + replicas)
- Compute: heavy JVM (~1-2 GB per index per node)
- Search: rich, fast

## Compute

| | Loki | ELK |
|---|---|---|
| Memory | low (few GB) | high (32 GB+ per node) |
| CPU | low | medium-high |
| Disk | low (S3) | high (SSD) |

## Query

| | Loki | ELK |
|---|---|---|
| Label filter | fast | fast (keyword) |
| Content search | linear scan | inverted index (fast) |
| Aggregation | basic | rich |
| Time series | yes (LogQL) | yes (timelion) |

## When Loki

- Cost-conscious
- Already use Grafana
- Logs as streams (filter by label)
- High volume

## When ELK

- Complex search (full-text)
- SIEM features
- Existing investment
- Rich aggregations

## Real Cost Example

10 TB/month logs, 30-day retention:

### ELK
```
Storage: 10 TB × 1.2 (overhead) × 2 (replica) × $0.20 (SSD) = $4800/mo
Compute: 5-10 nodes × $300/mo = $1500-3000
Total: ~$6000-8000/mo
```

### Loki
```
Storage: 10 TB × 1.1 (overhead) × $0.02 (S3) = $220/mo
Compute: 3 nodes × $150/mo = $450
Total: ~$700/mo
```

10× cheaper. (Approx; varies)

## Hidden Costs

### ELK
- Operational overhead (cluster mgmt)
- Licensing (paid X-Pack features)
- Expertise

### Loki
- Loki is "Grafana-stack" only mostly
- Some features less mature

## Hybrid

Some orgs:
- Recent logs (1 week) in ELK (rich search)
- Long-term in Loki (cheap)

For: best of both.

## Migration

ELK → Loki:
1. Parallel collection
2. Test queries (different syntax)
3. Validate
4. Cut over

Common path; saves cost.

## Feature Compare

| Feature | Loki | ELK |
|---|---|---|
| Structured logs | yes (parse at query) | yes (indexed) |
| Full-text | linear scan | inverted index |
| Numeric range | parse + filter | indexed |
| Geo | limited | full |
| ML | no | yes (paid) |
| Alerting | yes | yes |

## Cardinality

Both careful:
- Loki: stream count
- ELK: index field cardinality

Both can OOM.

## Operations

| | Loki | ELK |
|---|---|---|
| Setup | helm install simple | complex |
| Upgrade | easy | involved |
| HA | S3 + replicas | shards + replicas |
| Backup | S3 native | snapshot to S3 |

## Mature Stacks

### Loki Stack (LGTM)
Loki + Grafana + Tempo + Mimir + Pyroscope.

For: integrated.

### ELK
- Elasticsearch + Logstash + Kibana
- Plus Beats, Watcher, ML

## Vendor Options

- Elastic Cloud (managed ES)
- Grafana Cloud (Loki + others)
- AWS OpenSearch (ES-fork)

For: avoid self-host.

## OSS vs Commercial

ELK:
- OSS still available
- Enterprise (X-Pack paid)
- License changes (AGPL-style; AWS forked → OpenSearch)

Loki:
- AGPL
- Grafana Cloud paid

For: license concerns.

## Decision

```
Cost: Loki
Rich search: ELK
SIEM: ELK
Cloud-native: Loki (simpler)
Grafana shop: Loki
Existing ES: stay
```

## Real Examples

### Loki Adoption
- GitLab
- HelloFresh
- Many K8s shops

### ELK Continues
- Banks
- E-commerce (complex search)
- SIEM users

## Migration Path

If on ELK; cost issue:
1. Audit: what queries used?
2. Test Loki for those
3. Pilot service
4. Expand
5. Retire ELK

Years for large orgs.

## Best Practices

- Match tool to query
- Cost vs feature tradeoff
- Hybrid OK
- Loki: low-cardinality labels
- ELK: ILM + tiers

## Common Mistakes

- ELK for grep workload (Loki cheaper)
- Loki for rich search (limited)
- No retention limit
- Single-node prod

## Quick Refs

```
Loki:    cheap, label-based, streaming
ELK:     rich, full-text, indexed
Hybrid:  recent in ELK, old in Loki
```

## Interview Prep

**Mid**: "Loki vs ELK cost."

**Senior**: "Migration."

**Staff**: "Log platform choice."

## Next Topic

→ Move to [L18/C04 — Collectors & Shippers](../C04/README.md)
