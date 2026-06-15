# L08/C10/T01 — SQS (Standard, FIFO, DLQ)

## Learning Objectives

- Use SQS for decoupling
- Handle DLQ

## SQS

Managed message queue. Producers send; consumers poll.

## Standard vs FIFO

| | Standard | FIFO |
|---|---|---|
| Order | Best-effort | Strict (per MessageGroupId) |
| Delivery | At-least-once | Exactly-once within the 5-min dedup window |
| Throughput | Unlimited | 300 msg/sec (3000 with batching) |
| Cost | $0.40/M | $0.50/M |

For high-throughput: Standard.
For order / exactly-once: FIFO.

## Standard

```bash
aws sqs create-queue --queue-name myQ
aws sqs send-message --queue-url ... --message-body "hello"
aws sqs receive-message --queue-url ... --max-number-of-messages 10 --wait-time-seconds 20
aws sqs delete-message --queue-url ... --receipt-handle ...
```

## FIFO

```bash
aws sqs create-queue --queue-name myQ.fifo --attributes FifoQueue=true,ContentBasedDeduplication=true
aws sqs send-message --queue-url ... --message-body "..." --message-group-id user-123
```

Required:
- `MessageGroupId`: ordering scope
- `MessageDeduplicationId`: dedup token (or ContentBasedDeduplication)

## Visibility Timeout

After receive, message hidden N seconds. If processed: delete. If not: returns to queue.

Default 30s; set per queue or per receive.

Set > max processing time. Else duplicates.

```bash
aws sqs change-message-visibility --queue-url ... --receipt-handle ... --visibility-timeout 60
```

Extend if processing slower.

## Long Polling

```bash
aws sqs receive-message --wait-time-seconds 20
```

Waits up to 20s for message. Reduces empty polls (cost).

Default 0 (short poll). Always set 20.

## Message Retention

Default 4 days. Configurable 1 min - 14 days:
```bash
aws sqs set-queue-attributes --queue-url ... --attributes MessageRetentionPeriod=1209600   # 14 days
```

After retention: dropped silently. Plan consumer keeping up.

## Delay Queues

Delay delivery N seconds (0-15 min):
```bash
aws sqs send-message --queue-url ... --delay-seconds 60 --message-body "..."
```

Per message or per queue default.

For: scheduled work, retries with backoff.

For >15 min delay: Step Functions Wait state or EventBridge schedule.

## Batching

Send/receive up to 10 messages per API call.

Throughput + cost benefit.

```bash
aws sqs send-message-batch --queue-url ... --entries ...
```

## Dead Letter Queue (DLQ)

After max receives, message moves to DLQ:
```yaml
RedrivePolicy:
  deadLetterTargetArn: arn:aws:sqs:...:myQ-dlq
  maxReceiveCount: 3
```

Inspect DLQ for failed:
- Bad message format
- Bug in consumer
- Downstream service down

Re-drive (move back to main queue) after fix:
```bash
aws sqs start-message-move-task --source-arn arn:dlq ...
```

## Message Size

Max 256 KB per message.

For larger:
- Store in S3; send pointer in SQS
- Or use Kinesis (1 MB per record)

Extended client library handles automatically.

## At-Least-Once Delivery

Standard: possible duplicates. Consumer MUST be idempotent.

FIFO: exactly-once (with dedup ID). 5-min dedup window.

## Order

Standard: best-effort; mostly in order but no guarantee.

FIFO: strict per MessageGroupId.
- Same MessageGroupId → ordered
- Different MessageGroupId → independent, parallel

Plan: granular MessageGroupId for parallelism (e.g., per user).

## Consumer Patterns

### Lambda Trigger
```bash
aws lambda create-event-source-mapping --function-name myFn --event-source-arn arn:sqs:...
```

Lambda polls SQS; processes batches. Concurrency scales.

Returns errors → message returned to queue → eventual DLQ.

### EC2 / ECS Worker
```python
while True:
    msgs = sqs.receive_message(WaitTimeSeconds=20, MaxNumberOfMessages=10)
    for msg in msgs.get("Messages", []):
        try:
            process(msg)
            sqs.delete_message(ReceiptHandle=msg["ReceiptHandle"])
        except Exception:
            # Will retry after visibility timeout
            pass
```

### Long-Running
Use ChangeMessageVisibility heartbeat:
```python
while processing:
    sqs.change_message_visibility(...)
    time.sleep(half_visibility_timeout)
```

## Scaling

For load spike:
- More Lambda concurrency
- More EC2 / ECS workers
- Auto-scale on `ApproximateNumberOfMessagesVisible`

## Encryption

SSE-SQS (default 2023): AWS-managed.
SSE-KMS: customer-managed.

In transit: HTTPS.

## VPC Endpoint

SQS interface endpoint for private VPC access.

## Permissions

Queue policy (resource-based) + IAM (identity-based).

Cross-account: queue policy allows other account's role.

## Patterns

### Web → Worker
```
ALB → API → SQS → Worker
```

API enqueues; returns 200 fast; worker processes async.

### Fan-Out
```
SNS → SQS A
   → SQS B
   → SQS C
```

Each SQS = different consumer pipeline.

### Pipeline
```
SQS A → Lambda 1 → SQS B → Lambda 2 → SQS C → ...
```

Each stage decoupled.

### Buffer
Spike absorption. Producer fast; consumer at own rate.

## Monitoring

CloudWatch:
- ApproximateNumberOfMessagesVisible (queue depth)
- ApproximateNumberOfMessagesNotVisible (in-flight)
- ApproximateAgeOfOldestMessage (lag)
- NumberOfMessagesSent / Received

Alert on:
- Depth growing (consumer not keeping up)
- Age old (stuck messages)
- DLQ depth > 0

## Cost

- $0.40 per million (Standard)
- $0.50 per million (FIFO)
- Free first 1M / month

For 1B/month: ~$400. Cheap relative to processing.

## Common Mistakes

- Same MessageGroupId for all (defeats FIFO parallelism)
- Not idempotent consumer
- No DLQ
- Long-poll 0 (cost / latency)
- Visibility timeout too short (duplicates)

## Best Practices

- Long-poll 20s
- Idempotent consumer
- DLQ + alert
- Visibility timeout > max processing
- Monitor depth + age
- Encryption
- Batch sends/receives
- Backoff on transient failures

## Cost Optimization

- Long polling (fewer empty receives)
- Batch (up to 10 per API)
- Shorter retention (if dropping OK)
- Standard over FIFO when possible

## Idempotency

Consumer side:
```python
def process(msg):
    msg_id = msg["MessageId"]
    if already_processed(msg_id):
        return
    do_work(msg)
    mark_processed(msg_id)
```

Track processed IDs (DynamoDB with TTL).

## Throughput Limits

Standard: virtually unlimited.

FIFO:
- 300 TPS without batching
- 3000 TPS with batching
- High-throughput FIFO: 70,000 TPS in some regions

## Quick Refs

```bash
# Create
aws sqs create-queue --queue-name myQ --attributes VisibilityTimeout=30,MessageRetentionPeriod=1209600

# Send
aws sqs send-message --queue-url ... --message-body "..."

# Receive (long poll)
aws sqs receive-message --queue-url ... --wait-time-seconds 20

# DLQ config
aws sqs set-queue-attributes --queue-url ... --attributes RedrivePolicy='{"deadLetterTargetArn":"arn:dlq","maxReceiveCount":3}'
```

## Interview Prep

**Junior**: "Why use SQS."

**Mid**: "Standard vs FIFO."

**Senior**: "Idempotent consumer pattern."

**Staff**: "Design async pipeline at 1M msg/sec."

## Next Topic

→ [T02 — SNS & Fanout Patterns](T02-SNS-Fanout.md)
