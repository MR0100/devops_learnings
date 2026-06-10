# L22/C06/T01 — AWS SQS, SNS, Kinesis, MSK

## Learning Objectives

- Choose AWS messaging
- Operate each

## SQS

Simple Queue Service:
- Managed queue
- At-least-once
- Standard or FIFO

```python
sqs.send_message(QueueUrl=url, MessageBody='...')
sqs.receive_message(QueueUrl=url)
sqs.delete_message(QueueUrl=url, ReceiptHandle=h)
```

## SQS Standard

- High throughput
- Best-effort order
- At-least-once (dupes possible)

## SQS FIFO

- Strict order per group
- Exactly-once (with dedupe)
- Lower throughput (3000 msg/sec)

```bash
aws sqs create-queue --queue-name X.fifo \
  --attributes FifoQueue=true,ContentBasedDeduplication=true
```

## SNS

Simple Notification Service:
- Pub/sub
- Fanout
- Subscribers: SQS, Lambda, HTTP, email, SMS

```python
sns.publish(TopicArn=arn, Message='...')
```

## SNS + SQS Fanout

```
SNS topic
├─ SQS queue A
├─ SQS queue B
└─ Lambda
```

Standard pattern.

## Kinesis Data Streams

Kafka-like:
- Shards (like partitions)
- 1 MB/s per shard write
- 2 MB/s per shard read
- 7-day retention

```python
kinesis.put_record(StreamName='X', Data=b'...', PartitionKey='k')
```

## Kinesis vs Kafka

| | Kinesis | Kafka |
|---|---|---|
| Managed | yes | no (or MSK) |
| Throughput | per shard | per partition |
| Retention | up to 365 days | configurable |
| Cost | per shard hour | infra |

## MSK

Managed Kafka:
- AWS-operated brokers
- VPC integration
- IAM auth
- Less ops

For: Kafka without operating.

## MSK Serverless

Auto-scale:
- No capacity to plan
- Pay per usage

## EventBridge

Event bus:
- Schema discovery
- Filtering rules
- SaaS event sources

For: cross-account events.

## Choosing

```
Queue: SQS (Standard for throughput; FIFO for order)
Pub/Sub: SNS
Stream: Kinesis or MSK
Event router: EventBridge
```

## Cost

- SQS: $0.40 / million
- SNS: similar
- Kinesis: per shard hour + per write
- MSK: per broker hour

## Lambda Integration

SQS triggers Lambda. Built-in.

For: serverless workers.

## Dead Letter Queue

```bash
aws sqs create-queue --queue-name dlq
aws sqs set-queue-attributes --queue-url main \
  --attributes RedrivePolicy='{"deadLetterTargetArn":"...","maxReceiveCount":"5"}'
```

After 5 failures: to DLQ.

## Best Practices

- DLQ for failures
- FIFO if order critical
- SNS+SQS for fanout
- IAM least-priv
- Encrypt with KMS

## Common Mistakes

- Standard when FIFO needed
- No DLQ
- Long visibility timeout (delays retries)
- No metrics

## Quick Refs

```python
sqs.send_message / receive_message / delete_message
sns.publish / subscribe
kinesis.put_record / get_records
```

```bash
aws sqs / sns / kinesis / msk
```

## Interview Prep

**Mid**: "AWS messaging."

**Senior**: "SNS+SQS pattern."

**Staff**: "Messaging architecture AWS."

## Next Topic

→ [T02 — GCP Pub/Sub](T02-GCP-PubSub.md)
