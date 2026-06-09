# L22/C01 — Messaging Fundamentals

## Topics

- **T01 Queues vs Topics vs Streams** — Distinct patterns
- **T02 At-Most-Once, At-Least-Once, Exactly-Once Delivery** — Semantics
- **T03 Ordering Guarantees** — When messages stay in order

## Queues vs Topics vs Streams

### Queue (Point-to-Point)
- N producers write
- N consumers compete for messages
- Each message goes to ONE consumer
- Used for: work distribution, task queues
- Examples: SQS, RabbitMQ queues, Sidekiq

### Topic (Publish-Subscribe)
- N producers write
- M subscribers each get a copy
- Used for: fan-out, event broadcasting
- Examples: SNS, RabbitMQ topics, Kafka (multi-consumer)

### Stream (Log)
- Append-only ordered log
- Consumers read at their own pace (offsets)
- Replayable
- Used for: event sourcing, CDC, real-time analytics
- Examples: Kafka, Kinesis, Pulsar

## Delivery Semantics

### At-Most-Once
- Message may be lost
- Won't be duplicated
- Fire-and-forget
- Example: UDP-style; metrics push (drop if congested)

### At-Least-Once
- Message will be delivered
- May be duplicated
- Default in most systems (SQS, Kafka without idempotence)
- Requires consumer to handle dupes

### Exactly-Once
- Delivered exactly once
- Expensive; constraints on producer + consumer + transport
- Kafka transactions (within Kafka)
- Often: at-least-once + idempotent consumer = "effectively exactly-once"

Most apps want "at-least-once + idempotent". Truly exactly-once is rare and costly.

## Implementing Idempotent Consumers

Pattern:
1. Each message has an idempotency key (e.g., order_id)
2. Consumer maintains a "processed" set (DB, Redis)
3. On receive: check key; if processed, ack and skip; else process + record key

```python
def process(msg):
    if seen.has(msg.id):
        return ack()
    do_work(msg)
    seen.add(msg.id, ttl=24h)
    return ack()
```

Subtleties:
- TTL on the seen set
- Atomicity of process + record (if fails between, duplicate possible)
- Use DB transaction wrapping both

## Ordering Guarantees

### No Ordering
SQS Standard: best-effort order. Use for tasks without dependencies.

### Partial Ordering (per partition/queue)
Kafka: ordering within a partition.
SQS FIFO: ordering within a MessageGroupId.

### Total Ordering
Hard to scale (single writer needed). Avoid unless required.

### Use Cases for Ordering
- Bank transactions for an account
- State machine events for an entity
- Audit logs for a resource

## Consumer Patterns

### Push vs Pull
- **Push**: broker sends to consumer (e.g., SNS to Lambda)
- **Pull**: consumer fetches (Kafka, SQS)

Pull more controllable (backpressure naturally).

### Consumer Groups (Kafka)
- Multiple consumers in a group share work
- Each partition assigned to one consumer in the group
- More consumers than partitions = idle

### Concurrency Models
- **Single-threaded per partition** (Kafka): ordering preserved
- **Multi-threaded** (SQS): more throughput, no ordering
- **Worker pools** (RabbitMQ): N workers consuming from queue

## Backpressure

When downstream slow:
- Broker holds messages (Kafka retention)
- Consumer pulls slower
- Or producer rejected (throughput limit)
- Or queue grows unbounded (RAM/disk pressure)

Strategies:
- Set max queue size; producer fails fast or blocks
- Scale consumers (HPA on queue depth via KEDA)
- Drop low-priority messages

## Dead Letter Queue (DLQ)

After N failed processing attempts → move to DLQ for inspection.

```
SQS main queue → consumer → fails 5 times → DLQ
```

Without DLQ: failures retry forever or get stuck.

Operations:
- Alarm on DLQ depth > 0
- Manual replay after fixing root cause

## Message Sizing

Most brokers limit message size:
- SQS: 256 KB (or 2 GB with extended client)
- Kafka: configurable, default 1 MB
- RabbitMQ: 128 MB

For larger payloads: store in S3, send pointer in message.

## Choosing

| Need | Pick |
|---|---|
| Work distribution | SQS, RabbitMQ |
| Fanout | SNS, Kafka |
| Event log + replay | Kafka, Kinesis |
| Multi-tenant | Pulsar |
| Lowest latency | NATS |
| Cloud-native AWS | SQS + SNS + EventBridge + MSK |

## Interview Themes

- "Queue vs topic vs stream"
- "Delivery semantics — explain"
- "Idempotent consumer pattern"
- "When does exactly-once actually work?"
- "Ordering guarantees per broker"
