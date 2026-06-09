# L08/C10/T04 — Kinesis Data Streams, Firehose, Analytics

## Learning Objectives

- Use Kinesis for streaming
- Pick variant

## Kinesis Family

| | Use |
|---|---|
| Data Streams | Ordered shard-based stream; sub-second |
| Firehose | Delivery to S3 / Redshift / OpenSearch / Splunk |
| Data Analytics | SQL on streams (legacy, superseded) |
| Video Streams | Video ingestion / playback |

## Data Streams

Like Kafka. Shards; producers send; consumers read.

```bash
aws kinesis create-stream --stream-name myStream --shard-count 4
```

## Records

```json
{
  "PartitionKey": "user-123",
  "Data": "base64-encoded-payload",
  "SequenceNumber": "..."
}
```

PartitionKey: hash → shard.
SequenceNumber: order within shard.

## Shards

Unit of capacity:
- 1 MB/sec write OR 1000 records/sec
- 2 MB/sec read (per consumer; up to 5 consumers)

For 10 MB/sec needed: 10 shards.

## Producer

```python
import boto3
client = boto3.client("kinesis")
client.put_record(StreamName="myStream", PartitionKey="user-123", Data=b"...")

# Batch
client.put_records(StreamName="myStream", Records=[
  {"PartitionKey": "user-123", "Data": b"..."},
  {"PartitionKey": "user-456", "Data": b"..."}
])
```

## Consumer

### Shared Throughput
Up to 5 consumers; each gets full 2 MB/sec; shared.

### Enhanced Fan-Out
20 consumers; each gets 2 MB/sec dedicated.
Cost: per consumer-shard hour + data.

For: many independent processors.

## Kinesis Client Library (KCL)

Library for stateful consumers:
- Manages shard assignments across workers
- Checkpoints in DynamoDB
- Handles shard splits/merges

For Java, Python (KPL/KCL).

## Lambda Consumer

```bash
aws lambda create-event-source-mapping --function-name myFn --event-source-arn arn:kinesis:...
```

Lambda polls; processes batches per shard.

Concurrency = shards × parallelization factor.

## Retention

Default 24 hours; up to 365 days (extra cost).

For replay / reprocessing: longer retention.

## Ordering

Per shard: ordered by SequenceNumber.
Across shards: not.

PartitionKey determines shard; same key = same shard = ordered.

## On-Demand vs Provisioned

Provisioned: fixed shards; you manage.
On-Demand: auto-scale; pay per GB written/read.

For: variable workloads, on-demand. Predictable: provisioned.

## Firehose

Managed delivery from stream to destination:
- S3
- Redshift
- OpenSearch
- Splunk
- HTTP endpoint
- Datadog, New Relic, etc.

Buffers + delivers in batches. No consumer to manage.

```bash
aws firehose create-delivery-stream --delivery-stream-name myFirehose --s3-destination-configuration ...
```

## Firehose Features

- Buffer (size + time-based)
- Compression (gzip)
- Conversion (JSON → Parquet)
- Partitioning (date-based S3 prefix)
- Lambda transform (per record)
- Encryption

## Firehose Pricing

$0.029/GB ingested. No shard concept.

Cheaper than Data Streams + custom consumer for delivery use.

## Firehose vs Data Streams

| | Firehose | Data Streams |
|---|---|---|
| Setup | Easier | Manual |
| Latency | ~60s (buffered) | Sub-second |
| Use | ETL to storage | Real-time processing |
| Cost | Per GB | Per shard |
| Custom consumer | No | Yes |

For delivery: Firehose.
For real-time: Data Streams + Lambda / Spark.

## Patterns

### Log Pipeline
```
App → Firehose → S3 (Parquet) → Athena/Redshift
```

Cheap; scalable.

### Real-Time Analytics
```
App → Data Streams → Lambda → DynamoDB / Cache
```

Live updates.

### Clickstream
```
Web → API → Data Streams → KCL workers → process
```

### Multi-Destination
```
Data Streams → Firehose → S3 (archive)
            → Lambda → real-time alerts
            → OpenSearch (search index)
```

## Kafka vs Kinesis

| | Kinesis | Kafka (MSK) |
|---|---|---|
| Managed | Yes | Yes (MSK) or self |
| Ordering | Per shard | Per partition |
| Latency | Sub-second | Sub-millisecond |
| Throughput | Shards × 1 MB/s | High (configurable) |
| Cost | Per shard | Per broker |
| Ecosystem | AWS | Open source |

Kafka: more standard; portable.
Kinesis: AWS-native; tightly integrated.

For AWS-only: Kinesis.
For multi-cloud / lots of Kafka tools: MSK.

## Resharding

Increase capacity: split shards.
Decrease: merge shards.

Done online; no downtime. Existing data on old shards retained until expiration.

## Costs

Data Streams:
- $0.015 per shard-hour ($11/mo)
- $0.014 per million records (PUT)
- Enhanced Fan-Out: more

For 4 shards 24/7: ~$44/mo + records.

Firehose:
- $0.029 per GB
- Lambda processing extra
- Conversion (Parquet) extra

## Monitoring

CloudWatch:
- IncomingBytes / IncomingRecords
- IteratorAgeMilliseconds (consumer lag)
- WriteProvisionedThroughputExceeded
- ReadProvisionedThroughputExceeded

Alert on:
- High iterator age (consumer behind)
- Throughput exceeded (need more shards)

## Common Mistakes

- Hot partition key (one shard hammered)
- No checkpointing (replay from beginning)
- Too few shards (throttled)
- Too many shards (overpaying)
- Firehose with sub-second expectation

## Best Practices

- Partition key with high cardinality
- KCL for stateful processing
- Monitor iterator age
- Right shard count (resize as needed)
- Firehose for delivery
- Compression / Parquet for S3

## Patterns to Avoid

### Single Partition Key for All
All to one shard; bottlenecked.

### No Backpressure
Producer faster than consumer → records expire → data loss.

Monitor IteratorAge.

## When NOT Kinesis

- Simple queue: SQS
- Pub/sub fanout: SNS / EventBridge
- File ingestion to S3 only: Firehose (cheaper)
- Sub-millisecond: MSK

## Data Streams + Step Functions

For complex per-record processing: Step Functions invoked per record. Express SF for short.

## Schema Validation

No built-in. Use Schema Registry (Glue) or app-level.

## Encryption

KMS at rest. TLS in transit.

## VPC Endpoint

Interface endpoint for private VPC access.

## Quick Refs

```bash
# Create stream
aws kinesis create-stream --stream-name myStream --shard-count 4

# Put record
aws kinesis put-record --stream-name myStream --partition-key user-123 --data "..."

# Firehose
aws firehose create-delivery-stream --delivery-stream-name myFirehose --s3-destination-configuration ...

# Resharding
aws kinesis update-shard-count --stream-name myStream --target-shard-count 8 --scaling-type UNIFORM_SCALING
```

## Interview Prep

**Mid**: "Kinesis vs SQS."

**Senior**: "Streaming pipeline architecture."

**Staff**: "Kafka vs Kinesis tradeoffs."

## Next Topic

→ [T05 — MSK (Managed Kafka)](T05-MSK.md)
