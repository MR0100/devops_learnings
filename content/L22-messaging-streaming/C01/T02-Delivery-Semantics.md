# L22/C01/T02 — At-Most-Once, At-Least-Once, Exactly-Once Delivery

## Learning Objectives

- Understand delivery guarantees
- Choose semantics

## Three Semantics

### At-Most-Once
Message delivered 0 or 1 times.
- May lose
- Never duplicate

### At-Least-Once
Delivered 1+ times.
- Never lose
- May duplicate

### Exactly-Once
Delivered exactly 1 time.
- Hardest
- Idealized

## Reality

Distributed systems:
- At-most-once: easy
- At-least-once: most common
- Exactly-once: marketing term often

## At-Least-Once

Most common. Common pattern:
- Producer sends
- Broker stores
- Consumer ack after processing
- If no ack: resend

Risk: duplicates if consumer crashes after processing, before ack.

For: idempotent consumers handle.

## At-Most-Once

Send and forget. No retries.

For: data OK to lose (metrics, samples).

## Exactly-Once

Requires:
- Idempotent producer
- Transactional commit
- Idempotent consumer

Or:
- Idempotency keys
- Dedupe in consumer

For: payments, critical.

## Idempotent Consumer

Consumer:
- Track processed message IDs
- Skip duplicates

```python
def handle(msg):
    if seen(msg.id):
        return
    process(msg)
    mark_seen(msg.id)
```

## Idempotency Key

App layer:
- Unique key per request
- DB unique constraint
- Reject duplicates

For: HTTP POST safe to retry.

## Kafka Exactly-Once

Within Kafka:
- Idempotent producer (sequence numbers)
- Transactional commit (consume + produce atomic)

Across systems (Kafka → DB): app-level idempotency.

## Trade-Offs

| | At-most | At-least | Exactly |
|---|---|---|---|
| Latency | low | low | higher |
| Throughput | high | high | lower |
| Complexity | simple | medium | complex |
| Use | metrics | events | payments |

## Producer

For at-least-once:
```python
producer.send(topic, value, callback=on_success)
# Retry on failure
```

For at-most-once:
```python
producer.send(topic, value)
# Fire and forget
```

For exactly-once (Kafka):
```python
producer = KafkaProducer(enable_idempotence=True, transactional_id='my-tx')
producer.init_transactions()

producer.begin_transaction()
producer.send(...)
producer.commit_transaction()
```

## Consumer

For at-least-once:
```python
for msg in consumer:
    process(msg)
    consumer.commit()
```

For exactly-once (within Kafka):
- Transaction includes commit + produce
- All-or-nothing

## Common Pattern: Outbox

Postgres write + event:
1. Begin tx
2. Insert record + insert outbox message
3. Commit tx
4. Worker reads outbox; sends to Kafka
5. Mark outbox sent

For: at-least-once with strong consistency.

## Idempotent Operations

```python
def credit_account(user_id, amount, idempotency_key):
    with tx:
        if processed(idempotency_key):
            return cached_result(idempotency_key)
        result = do_credit(user_id, amount)
        record_processed(idempotency_key, result)
        return result
```

## Real Examples

### Stripe
Idempotency keys for all writes.

### Kafka Streams
Exactly-once via transactions.

### SQS
At-least-once (mostly); FIFO offers stronger.

## When Exactly-Once

- Financial transactions
- Inventory decrement
- Critical state changes

Cost: complex; slower.

## When At-Least-Once + Idempotent

Most apps:
- Simpler
- Cheaper
- Idempotent consumer handles dupes

## Best Practices

- At-least-once + idempotency
- Outbox pattern for DB+events
- Test dedupe
- Monitor duplicates

## Common Mistakes

- "Exactly-once" without details
- No idempotency
- Dedupe slow (DB constraint OK)
- Ignore network failures

## Quick Refs

```
At-most-once:  fire forget
At-least-once: ack-based
Exactly-once:  transactional + idempotent

Idempotent consumer: handles dupes
Idempotency key: unique per logical request
Outbox: DB + event together
```

## Interview Prep

**Mid**: "What are the three delivery semantics?" — At-most-once (fire-and-forget; may drop, never duplicates), at-least-once (retry until acked; may duplicate, never drops), and exactly-once (no loss, no duplicate). Most systems use at-least-once because dropping data is usually worse than handling a duplicate.

**Senior**: "Is exactly-once real, and how does it work?" — End-to-end exactly-once is at-least-once delivery plus deduplication. Kafka EOS achieves it within Kafka via idempotent producers (sequence numbers dedupe retries) and transactions (atomic produce + offset commit). Across system boundaries you can't get it for free — you make the consumer idempotent (dedupe key, upsert) so duplicates are harmless, which is cheaper and more robust.

**Staff**: "Design a reliable event flow." — Default to at-least-once with idempotent consumers: every message carries a stable key, the consumer upserts or checks a processed-ID store before acting, and commits offsets only after the side effect succeeds. Use the transactional outbox to publish atomically with the DB write, dead-letter poison messages, and reserve Kafka transactions/EOS for the rare in-Kafka stream-processing case where the overhead is justified.

## Next Topic

→ [T03 — Ordering Guarantees](T03-Ordering.md)
