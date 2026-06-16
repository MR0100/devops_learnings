# L08/C05/T07 — S3 Event Notifications & Triggers

## Learning Objectives

- Wire S3 events to processing
- Build event-driven flows

## S3 Events

S3 emits events on operations:
- `s3:ObjectCreated:*` (Put, Post, Copy, CompleteMultipartUpload)
- `s3:ObjectRemoved:*` (Delete, Delete marker)
- `s3:ObjectRestore:*` (Glacier restore complete)
- `s3:ObjectAcl:Put`
- `s3:ObjectTagging:*`
- `s3:Replication:*`

Many sub-events. Most common: ObjectCreated.

## Destinations

Three:
- SNS (topic)
- SQS (queue)
- Lambda (function)
- EventBridge (newer; richer)

## Configure

```bash
aws s3api put-bucket-notification-configuration --bucket b --notification-configuration '{
  "LambdaFunctionConfigurations": [{
    "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123:function:Process",
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {
      "Key": {
        "FilterRules": [
          {"Name": "Prefix", "Value": "uploads/"},
          {"Name": "Suffix", "Value": ".jpg"}
        ]
      }
    }
  }]
}'
```

Auto-creates resource policy on Lambda allowing S3 invoke.

## Use Cases

### Process Uploads
User uploads image → Lambda resizes → store thumbs.

### ETL
Data file lands → Lambda processes → loads to DB.

### Replicate
File created → SQS → consumer replicates to other system.

### Audit
Sensitive bucket → Lambda → log to SIEM.

### Triggering Pipelines
Code uploaded → Lambda → trigger Step Function.

## SQS Pattern

For high-volume / decoupled:
```
S3 → SQS → Workers (Lambda, ECS, EC2)
```

Workers pull from SQS; process at own pace; ack on success.

Benefits:
- Buffer (S3 can produce faster than consumer)
- Multiple consumers
- Retry on failure
- Dead letter queue

## SNS Pattern

Fan-out:
```
S3 → SNS → multiple subscribers
       ├── Lambda 1
       ├── SQS 1
       └── HTTP endpoint
```

One event → many consumers.

## Lambda Pattern

Direct processing:
```
S3 → Lambda
```

For small workloads. Direct; no buffer; concurrency limited by Lambda.

## EventBridge Pattern

Newer; richer:
- Event bus
- Pattern matching (JSON rules)
- Many targets
- Archive + replay
- Schema registry

```bash
aws s3api put-bucket-notification-configuration --bucket b --notification-configuration '{
  "EventBridgeConfiguration": {}
}'
```

S3 events go to default event bus. Rules route:
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {"name": ["b"]},
    "object": {"key": [{"prefix": "uploads/"}]}
  }
}
```

EventBridge → many targets.

## Filtering

S3 native filter:
- Prefix
- Suffix

EventBridge: rich JSON pattern (key prefix, size, tags, etc.).

For complex filtering: EventBridge.

## Delivery Guarantees

At-least-once. Possible duplicate delivery.

Consumer MUST be idempotent.

S3 events emitted asynchronously; can be delayed under load.

## Latency

Typical: <1 sec from S3 PUT to event delivery.

Spikes: occasional minutes.

## Limits

- 100 notifications per bucket configuration
- Each rule: one destination

For many: use SNS fan-out.

## Event Payload

```json
{
  "Records": [{
    "eventSource": "aws:s3",
    "eventName": "ObjectCreated:Put",
    "s3": {
      "bucket": {"name": "b"},
      "object": {
        "key": "uploads/file.jpg",
        "size": 12345,
        "eTag": "abc..."
      }
    }
  }]
}
```

Lambda reads `event["Records"]`; SQS message wraps in body; SNS wraps in Message.

## Multiple Events per Notification

S3 can batch multiple Records per Lambda invocation (rare; usually 1).

Process loop; idempotent.

## Common Patterns

### Image Resize
```
User uploads to bucket/uploads/
→ S3 event → Lambda → 
  - Read image
  - Resize 3 sizes
  - Write to bucket/processed/<id>/sm/, md/, lg/
```

### Log Processing
```
App writes log to S3
→ Event → Lambda →
  - Parse log
  - Extract metrics
  - Write to CloudWatch
```

### Document Indexing
```
PDF uploaded
→ Event → Lambda
  - Extract text
  - Index in Elasticsearch
  - Notify search service
```

## DLQ for Failed Lambda

Configure DLQ for Lambda invoked via S3:
- Failed events go to SQS / SNS DLQ
- Manual investigation
- Re-drive after fix

S3 retries Lambda invocation (2 retries for async); then DLQ.

## SQS for High Volume

When S3 generates >Lambda concurrency:
```
S3 → SQS → Lambda (concurrency-controlled)
```

SQS buffers; Lambda processes at own rate.

Or Lambda direct with reserved concurrency to limit blast radius.

## Avoid Recursive Loops

```
Lambda triggered by S3
  ↓
Lambda writes back to same bucket prefix
  ↓
Trigger again!
```

Mitigate:
- Different prefix for input/output
- Skip if name matches output pattern
- Conditional check

## EventBridge vs Native

For new: EventBridge.
- Richer routing
- Archive + replay
- Schema registry
- Cross-account events
- Better debugging

Native (Lambda/SQS/SNS direct): simpler; legacy.

## Cross-Region

Native: same region.
EventBridge: can route cross-region (event bus copies).

## Logging Events

```
S3 → EventBridge → CloudWatch Logs (for audit)
                → Lambda (for processing)
                → SQS (for downstream)
```

Multiple targets per pattern.

## Cost

S3 event itself: free.
- Lambda: per invocation + duration
- SQS: $0.40 per million
- SNS: $0.50 per million
- EventBridge: $1 per million

For 1M files/day:
- Direct Lambda: ~$0.20 lambda + ~$20 events
- EventBridge: ~$30
- SQS-based: ~$5

## When NOT Events

If you can write to DB directly: simpler than event-loop.

For complex multi-step: Step Functions (state machine) > chained events.

## Test

```bash
# Simulate event via CLI
aws lambda invoke --function-name myFn --payload file://event.json out.json
```

Sample event from S3 docs.

## Common Mistakes

- Lambda not idempotent → duplicate processing
- No DLQ
- Recursive loop
- Slow Lambda (S3 events queue up)
- No filter (process all when only specific)
- Same bucket for input/output without conditional

## Best Practices

- Idempotency via event ID or object key
- DLQ for failed
- Filter to reduce noise
- EventBridge for complex routing
- Separate input/output buckets/prefixes
- Monitor Lambda errors

## Replay

EventBridge archive: replay events later. Useful if Lambda was broken:
- Fix Lambda
- Replay archive into rule
- Reprocess missed events

## Other Triggers

- S3 Batch Operations: apply Lambda to many existing objects (not just new)
- S3 Inventory + Athena → trigger processing on subset

## Quick Refs

```bash
# Native notification
aws s3api put-bucket-notification-configuration --bucket b --notification-configuration file://config.json

# EventBridge enable
aws s3api put-bucket-notification-configuration --bucket b --notification-configuration '{"EventBridgeConfiguration": {}}'

# Add Lambda invoke permission for S3
aws lambda add-permission --function-name myFn --statement-id s3-invoke --principal s3.amazonaws.com --action lambda:InvokeFunction --source-arn arn:aws:s3:::b
```

## Interview Prep

**Mid**: "S3 → Lambda pattern."

**Senior**: "S3 events for ETL."

**Staff**: "Event-driven architecture on S3."

## Next Topic

→ [T08 — EFS & FSx (File Storage)](T08-EFS-FSx.md)
