# L22/C01/T01 — Queues vs Topics vs Streams

## Learning Objectives

- Distinguish models
- Choose for use case

## Queue

- One consumer per message
- Distributes work
- FIFO usually

Examples: RabbitMQ, SQS.

## Topic (Pub/Sub)

- Multiple subscribers
- Each gets copy
- Fanout

Examples: SNS, RabbitMQ exchange.

## Stream

- Append-only log
- Multiple consumers
- Replay from any offset
- Retention

Examples: Kafka, Kinesis, Pulsar.

## Compare

| | Queue | Topic | Stream |
|---|---|---|---|
| Delivery | one consumer | all subs | offset-based |
| Order | FIFO (often) | per topic | partition |
| Replay | rarely | no | yes |
| Retention | until consumed | until consumed | configurable |

## When Queue

- Task distribution
- Each task to one worker
- Order somewhat important

Example: image processing jobs.

## When Topic

- Notification fanout
- Event broadcast
- Decoupled subscribers

Example: order placed → notify shipping + analytics + billing.

## When Stream

- Event log
- Replay
- Multiple consumer groups
- Stateful processing

Example: user activity events.

## Hybrid

Tools support multiple:
- Kafka: stream + pub/sub
- RabbitMQ: queue + topic
- Pulsar: all three
- NATS: pub/sub + JetStream stream

## Delivery Semantics

- At-most-once
- At-least-once
- Exactly-once (rare)

(See T02.)

## Ordering

- None
- Partition / key-based
- Global

Kafka: per-partition.
SQS FIFO: per-message-group.

## Examples

### E-commerce Order
Stream (Kafka):
- Order topic
- Consumers: shipping, billing, analytics
- Replay if down

### Image Resize
Queue (SQS):
- Job posted
- Workers pull
- Each does one

### Notification
Topic (SNS):
- "Order placed" event
- Fanout to email, SMS, push

## Best Practices

- Pick by access pattern
- Queue: work distribution
- Topic: notification
- Stream: event log + replay

## Common Mistakes

- Queue for events (lose history)
- Stream for tasks (overhead)
- Wrong delivery semantics

## Quick Refs

```
Queue:  one worker per message (SQS, RabbitMQ queue)
Topic:  fanout (SNS, RabbitMQ exchange)
Stream: log + replay (Kafka, Kinesis, Pulsar)
```

## Interview Prep

**Junior**: "Queue vs topic vs stream."

**Mid**: "When each."

**Senior**: "System design choice."

## Next Topic

→ [T02 — Delivery Semantics](T02-Delivery-Semantics.md)
