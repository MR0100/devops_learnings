# L08/C10 — Messaging & Streaming

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-SQS.md) | SQS (Standard, FIFO, DLQ) | 1 hr |
| [T02](T02-SNS-Fanout.md) | SNS & Fanout Patterns | 0.5 hr |
| [T03](T03-EventBridge.md) | EventBridge (Buses, Rules, Schemas) | 1 hr |
| [T04](T04-Kinesis.md) | Kinesis Data Streams, Firehose, Analytics | 1.5 hr |
| [T05](T05-MSK.md) | MSK (Managed Kafka) | 1 hr |

## SQS Deep Dive

### Standard vs FIFO

| | Standard | FIFO |
|---|---|---|
| Ordering | Best-effort | Strict per MessageGroupId |
| Delivery | At-least-once | Exactly-once within the 5-min dedup window |
| Throughput | Unlimited | 300/s/group; 3000/s with batching |
| Use | Most use cases | Ordering/dedup essential |

### Key Settings
- **Visibility Timeout**: time message is hidden after receive (default 30s)
  - Should be > max processing time
  - Extend during processing if needed
- **Message Retention**: 1 min to 14 days (default 4 days)
- **Receive Wait Time**: 0-20s (use 20 for long polling — saves API calls)
- **Max Message Size**: 256 KB (use S3 for larger; Extended Library)

### DLQ (Dead Letter Queue)
Failed messages after N receives → DLQ for inspection.
- Set Redrive Policy on main queue
- DLQ should outlast main queue retention
- Monitor DLQ depth as alarm

### Polling
```python
# Long polling (recommended)
response = sqs.receive_message(
    QueueUrl=url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,        # long poll
    VisibilityTimeout=60,
)
```

## SNS

Pub/sub messaging.

### Topic Types
- Standard (best-effort order)
- FIFO

### Subscription Targets
- SQS (most common: fanout to multiple queues)
- Lambda
- Email/SMS
- HTTP/HTTPS endpoint
- Kinesis Data Firehose
- SNS in another region (cross-region)

### Filtering
Subscription filters reject events early:
```json
{"eventType": ["order.created"], "amount": [{"numeric": [">", 1000]}]}
```

Saves Lambda invocations & SQS messages.

### Fanout Pattern
```
SNS Topic (event published)
├── SQS Queue A → Service A
├── SQS Queue B → Service B
├── Lambda → real-time processing
└── HTTP endpoint → 3rd-party webhook
```

## EventBridge

The "next gen" event bus.

### Concepts
- **Bus**: default (AWS events) or custom (your events) or partner (SaaS)
- **Rule**: pattern match → target
- **Target**: 30+ types including Lambda, SQS, SNS, Step Functions, ECS task, EventBridge in other region

### Event Pattern
```json
{
  "source": ["myapp.orders"],
  "detail-type": ["OrderPlaced"],
  "detail": {
    "amount": [{"numeric": [">=", 100]}],
    "region": ["us-east-1", "us-west-2"]
  }
}
```

### Schema Registry & Discoverer
EventBridge auto-discovers schemas of events flowing through; generates code bindings.

### Pipes (2022+)
Source → enrichment → target (no Lambda for transformation):
```
SQS → Pipe (filter + enrich via Lambda) → Step Functions
```

### EventBridge vs SNS
| | EventBridge | SNS |
|---|---|---|
| Routing | Pattern matching | Filter only |
| Source | AWS services, custom, SaaS | Your code |
| Target types | 30+ | Limited |
| Schema discovery | Yes | No |
| Throughput | Sustained 10K/s; can request more | Higher per topic |
| Cost | $1/M events | $0.50/M (more for HTTP) |

Use EventBridge for: structured events with routing logic, SaaS integration, schemas matter.
Use SNS for: simple fanout, very high throughput, HTTP webhook delivery.

## Kinesis Data Streams

Real-time data stream (Kafka-like).

### Concepts
- **Stream**: top-level resource
- **Shard**: unit of capacity (1 MB/s write, 2 MB/s read, 1000 records/s write)
- **Record**: data + partition key + sequence number
- **Retention**: 1 day default, up to 365 days

### Consumer Models
- **Standard fan-out**: all consumers share 2 MB/s per shard
- **Enhanced fan-out**: each consumer gets dedicated 2 MB/s (HTTP/2 push)
- **Lambda integration**: poll-based or enhanced fan-out

### Partition Keys
Like Kafka: hash determines shard. Bad keys → hot shards.

### On-demand mode
Auto-scales shards; pay per usage. Use when traffic is variable.

## Kinesis Data Firehose

Streaming ingestion to destinations:
- S3
- Redshift (via S3 intermediary)
- OpenSearch
- Splunk, Datadog, etc.

Buffering window (60-900 sec) + size (1-128 MB) triggers delivery.

Common pattern: app → Firehose → S3 (Parquet) → Athena queries.

## MSK (Managed Kafka)

AWS-managed Kafka cluster.

### Variants
- **Provisioned**: choose broker size & count; pay for cluster
- **Serverless**: auto-scale; pay per usage

### Why MSK over Self-Managed
- AWS handles patching, broker replacement, ZK→KRaft migration
- Multi-AZ
- IAM authentication option

### MSK Connect
Managed Kafka Connect for connectors (sources, sinks).

## Choosing Messaging on AWS

| Use Case | Pick |
|---|---|
| Simple queue, decoupling | SQS |
| Fanout to multiple consumers | SNS → SQS |
| Routing structured events | EventBridge |
| High-throughput streaming, log-like | Kinesis or MSK |
| Ordered processing | SQS FIFO or Kafka (MSK) |
| Cross-account fanout | SNS or EventBridge |
| Real-time analytics | Kinesis Data Analytics |
| Logs/clickstream to S3 | Firehose |

## Interview Themes

- "Compare SQS, SNS, EventBridge"
- "Walk through SQS DLQ and visibility timeout"
- "Kinesis shard sizing for X events/sec"
- "Design fanout: 1 event → 5 services"
- "MSK vs Kinesis — when each?"
