# L22/C03 — RabbitMQ

## Topics

- **T01 Exchanges, Queues, Bindings** — Routing model
- **T02 Quorum Queues, Streams** — Modern replicated queue
- **T03 Clustering** — HA

## Concepts

```
Producer → Exchange → (bindings) → Queue → Consumer
```

### Exchange Types
- **direct**: route by exact routing key
- **topic**: route by pattern (`order.*.created`)
- **fanout**: broadcast to all bound queues
- **headers**: route by message headers

### Binding
A rule linking exchange to queue with optional routing key/pattern.

## Sample
```python
import pika

conn = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
ch = conn.channel()

ch.exchange_declare('orders', exchange_type='topic')
ch.queue_declare('order_processing', durable=True)
ch.queue_bind(exchange='orders', queue='order_processing', routing_key='order.*.created')

ch.basic_publish(exchange='orders',
                 routing_key='order.us.created',
                 body=msg,
                 properties=pika.BasicProperties(delivery_mode=2))  # persistent
```

## Queue Types

### Classic Queues (legacy)
- Original; mirroring optional
- Being deprecated

### Quorum Queues (modern)
- Built on Raft consensus
- Fault-tolerant by default
- Use for: business-critical persistence

```python
ch.queue_declare('orders', arguments={'x-queue-type': 'quorum'})
```

### Streams
- Append-only log (similar to Kafka)
- Replayable
- Use for: event sourcing within RabbitMQ

```python
ch.queue_declare('events', arguments={'x-queue-type': 'stream'})
```

## Clustering

3+ nodes form a cluster.
- All metadata replicated
- Queues (classic mirrored or quorum) replicated
- Use a load balancer in front

### Federation
Cross-cluster message routing (across DCs).

### Shovel
Move messages between clusters/queues.

## RabbitMQ vs Kafka

| | RabbitMQ | Kafka |
|---|---|---|
| Pattern | Queue-centric | Log-centric |
| Routing | Flexible (exchanges) | Topic + partition |
| Throughput | 10K-100K/sec | Millions/sec |
| Latency | Sub-ms | Few ms |
| Use | Task queue, complex routing | High-throughput streams |
| Replay | Limited (streams type) | First-class |

## When RabbitMQ

- Complex routing patterns
- Lower throughput needs
- Diverse client libraries (every language has good support)
- Classic queue/task workloads

## Common Patterns

### Work Queue
- Producer → queue → N workers
- Round-robin or fair distribution

### Pub/Sub
- fanout exchange → N queues → N consumer groups

### RPC
- Reply-to header pattern
- Caller creates a temporary reply queue, sets in message, consumer replies to it

### Dead Letter Exchange (DLX)
```python
ch.queue_declare('main', arguments={
    'x-dead-letter-exchange': 'dlx',
    'x-dead-letter-routing-key': 'dead'
})
```

## Operating

- Memory + disk thresholds (back-pressure triggers)
- Set message TTL where appropriate
- Monitor: queue depth, consumer count, message rate
- Quorum queues for durability
- Plugin: management UI, Shovel, Federation, Prometheus

## Interview Themes

- "RabbitMQ exchange types"
- "Compare Quorum queues and classic"
- "When RabbitMQ over Kafka?"
- "DLX pattern"
- "RabbitMQ clustering"
