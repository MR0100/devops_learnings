# L22/C02/T03 — Producers & Idempotence

## Learning Objectives

- Tune producer
- Use idempotent producer

## Producer

Sends to Kafka:
```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='broker:9092',
    acks='all',
    enable_idempotence=True,
    linger_ms=10,
    batch_size=16384,
    compression_type='snappy',
)

producer.send('topic', key=b'k', value=b'v')
producer.flush()
```

## Acks

- 0: no ack (fast; loss possible)
- 1: leader ack (medium)
- all: all ISR ack (slow; durable)

For durability: `all`.

## Idempotent Producer

```python
KafkaProducer(enable_idempotence=True)
```

How:
- Producer ID + sequence
- Broker dedupes

Prevents:
- Duplicate on retry

For: no manual dedupe.

## Transactional

```python
producer = KafkaProducer(
    transactional_id='my-app',
    enable_idempotence=True,
)
producer.init_transactions()

producer.begin_transaction()
producer.send(...)
producer.send_offsets_to_transaction(...)  # for read-process-write
producer.commit_transaction()
```

For: exactly-once.

## Batch

```python
linger_ms=10        # wait up to 10ms to batch
batch_size=16384    # 16 KB
```

More batching = better throughput; more latency.

## Compression

```python
compression_type='snappy'   # or gzip, lz4, zstd
```

- gzip: high compression, slow
- snappy: fast, modest compression
- lz4: fast
- zstd: best ratio + speed

For Kafka 2.1+: zstd often best.

## Buffer

```python
buffer_memory=33554432   # 32 MB
```

Producer-side buffer. If full: send() blocks.

## Retries

```python
retries=2147483647       # max
retry_backoff_ms=100
```

Default high. Mostly fine.

## Max Message Size

```python
max_request_size=1048576   # 1 MB default
```

Broker side:
```properties
message.max.bytes=1048576
```

Both must match for large.

## Key

For partition routing:
```python
producer.send('topic', key=b'user-1', value=b'...')
```

Same key → same partition.

For: per-key ordering.

## Async

```python
future = producer.send(...)
future.add_callback(on_success).add_errback(on_error)
```

Non-blocking.

## Sync (Slow)

```python
result = producer.send(...).get(timeout=10)
```

Per-message wait.

## Throughput

Tune:
- High batch + linger
- Compression
- Many partitions
- Many producer threads

Result: 1M+ msg/sec possible.

## Latency

For low latency:
- linger_ms=0 (no batching)
- acks=1 (not all)
- Small batch_size

Result: < 5 ms.

Trade-off with throughput.

## Send Patterns

### Fire-and-Forget
```python
producer.send(...)
# Don't check result
```

For: metrics; loss OK.

### At-Least-Once
```python
producer.send(...).get()
# Wait, retry if fail
```

### Transactional
For exactly-once across topics.

## Errors

- KafkaError: broker error
- TimeoutError: producer side
- NotLeaderForPartitionError: leader changed (retry)

Most retryable.

## Cluster Connection

```python
bootstrap_servers='broker1:9092,broker2:9092,broker3:9092'
```

List several. Discovers rest.

## TLS / SASL

```python
KafkaProducer(
    security_protocol='SASL_SSL',
    sasl_mechanism='PLAIN',
    sasl_plain_username='...',
    sasl_plain_password='...',
)
```

For: secure clusters.

## Best Practices

- enable_idempotence=True
- acks='all'
- Compression
- Batching tuned
- Keys for ordering / partitioning
- Monitor errors

## Common Mistakes

- acks=0 in critical (loss)
- No batching (low throughput)
- No compression (bandwidth)
- Same key for all (hot partition)
- No error handling

## Monitoring

```promql
kafka_producer_record_send_total
kafka_producer_record_error_total
kafka_producer_request_latency_avg
```

## Quick Refs

```python
producer = KafkaProducer(
    bootstrap_servers='...',
    acks='all',
    enable_idempotence=True,
    compression_type='snappy',
    batch_size=16384,
    linger_ms=10,
)

producer.send(topic, key=k, value=v)
producer.flush()
producer.close()
```

## Interview Prep

**Mid**: "Producer basics."

**Senior**: "Idempotent producer."

**Staff**: "Exactly-once."

## Next Topic

→ [T04 — Consumers & Consumer Groups](T04-Consumers.md)
