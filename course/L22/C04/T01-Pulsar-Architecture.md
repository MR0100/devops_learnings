# L22/C04/T01 — Pulsar Architecture (Brokers, BookKeeper)

## Learning Objectives

- Understand Pulsar
- Compare to Kafka

## Pulsar

Apache; messaging + streaming:
- Multi-tenant
- Geo-replication built-in
- Compute / storage separated
- Yahoo origin

## Architecture

```
Broker (stateless)
   ↕
BookKeeper (storage; bookies)
   ↕
ZooKeeper (metadata)
```

Brokers handle traffic. BookKeeper stores. Stateless brokers = easy scale.

## Components

### Broker
Handles client connections.
Stateless. Scale freely.

### BookKeeper
Distributed ledger storage.
Replicated across bookies.

### ZooKeeper
Metadata: topics, namespaces, etc.

## Vs Kafka

| | Pulsar | Kafka |
|---|---|---|
| Storage | separated (BookKeeper) | broker-coupled |
| Multi-tenant | strong | basic |
| Geo | native | Mirror Maker |
| Functions | built-in | Streams |
| Maturity | growing | mature |

## Tenancy

```
tenant/namespace/topic
```

```
acme/finance/orders
```

For: multi-tenant.

## Topics

```
persistent://acme/finance/orders
non-persistent://acme/finance/notifications
```

Persistent / not.

## Subscription Modes

- Exclusive (one consumer)
- Failover (one active; others backup)
- Shared (multiple parallel)
- Key_Shared (parallel by key)

## Compute / Storage

Broker = compute (stateless).
BookKeeper = storage.

Scale independently:
- More traffic: more brokers
- More data: more bookies

## Functions

Run code on Pulsar:
```python
def my_function(input, context):
    return process(input)
```

Lightweight stream processor.

## Geo-Replication

```bash
pulsar-admin namespaces set-clusters acme/finance --clusters us-east,us-west
```

Multi-region native.

## Install

```bash
docker run -d -p 6650:6650 -p 8080:8080 apachepulsar/pulsar:latest \
  bin/pulsar standalone
```

## Producer

```python
from pulsar import Client

client = Client('pulsar://localhost:6650')
producer = client.create_producer('persistent://public/default/test')
producer.send(b'hello')
```

## Consumer

```python
consumer = client.subscribe('persistent://public/default/test', 'my-sub')
msg = consumer.receive()
consumer.acknowledge(msg)
```

## Cluster

3+ brokers, 3+ bookies, 3+ ZK.

For HA.

## When Pulsar

- Multi-tenant SaaS
- Geo-replication
- Function processing

## When Not

- K8s + simple → Kafka often easier
- Smaller community

## Ecosystem

- Pulsar IO (connectors)
- Pulsar SQL (queries)
- Functions

## Best Practices

- Separate compute / storage
- Tenancy structure
- Geo-replication
- Use functions sparingly

## Common Mistakes

- Pulsar for simple (Kafka often suffices)
- ZK overlooked
- BookKeeper underspec

## Quick Refs

```bash
pulsar-admin namespaces / topics
pulsar-client produce / consume
```

## Interview Prep

**Mid**: "What's Pulsar."

**Senior**: "Pulsar vs Kafka."

**Staff**: "Multi-tenant messaging."

## Next Topic

→ [T02 — Multi-Tenancy](T02-Pulsar-Multi-Tenancy.md)
