# L22/C02/T04 — Consumers & Consumer Groups

## Learning Objectives

- Use consumer groups
- Manage offsets

## Consumer

Reads from Kafka:
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'events',
    bootstrap_servers='broker:9092',
    group_id='my-group',
    auto_offset_reset='earliest',
)

for msg in consumer:
    print(msg.value)
```

## Group

Multiple consumers in group:
- Partitions distributed
- Each partition → one consumer
- Parallel processing

```
Topic 12 partitions
Group with 3 consumers:
- Consumer 1: partitions 0-3
- Consumer 2: partitions 4-7
- Consumer 3: partitions 8-11
```

## Rebalance

Trigger:
- New consumer joins
- Consumer leaves
- Topic partitions change

Rebalance:
- Pauses consumption
- Reassigns partitions
- Resumes

For: smooth scaling.

## Offsets

Per partition, per group:
- Last consumed
- Stored in `__consumer_offsets` topic

Commit:
- Auto (default)
- Manual

## Auto Commit

```python
consumer = KafkaConsumer(
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,
)
```

Periodic commit.

Risk: commit before process → message lost.

## Manual Commit

```python
for msg in consumer:
    process(msg)
    consumer.commit()
```

After processing.

For: at-least-once.

## Async Commit

```python
consumer.commit_async()
```

Faster; less reliable.

## Specific Offset

```python
consumer.seek(partition, offset)
```

Replay or skip.

## Reset Strategies

```python
auto_offset_reset='earliest'  # start from beginning
auto_offset_reset='latest'    # only new
auto_offset_reset='none'      # error if no offset
```

For new groups.

## Poll

```python
records = consumer.poll(timeout_ms=1000, max_records=500)
for tp, msgs in records.items():
    for msg in msgs:
        process(msg)
```

For: manual control.

## Heartbeat

Consumer sends heartbeat to coordinator.

If missed (session.timeout.ms): consider dead.

```python
session_timeout_ms=30000
heartbeat_interval_ms=3000
```

## max.poll.interval.ms

```python
max_poll_interval_ms=300000   # 5 min
```

Max time between poll() calls.

For long processing: increase.

## Processing Patterns

### Sync
Process each; commit.

### Batched
```python
for batch in poll():
    process_all(batch)
    consumer.commit()
```

For: throughput.

### Async
Send to thread pool; track completion.

For: parallel CPU.

## Pause / Resume

```python
consumer.pause(partition)
consumer.resume(partition)
```

Control backpressure.

## Lag

```bash
kafka-consumer-groups --describe --group my-group
```

Lag = end offset - current offset.

For: monitoring.

## Lag Alert

```promql
kafka_consumer_lag_sum > 10000
```

For: consumer keeping up.

## Static Membership

```python
group_instance_id='consumer-1'
```

Survives restart without rebalance.

For: stateful processors.

## Best Practices

- group_id meaningful
- Manual commit for at-least-once
- Idempotent process
- Monitor lag
- Pause for backpressure
- Static membership for stable

## Common Mistakes

- Auto commit before process (loss)
- No idempotency (dupes on retry)
- Slow process (timeout)
- Single consumer for hot topic (lag)

## Multi-Topic

```python
consumer.subscribe(['topic1', 'topic2'])
```

Or assign specific partitions:
```python
consumer.assign([TopicPartition('topic', 0)])
```

## Transactional Consumer

```python
KafkaConsumer(
    isolation_level='read_committed'
)
```

Only sees committed transactional messages.

For: exactly-once flow.

## Quick Refs

```python
consumer = KafkaConsumer(
    'topic',
    group_id='X',
    auto_offset_reset='earliest',
    enable_auto_commit=False,
)

for msg in consumer:
    process(msg)
    consumer.commit()

consumer.close()
```

```bash
kafka-consumer-groups --describe --group X
```

## Interview Prep

**Mid**: "Consumer groups."

**Senior**: "Rebalance."

**Staff**: "Consumer at scale."

## Next Topic

→ [T05 — Kafka Connect & Mirror Maker](T05-Kafka-Connect.md)
