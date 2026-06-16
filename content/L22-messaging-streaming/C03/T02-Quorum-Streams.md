# L22/C03/T02 — Quorum Queues, Streams

## Learning Objectives

- Use modern RabbitMQ queues
- Compare types

## Quorum Queue

Raft-based:
- 3-5 replicas
- Strong consistency
- HA via leader election

```python
ch.queue_declare(queue='X', durable=True, arguments={'x-queue-type': 'quorum'})
```

## Vs Classic Mirrored

| | Classic Mirrored | Quorum |
|---|---|---|
| Algorithm | GM | Raft |
| Recovery | manual | auto |
| Memory | high | low |
| Throughput | medium | medium |
| Use case | legacy | modern |

For new: quorum.

## Stream Queue

Append-only log:
- Like Kafka
- Replayable

```python
ch.queue_declare(queue='X', arguments={
    'x-queue-type': 'stream',
    'x-max-length-bytes': 10000000000  # 10 GB
})
```

## Consumer

```python
ch.basic_qos(prefetch_count=100)
ch.basic_consume(
    queue='X',
    arguments={'x-stream-offset': 'first'}
)
```

Replay from start.

## Stream Use Cases

- Event sourcing
- Audit logs
- Multi-consumer with replay

## Compared to Kafka

| | Stream (RabbitMQ) | Kafka |
|---|---|---|
| Protocol | AMQP / native | Native |
| Throughput | high | very high |
| Maturity | newer | mature |
| Ecosystem | smaller | huge |

For: stream-like in RabbitMQ ecosystem.

## Throughput

Quorum: 30k-100k msg/sec.
Stream: 200k-1M msg/sec.

## Lazy Mode

For very large queues:
- Disk-backed
- Lower memory
- Slower

```python
queue_declare arguments={'x-queue-mode': 'lazy'}
```

## Mirrored Deprecation

Classic mirrored deprecated in 3.10+.

Migrate to quorum.

## Best Practices

- Quorum for HA queues
- Stream for replayable
- 3-5 replicas
- Monitor leader health

## Common Mistakes

- Mirrored on new (deprecated)
- Single-replica quorum (no HA)
- Stream without retention limits

## Quick Refs

```python
# Quorum
queue_declare(arguments={'x-queue-type': 'quorum'})

# Stream
queue_declare(arguments={'x-queue-type': 'stream'})

# Offset
basic_consume(arguments={'x-stream-offset': 'first|last|TIMESTAMP'})
```

## Interview Prep

**Mid**: "Quorum vs mirrored."

**Senior**: "Stream use."

## Next Topic

→ [T03 — Clustering](T03-RabbitMQ-Clustering.md)
