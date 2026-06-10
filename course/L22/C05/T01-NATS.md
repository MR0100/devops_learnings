# L22/C05/T01 — When NATS Beats Kafka

## Learning Objectives

- Know NATS
- Choose when

## NATS

Lightweight messaging:
- Go-based
- Sub-ms latency
- Small binary
- Pub/sub + req/reply

JetStream: persistent layer.

## Install

```bash
docker run -p 4222:4222 -p 8222:8222 nats
```

## Pub/Sub

```python
import nats

async def main():
    nc = await nats.connect("nats://localhost:4222")
    
    # Publish
    await nc.publish("events", b"hello")
    
    # Subscribe
    async def cb(msg):
        print(msg.data)
    await nc.subscribe("events", cb=cb)
```

## Subject

```
events.user.created
events.user.updated
events.order.placed
```

Wildcards:
- `*` single token
- `>` multiple tokens

## JetStream

Persistent + streaming:
```
nats stream add events --subjects "events.>" --max-age 7d
nats consumer add events my-consumer --filter events.user.>
```

## Features

- Persistent storage
- Replay
- Consumer groups
- Exactly-once

## vs Kafka

| | NATS | Kafka |
|---|---|---|
| Latency | sub-ms | ms |
| Throughput | medium-high | very high |
| Footprint | tiny | huge |
| Ops | easy | complex |
| Replay | JetStream | yes |
| Persistence | JetStream | yes |

## When NATS

- IoT / edge (small footprint)
- Real-time low latency
- Microservices messaging
- Simple ops

## When Kafka

- Massive scale (>1M msg/sec)
- Long retention years
- Rich ecosystem
- Existing investment

## Connect Modes

- Cluster (HA)
- Leaf nodes (edge)
- Super-cluster (geo)

## Best Practices

- JetStream for durability
- Subject hierarchy
- Per-subject auth
- Cluster 3+ for HA

## Common Mistakes

- Use NATS for huge scale (limits)
- No JetStream (lose on restart)
- Wildcard everywhere (noise)

## Quick Refs

```bash
nats stream add / sub / pub
nats consumer add / next
```

```python
nc.publish / subscribe / request / reply
```

## Interview Prep

**Mid**: "NATS."

**Senior**: "NATS vs Kafka."

**Staff**: "Messaging choice."

## Next Topic

→ Move to [L22/C06 — Cloud-Native Messaging](../C06/README.md)
