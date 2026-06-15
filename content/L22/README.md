# L22 — Message Queues & Event Streaming

## Overview

Asynchronous messaging is how scale works. Kafka, RabbitMQ, Pulsar, NATS — pick the right tool and operate it well.

**7 chapters, 23 topics.**

## Chapter Map

### [C01](C01/) — Messaging Fundamentals
- T01 Queues vs Topics vs Streams
- T02 At-Most-Once, At-Least-Once, Exactly-Once Delivery
- T03 Ordering Guarantees

### [C02](C02/) — Kafka Deep Dive
- T01 Architecture (Broker, ZooKeeper / KRaft)
- T02 Topics, Partitions, Replicas
- T03 Producers & Idempotence
- T04 Consumers & Consumer Groups
- T05 Kafka Connect & Mirror Maker
- T06 Schema Registry
- T07 Operating Kafka in Production

### [C03](C03/) — RabbitMQ
- T01 Exchanges, Queues, Bindings
- T02 Quorum Queues, Streams
- T03 Clustering

### [C04](C04/) — Pulsar
- T01 Architecture (Brokers, BookKeeper)
- T02 Multi-Tenancy

### [C05](C05/) — NATS & JetStream
- T01 When NATS Beats Kafka

### [C06](C06/) — Cloud-Native Messaging
- T01 AWS SQS, SNS, Kinesis, MSK
- T02 GCP Pub/Sub
- T03 Azure Service Bus, Event Hubs

### [C07](C07/) — Event-Driven Architecture
- T01 Event Sourcing
- T02 CQRS
- T03 Saga Pattern
- T04 Outbox Pattern

## Delivery Semantics

| Semantic | Means | Implementation |
|---|---|---|
| At-most-once | May drop | Fire-and-forget |
| At-least-once | May duplicate | Retry + ack |
| Exactly-once | Once, no dup | Idempotent producer + transactional consumer (Kafka EOS) |

Most apps actually want "at-least-once + idempotency on the consumer". Exactly-once is expensive and rarely necessary if consumers are idempotent.

## Kafka Architecture

```
Producers ──► Brokers (replicated) ──► Consumers
              │   │   │
              ▼   ▼   ▼
              Partition replicas across brokers
              (leader/follower, ISR set)
```

- **Partitions** parallelize a topic
- **Replicas** provide durability (min.insync.replicas)
- **Consumer groups** share work across consumers
- **Offsets** track per-consumer position

## Producer Reliability Settings

```
acks=all                          # wait for ISR
enable.idempotence=true           # exactly-once delivery to broker
max.in.flight.requests=5          # allowed with idempotence
retries=Integer.MAX_VALUE         # retry forever
delivery.timeout.ms=120000        # bounded
compression.type=lz4              # or zstd
```

## Consumer Group Semantics

- A topic with N partitions → up to N consumers in a group can parallelize
- More consumers than partitions = idle
- Rebalancing happens on group membership change
- Cooperative rebalancing (since 2.4) reduces stop-the-world

## When to Pick Each

| Need | Pick |
|---|---|
| High-throughput streaming, log-like | Kafka |
| Complex routing patterns | RabbitMQ |
| Multi-tenant, geo-replication, tiered storage | Pulsar |
| Ultra-low-latency request/reply | NATS |
| AWS-native, queue semantics | SQS |
| AWS-native fanout | SNS or EventBridge |
| AWS-native streaming | Kinesis or MSK |

## Operating Kafka in Production

- Use KRaft: production-ready in 3.3, ZooKeeper deprecated in 3.5, ZooKeeper support fully removed in 4.0 (ZK clusters cannot run 4.0)
- Min 3 brokers; 5+ for serious workloads
- Monitor: ISR shrink, under-replicated partitions, request latency
- Partition count: 100s acceptable per broker; 1000s strains JVM heap
- Use Cruise Control for rebalancing
- Consumer lag is the #1 metric

## Recommended Reading

- *Kafka: The Definitive Guide* — Gwen Shapira, Todd Palino
- *Designing Data-Intensive Applications* — Ch 11 (streams)
- Confluent's docs

## Interview Themes

- "Compare Kafka and RabbitMQ"
- "What's exactly-once and when does it actually work?"
- "Design event-driven order processing"
- "Operating Kafka — what's hard?"

## Next

→ [L23 — Caching & CDN](../L23/README.md)
