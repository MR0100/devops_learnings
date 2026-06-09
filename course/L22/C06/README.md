# L22/C06 — Cloud-Native Messaging

## Topics

- **T01 AWS SQS, SNS, Kinesis, MSK**
- **T02 GCP Pub/Sub**
- **T03 Azure Service Bus, Event Hubs**

## AWS

### SQS
- Queue; pull-based; standard or FIFO
- Per-message charge; near-unlimited TPS (Standard); 300/s/group (FIFO)
- DLQ pattern built-in
- Visibility timeout for processing window

### SNS
- Pub/sub; topic with subscribers
- Subscribers: SQS, Lambda, HTTP, email
- FIFO topics for ordered fanout

### EventBridge
- Event bus with rule-based routing
- AWS service events + custom + SaaS partner events
- Schema discovery
- More features than SNS; higher cost

### Kinesis Data Streams
- Streaming (Kafka-like); shard-based; 1 MB/s write / 2 MB/s read per shard
- Standard fan-out or enhanced fan-out (HTTP/2 push)
- Retention 1-365 days
- Enhanced fan-out consumer dedicated throughput

### Kinesis Firehose
- Streaming ingestion to S3 / Redshift / OpenSearch
- Batch size + window-based delivery

### MSK
- Managed Kafka
- Both provisioned and serverless modes
- IAM auth, encryption

## GCP

### Pub/Sub
- Global topic + subscription
- At-least-once
- Push or pull subscribers
- 7-day message retention default
- Ordered delivery within keys
- Massive scale (Google internal use)

### Pub/Sub Lite
- Cheaper but more limited (zonal)

## Azure

### Service Bus
- Queues + topics
- Premium tier with sessions, dead lettering, scheduled messages
- FIFO queues with sessions

### Event Hubs
- Streaming (Kafka-compatible API)
- Capture to Blob / Data Lake

### Event Grid
- Event routing (similar to EventBridge)

## Choosing on Each Cloud

### AWS

| Need | Pick |
|---|---|
| Simple queue | SQS |
| Fanout pub/sub | SNS |
| Routing structured events | EventBridge |
| High-throughput streaming | Kinesis or MSK |
| Long retention + replay | Kinesis or MSK |
| Cross-account fanout | SNS or EventBridge |

### GCP
- Pub/Sub for nearly everything
- Confluent Cloud Kafka if you need Kafka specifically

### Azure
- Service Bus for queues
- Event Hubs for streaming (Kafka-compatible if needed)
- Event Grid for routing

## Cross-Cloud

- Confluent Cloud (multi-cloud Kafka SaaS)
- Aiven (multi-cloud Kafka/RabbitMQ/Pulsar)
- Self-hosted on Kubernetes (Strimzi for Kafka, RabbitMQ Operator)

## Pricing Snapshot

| Service | Cost (approx) |
|---|---|
| SQS Standard | $0.40 per 1M req |
| SNS | $0.50 per 1M publishes + delivery fees |
| EventBridge | $1 per 1M events |
| Kinesis | $0.015 / shard-hour + $0.014 / 1M PUT |
| MSK Standard | $0.0456 / hr per broker (m7g.large) + storage |
| GCP Pub/Sub | $40 / TB throughput + storage |
| Azure Service Bus Premium | $677 / Messaging Unit / month |

## Common Issues

- SQS visibility timeout < processing time → duplicates
- SNS no retry guarantee on HTTP (use SQS subscriber)
- Kinesis hot shard
- MSK broker scaling pain (broker count must be planned)
- EventBridge rule pattern bugs (silent message drops)

## Interview Themes

- "Compare SQS, SNS, EventBridge, Kinesis"
- "When MSK over Kinesis?"
- "GCP Pub/Sub — what's special?"
- "Cross-cloud messaging strategy"
