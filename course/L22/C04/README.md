# L22/C04 — Pulsar

## Topics

- **T01 Architecture (Brokers, BookKeeper)** — Storage-compute separation
- **T02 Multi-Tenancy** — Per-tenant isolation

## Apache Pulsar

Yahoo origin (2016). CNCF top-level. Kafka-class throughput + first-class multi-tenancy + tiered storage.

## Architecture

```
[Pulsar Brokers] (stateless)
   ↓ writes to ↓
[BookKeeper] (storage layer; bookies)
   ↑
[Tiered Storage (S3, GCS)] for older data
```

Unlike Kafka (brokers store + serve), Pulsar separates:
- Brokers: stateless serving layer
- BookKeeper: durable storage
- ZooKeeper / Etcd: metadata

### Why Separation
- Scale brokers and storage independently
- Move data to cheaper tier (S3) seamlessly
- No data movement when adding broker

## Multi-Tenancy

Hierarchical:
```
Tenant: company-A
  └── Namespace: production
       └── Topic: orders
```

Per-tenant: quotas, auth, retention policies. Strong isolation.

Good for: SaaS platforms, multi-team K8s environments.

## Geo-Replication

Native multi-region:
- Topic replicated across clusters
- Producer publishes to one cluster, consumer reads from any

## Tiered Storage

- Recent data in BookKeeper (fast)
- Older offloaded to S3 / GCS (cheap)
- Consumers can read transparently across tiers
- Long retention possible without expensive disk

## Subscription Modes

Different patterns within one topic:

### Exclusive
- One consumer; others rejected

### Failover
- One active; others standby

### Shared
- Round-robin across consumers (like a queue)

### Key_Shared
- Hash-partitioned across consumers (key → consistent consumer)

This flexibility differs from Kafka's "consumer group only" model.

## Pulsar Functions

Light-weight stream processing built-in. JavaScript / Python / Go / Java functions transform messages.

## Pulsar IO

Connectors (like Kafka Connect) for moving data in/out.

## Pulsar SQL (Presto)

Query topics with SQL.

## Comparison to Kafka

| | Kafka | Pulsar |
|---|---|---|
| Architecture | Brokers = storage + serving | Brokers stateless; BookKeeper stores |
| Tiered storage | KIP-405 (Kafka 3.6+ tiered storage) | Native |
| Multi-tenancy | Limited | First-class |
| Geo-replication | MirrorMaker (external) | Native |
| Subscription models | Consumer group only | 4 modes |
| Ops complexity | Lower (single stack) | Higher (Pulsar + BookKeeper + ZK) |
| Adoption | Massive | Smaller |

## When Pulsar

- Multi-tenant from day one
- Long retention (need tiered storage)
- Geo-replication required
- Diverse subscription patterns

## When Kafka

- Defaults; most common
- Larger ecosystem
- Simpler ops
- Mature tooling

## Interview Themes

- "Pulsar architecture — what's different"
- "Tiered storage — value"
- "When Pulsar over Kafka?"
- "Subscription modes"
