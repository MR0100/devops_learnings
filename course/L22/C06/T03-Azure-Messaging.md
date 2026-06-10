# L22/C06/T03 — Azure Service Bus, Event Hubs

## Learning Objectives

- Use Azure messaging
- Choose between

## Service Bus

Enterprise messaging:
- Queues
- Topics + subscriptions
- Transactions
- Dead letter

## Queue

```python
from azure.servicebus import ServiceBusClient, ServiceBusMessage

client = ServiceBusClient.from_connection_string(conn)
with client.get_queue_sender('my-queue') as sender:
    sender.send_messages(ServiceBusMessage('hello'))
```

## Topic + Sub

```python
with client.get_topic_sender('events') as sender:
    sender.send_messages(...)

with client.get_subscription_receiver('events', 'sub-1') as receiver:
    for msg in receiver:
        process(msg)
```

## Features

- FIFO with sessions
- Duplicate detection
- Schedule messages
- Auto-forwarding
- Transactions

## Event Hubs

Streaming:
- Like Kafka
- Partitions
- Capture to Blob

```python
from azure.eventhub import EventHubProducerClient, EventData

producer = EventHubProducerClient.from_connection_string(conn, eventhub_name='X')
batch = producer.create_batch()
batch.add(EventData('hello'))
producer.send_batch(batch)
```

## Kafka Compatibility

Event Hubs supports Kafka API:
- Use Kafka clients
- Connect to Azure endpoint

For: easy migration.

## Capture

Event Hubs → Blob Storage / Data Lake.

Automatic; for analytics.

## Choose

| | Service Bus | Event Hubs |
|---|---|---|
| Model | queue / topic | stream |
| Throughput | medium | very high |
| Order | sessions | per-partition |
| Use | enterprise messaging | big data ingest |

## Cost

- Service Bus: per million operations
- Event Hubs: per TU (throughput unit)

## Encryption

- TLS in transit
- At-rest by default
- Managed keys or CMK

## Authentication

- Connection string
- SAS token
- Entra ID

## Best Practices

- Service Bus for transactional
- Event Hubs for stream
- Sessions for FIFO
- Capture for analytics

## Common Mistakes

- Wrong tool (Event Hubs for transactions)
- No DLQ
- Static creds (use Entra ID)

## Quick Refs

```python
# Service Bus
ServiceBusClient / get_queue_sender / get_subscription_receiver

# Event Hubs
EventHubProducerClient / EventHubConsumerClient
```

```bash
az servicebus / eventhubs
```

## Interview Prep

**Mid**: "Azure messaging."

**Senior**: "Service Bus vs Event Hubs."

**Staff**: "Azure event architecture."

## Next Topic

→ Move to [L22/C07 — Event-Driven Patterns](../C07/README.md)
