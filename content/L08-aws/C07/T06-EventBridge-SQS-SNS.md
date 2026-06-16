# L08/C07/T06 — EventBridge, SQS, SNS (Overview)

## Learning Objectives

- Distinguish three messaging services
- Pick for use case

## Three Pillars

| | Type | Pattern |
|---|---|---|
| SQS | Queue | Point-to-point; pull |
| SNS | Pub/Sub | Fan-out; push |
| EventBridge | Event bus | Routing on rules; push |

## SQS

Managed message queue. Decouple producer from consumer.

```bash
aws sqs create-queue --queue-name myQ
aws sqs send-message --queue-url ... --message-body "..."
aws sqs receive-message --queue-url ...
aws sqs delete-message --queue-url ... --receipt-handle ...
```

Producer sends; consumer polls (long poll typically).

### Standard
- High throughput
- At-least-once
- Best-effort ordering

### FIFO
- Strict ordering (per MessageGroupId)
- Exactly-once within the 5-min dedup window (deduplication ID)
- 300 msg/sec / 3000 with batching

### Visibility Timeout
After receive, message invisible for N seconds.
- If processed: delete
- If not deleted: returns to queue (retry)

Set timeout > max processing time.

### DLQ
Failed messages (max receives exceeded) move to DLQ for inspection.

### Use Cases
- Worker queues (web → SQS → workers)
- Async processing
- Decouple
- Load leveling

(Deep dive in L08/C10/T01.)

## SNS

Publish-Subscribe. Topic; subscribers receive each message.

```bash
aws sns create-topic --name myTopic
aws sns subscribe --topic-arn ... --protocol email --notification-endpoint me@example.com
aws sns publish --topic-arn ... --message "..."
```

### Subscribers
- Email
- SMS
- HTTP / HTTPS endpoint
- Lambda
- SQS queue
- Mobile push
- Kinesis Data Firehose

### Use Cases
- Fan-out (one event → many consumers)
- Alerts (CloudWatch alarms → SNS → email/Slack)
- Mobile push notifications
- Cross-account events

### Pattern: SNS → SQS Fan-Out
```
Publisher → SNS → multiple SQS queues → multiple consumers
```

Each consumer has own queue; processes at own rate; no consumer affects others.

### FIFO SNS
Strict ordering; pair with FIFO SQS.

## EventBridge

Event bus with rules; routes events to targets.

Concepts:
- Event bus (default + custom)
- Rule: pattern matches event → route to target
- Target: SQS, Lambda, Step Functions, Kinesis, etc.

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {"bucket": {"name": ["my-bucket"]}}
}
```

Matched → invoke target.

### Event Bus Types
- Default bus: AWS service events
- Custom bus: your events
- Partner bus: SaaS partners (Datadog, MongoDB, Auth0)

### Use Cases
- Decouple via events
- SaaS integration (Stripe → EventBridge → your app)
- Multi-target routing
- Schedule (replaces CloudWatch Events)
- Replay (archive + replay events)

### Schedule
```bash
aws scheduler create-schedule --name daily-job --schedule-expression "rate(1 day)" --target ...
```

Replaces cron-style CloudWatch Events.

## Comparison

| | SQS | SNS | EventBridge |
|---|---|---|---|
| Pattern | Queue | Pub/Sub | Event bus |
| Throughput | Very high | Very high | Lower |
| Filtering | DLQ only | Subscription filter | Rich JSON match |
| Targets | Consumers poll | Many subscriber types | Many AWS + SaaS |
| Ordering | Yes (FIFO) | No (FIFO has ordering) | No |
| Replay | No (use Kinesis) | No | Yes (archive + replay) |
| Schema | App-defined | App-defined | Schema registry |
| Cost | $0.40/M | $0.50/M | $1/M (default), $1/M (custom) |

## When SQS

- Decouple worker from request
- Buffer (spike absorption)
- Multiple consumers per queue (one wins)
- Strict ordering (FIFO)
- Retries needed

## When SNS

- Fan-out: one event → many subscribers
- Real-time push (email, SMS, mobile)
- Don't care if any subscriber down
- Simple

## When EventBridge

- Rich filtering / routing
- Many sources (AWS + custom + SaaS)
- Targets per rule
- Replay / archive
- Schema registry
- Schedule

## Common Patterns

### Web → Async Processing
```
ALB → API → SQS → Worker
```

API enqueues; returns 200 fast; worker processes async.

### Fan-Out
```
Order created → SNS → SQS-A (billing)
                    → SQS-B (analytics)
                    → SQS-C (inventory)
                    → Lambda (notify)
```

### Event-Driven Architecture
```
Service A → EventBridge → Service B
                       → Service C
```

Services decoupled via events.

### Saga / Choreography
```
Order → events
  → InventoryReserved event → Charge service
    → Charged event → Ship service
      → Shipped event → Notify
```

Each service consumes events from others.

## EventBridge Pipes

Connect source to target with filtering / enrichment:
```
SQS → Pipe (filter/transform) → EventBridge bus
```

No Lambda needed for simple routing.

## Schema Registry (EventBridge)

Define event schemas; auto-discover from events; codegen client.

For: typed events; team coordination.

## Pricing

For 1M events/month:
- SQS: $0.40
- SNS: $0.50
- EventBridge custom: $1.00
- EventBridge default (AWS events): free
- Schedule: free

For 100M:
- SQS: $40
- SNS: $50
- EventBridge: $100

Latency:
- SQS: ms
- SNS: 100s of ms
- EventBridge: 100s of ms - few sec

## Combined Architectures

```
Stripe → SaaS partner bus → EventBridge → Lambda (process)
                                       → SQS → Worker (audit)
                                       → S3 (archive)
```

EventBridge as central; SQS for buffering; SNS for SMS.

## DLQ

All three support DLQ:
- SQS: queue redrive
- SNS: failed deliveries → DLQ
- EventBridge: failed invocation → DLQ

Investigate; redrive.

## Best Practices

- Use right tool (SQS / SNS / EB)
- DLQ everywhere
- Schema discipline (especially EB)
- Idempotent consumers
- Monitor: queue depth, errors

## Common Mistakes

- SQS when fan-out needed
- SNS without subscribers' DLQ
- EventBridge for high-throughput (use SQS / Kinesis)
- Forgetting visibility timeout
- No DLQ

## Quick Refs

```bash
# SQS
aws sqs send-message --queue-url ... --message-body "..."

# SNS
aws sns publish --topic-arn ... --message "..."

# EventBridge
aws events put-events --entries 'Source=my.app,DetailType=OrderCreated,Detail="{\"id\":1}"'
```

## Interview Prep

**Mid**: "SQS vs SNS."

**Senior**: "Pick messaging for X."

**Staff**: "Event-driven architecture design."

## Next Topic

→ [T07 — API Gateway (REST, HTTP, WebSocket)](T07-API-Gateway.md)
