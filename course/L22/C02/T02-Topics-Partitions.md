# L22/C02/T02 — Topics, Partitions, Replicas

## Learning Objectives

- Design topics
- Choose partition count

## Topic

Logical category:
- events
- orders
- logs

## Partition

Topic split into N:
- Distributes load
- Enables parallelism
- Per-partition order

## Choosing Count

Considerations:
- Throughput needed
- Consumer parallelism (1 consumer per partition)
- Future growth
- Per-partition limit (~10 MB/s typical)

Rule of thumb:
```
partitions = max(producer_throughput / per_partition,
                 consumer_throughput / per_partition)
```

## Examples

### Light Traffic
- 6 partitions
- 6 consumers parallel

### Heavy
- 50 partitions
- 50 consumers

### Very Heavy
- 100-200 partitions
- Caution: too many = slow rebalance

## Replicas

Per partition:
- Leader
- N-1 followers

```bash
kafka-topics --create --partitions 12 --replication-factor 3
```

## ISR

Followers caught up.

Leader serves; followers replicate.

If leader fails: ISR follower becomes leader.

## Min ISR

```properties
min.insync.replicas=2
```

For replication 3:
- 2 must be in sync
- If only 1: writes fail

For: prevent split brain.

## Acks

```python
producer = KafkaProducer(acks='all')  # all ISR
producer = KafkaProducer(acks=1)       # leader only
producer = KafkaProducer(acks=0)       # fire-forget
```

`all` + `min.insync.replicas=2`: durable.

## Rack Awareness

```properties
broker.rack=us-east-1a
```

Replicas spread across racks (AZs).

For: AZ failure tolerance.

## Adding Partitions

```bash
kafka-topics --alter --topic X --partitions 24
```

Increases. Reshuffle data (per key changes partition!).

Caution: ordering breaks for existing keys.

## Removing Partitions

Not supported. Create new topic; mirror.

## Partition Reassignment

For:
- Add brokers
- Balance load

```bash
kafka-reassign-partitions --execute
```

Slow; throttle.

## Storage Per Partition

Plan:
- Throughput × retention
- 1 MB/s × 7 days = ~600 GB

For: capacity.

## Compacted Topics

```bash
--config cleanup.policy=compact
```

Keep latest per key. Acts as KV state.

For: stateful stream processors.

## Tombstones

```python
producer.send(topic, key=b'k', value=None)
```

Compaction removes that key.

## Topic Naming

Convention:
```
domain.entity.event
billing.invoice.created
auth.user.logged_in
```

For: organization.

## Best Practices

- 6-50 partitions typical
- replication=3
- min.insync.replicas=2
- Rack awareness
- Naming convention
- Plan future growth (some headroom)

## Common Mistakes

- 1 partition (no parallelism)
- 1000 partitions (slow)
- replication=1 (no HA)
- No rack awareness (zone failure)
- Add partitions without thinking key impact

## Monitoring

```promql
kafka_topic_partitions
kafka_topic_under_replicated_partitions
kafka_topic_offline_partitions
```

Alert on under-replicated.

## Quick Refs

```bash
kafka-topics --list / --describe TOPIC
kafka-topics --create --partitions N --replication-factor R
kafka-topics --alter --partitions N
kafka-reassign-partitions
```

## Interview Prep

**Mid**: "Topic + partition."

**Senior**: "Partition count choice."

**Staff**: "Topic design."

## Next Topic

→ [T03 — Producers & Idempotence](T03-Producers.md)
