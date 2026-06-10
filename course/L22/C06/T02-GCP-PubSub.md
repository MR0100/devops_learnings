# L22/C06/T02 — GCP Pub/Sub

## Learning Objectives

- Use GCP Pub/Sub
- Compare to alternatives

## Pub/Sub

GCP managed:
- At-least-once
- Global
- Push or pull
- Schema validation

## Topics + Subscriptions

```
Topic (events)
├─ Subscription A (push to webhook)
├─ Subscription B (pull from service)
└─ Subscription C (BigQuery sink)
```

Each subscription: independent.

## Publish

```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
future = publisher.publish('projects/X/topics/events', b'hello')
```

## Subscribe

```python
subscriber = pubsub_v1.SubscriberClient()
def cb(message):
    process(message.data)
    message.ack()
subscriber.subscribe('projects/X/subscriptions/my-sub', cb)
```

## Push

Pub/Sub delivers to HTTP endpoint:
```bash
gcloud pubsub subscriptions create my-sub --topic=events \
  --push-endpoint=https://my-app/handler
```

## Pull

App pulls:
```bash
gcloud pubsub subscriptions pull my-sub --auto-ack
```

For: Cloud Run / Functions.

## Ordering

Per ordering key:
```python
publisher.publish('topic', data, ordering_key='user-1')
```

Subscriber receives in order per key.

## Schemas

Validate:
```bash
gcloud pubsub schemas create my-schema --type=AVRO --definition=...
```

## Filters

```bash
gcloud pubsub subscriptions create my-sub --topic=events \
  --message-filter='attributes.type="critical"'
```

Subscription gets subset.

## Dead Letter

```bash
gcloud pubsub subscriptions create my-sub --topic=events \
  --dead-letter-topic=dlq --max-delivery-attempts=5
```

## BigQuery Sink

Pub/Sub → BigQuery directly:
```bash
gcloud pubsub subscriptions create my-sub --topic=events \
  --bigquery-table=PROJ:DS.TABLE
```

For: analytics.

## Pub/Sub Lite

Cheaper; partition-based (like Kafka):
- Lower cost
- Less features
- Regional

## Retention

Default 7 days; up to 31.

```bash
gcloud pubsub subscriptions update my-sub --message-retention-duration=10d
```

## Cost

- ~$0.04 per million messages
- Plus storage if backlog

For: relatively cheap.

## Compared

| | Pub/Sub | Kinesis | Kafka |
|---|---|---|---|
| Cloud | GCP | AWS | self / MSK |
| Model | sub-based | shard-based | partition-based |
| Throughput | huge | per shard | per partition |
| Cost | per message | per shard | infra |

## Best Practices

- Schema for typed
- Filters for subset
- DLQ
- BigQuery sink for analytics
- Ordering when needed

## Common Mistakes

- No DLQ
- Synchronous push (slow)
- No schema

## Quick Refs

```bash
gcloud pubsub topics / subscriptions
gcloud pubsub topics publish / subscriptions pull
```

## Interview Prep

**Mid**: "GCP Pub/Sub."

**Senior**: "Push vs pull."

**Staff**: "GCP messaging."

## Next Topic

→ [T03 — Azure Service Bus, Event Hubs](T03-Azure-Messaging.md)
