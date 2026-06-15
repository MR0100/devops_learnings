# L22/C01/T03 — Ordering Guarantees

## Learning Objectives

- Choose ordering
- Plan for partition

## Ordering Types

### None
Messages random order. Highest throughput.

### Partition
Within partition: ordered.
Across: not.

Kafka, Kinesis.

### Per-Key
Same key → same partition → ordered.

Kafka with key.

### Global
All messages ordered.
Single partition / sequential.

For: rare. Throughput-limited.

## Kafka Partition Ordering

```
Partition 0: msg1, msg2, msg3
Partition 1: msgA, msgB, msgC

Across: not ordered
```

## Per-User Ordering

```python
producer.send('events', key=user_id, value=...)
```

Same user_id → same partition.

For: per-user state consistent.

## SQS FIFO

```bash
aws sqs create-queue --queue-name my-queue.fifo \
  --attributes FifoQueue=true,ContentBasedDeduplication=true
```

Message group:
```python
sqs.send_message(QueueUrl, MessageBody, MessageGroupId='user-1')
```

Per-group ordered.

## Throughput Trade-Off

- No order: fastest
- Per-partition: fast
- Global: slow

For: scale via partitioning.

## Reordering

In transit:
- Network can reorder
- Async processing reorders
- Retries: rare msg moves

For: app handles.

## Sequence Numbers

Producer adds:
```json
{"seq": 1, "data": ...}
{"seq": 2, "data": ...}
```

Consumer:
- Buffer
- Process in seq order
- Detect gaps

For: at-app level.

## Compaction

Kafka compacted topic:
- Keep only latest per key
- Eventual state

For: state stores.

## Time-Based Order

Stamp:
```json
{"ts": 1700000000, "data": ...}
```

Process in ts order:
- Window-based
- Stream processing (Flink, Kafka Streams)

## Causal Order

For: A → B (B caused by A):
- Use vector clocks
- Or single partition

For: complex.

## Examples

### User Activity
Per-user ordering. Different users: independent.

```
key=user_id
```

### Order Status
Per-order: pending → confirmed → shipped → delivered.

```
key=order_id
```

### Logs
Time order helpful; per-source ordered.

```
key=source_id (per-source ordered)
```

## Anti-Patterns

### Global Order
"All events in order."

Forces single partition. Slow.

### Random Key
No order; can't reconstruct.

### Order Across Topics
Hard; out of scope mostly.

## Reordering Detection

Sequence gap:
```python
last_seq = -1
for msg in stream:
    if msg.seq != last_seq + 1:
        # Gap; reorder happened
    last_seq = msg.seq
```

For: detect.

## Best Practices

- Per-key partition for entity ordering
- Don't require global
- Sequence numbers if needed
- Time-based ordering at consumer
- Idempotent (handles reorder)

## Common Mistakes

- Assume global order
- Hot key (all to one partition)
- No reorder tolerance
- Sequence skipped (consumer breaks)

## Quick Refs

```
None:       fastest; no order
Partition:  Kafka per-partition
Per-key:    use key for hash
FIFO:       SQS FIFO group ID
Global:     1 partition / seq
```

## Interview Prep

**Mid**: "Ordering options."

**Senior**: "Per-key ordering."

**Staff**: "Ordered events at scale."

## Next Topic

→ Move to [L22/C02 — Kafka Deep Dive](../C02/README.md)
