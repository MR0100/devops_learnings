# L22/C03/T01 — RabbitMQ Exchanges, Queues, Bindings

## Learning Objectives

- Use RabbitMQ
- Understand routing

## RabbitMQ

AMQP-based:
- Exchanges (routers)
- Queues (storage)
- Bindings (rules)

## Exchange Types

### Direct
Routing key exact match.
- "events.user.created" → queue listening for that

### Topic
Pattern match (* and #):
- "events.*" matches "events.user.created"
- "events.#" matches deeper

### Fanout
Broadcast to all bound queues.

### Headers
Match by message headers.

## Setup

```python
import pika

conn = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
ch = conn.channel()

ch.exchange_declare(exchange='events', exchange_type='topic')
ch.queue_declare(queue='user-events')
ch.queue_bind(exchange='events', queue='user-events', routing_key='events.user.*')
```

## Publish

```python
ch.basic_publish(
    exchange='events',
    routing_key='events.user.created',
    body=json.dumps(data),
    properties=pika.BasicProperties(delivery_mode=2)  # persistent
)
```

## Consume

```python
def callback(ch, method, properties, body):
    process(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

ch.basic_consume(queue='user-events', on_message_callback=callback)
ch.start_consuming()
```

## Acknowledgment

- Auto: ack on receive
- Manual: ack after processing

For at-least-once: manual.

## Prefetch

```python
ch.basic_qos(prefetch_count=10)
```

Max 10 unacked per consumer. Backpressure.

## Persistence

Durable queue:
```python
ch.queue_declare(queue='X', durable=True)
```

Survives broker restart.

Persistent message:
```python
properties=pika.BasicProperties(delivery_mode=2)
```

Written to disk.

## Mirrored Queue (Legacy)

```bash
rabbitmqctl set_policy ha-all "^" '{"ha-mode":"all"}'
```

For HA. Replaced by Quorum Queues.

## Quorum Queue (Modern)

```python
ch.queue_declare(queue='X', durable=True, arguments={'x-queue-type': 'quorum'})
```

Raft-based; better HA.

For: prod.

## Streams (Modern)

```python
ch.queue_declare(queue='X', arguments={'x-queue-type': 'stream'})
```

Like Kafka log; replayable.

## TTL

```python
queue_declare(queue='X', arguments={'x-message-ttl': 60000})  # 60 sec
```

Old messages expire.

## Dead Letter

```python
queue_declare(queue='X', arguments={
    'x-dead-letter-exchange': 'dlx',
    'x-message-ttl': 30000,
})
```

Expired / nacked → DLX.

For: retry / debug.

## Use Cases

- Job distribution (queue)
- Notification (fanout)
- Event routing (topic)
- RPC pattern

## Compared to Kafka

| | RabbitMQ | Kafka |
|---|---|---|
| Pattern | queue + topic | stream |
| Replay | limited | yes |
| Throughput | medium | high |
| Latency | low | low |
| Use | task distribution | event log |

## Best Practices

- Quorum queues prod
- Manual ack
- Prefetch tuned
- Dead letter for failures
- TTL for old

## Common Mistakes

- Auto ack (loss)
- No prefetch (overwhelm)
- Mirrored queue old (use quorum)
- No persistent

## Quick Refs

```python
exchange_declare / queue_declare / queue_bind
basic_publish / basic_consume / basic_ack / basic_nack
basic_qos(prefetch_count=N)
```

```bash
rabbitmqctl list_queues / list_exchanges / list_bindings
rabbitmqadmin
```

## Interview Prep

**Mid**: "RabbitMQ basics."

**Senior**: "Exchange types."

**Staff**: "RabbitMQ vs Kafka."

## Next Topic

→ [T02 — Quorum Queues, Streams](T02-Quorum-Streams.md)
