# L08/C10/T02 — SNS & Fanout Patterns

## Learning Objectives

- Use SNS for fan-out
- Apply patterns

## SNS

Publish-Subscribe. Topic; subscribers receive each message.

```bash
aws sns create-topic --name myTopic
aws sns subscribe --topic-arn ... --protocol email --notification-endpoint me@example.com
aws sns publish --topic-arn ... --message "hello"
```

## Subscribers

- Email / SMS
- HTTP / HTTPS endpoint
- Lambda
- SQS
- Mobile push (APNS, FCM)
- Kinesis Data Firehose
- AWS services (CodePipeline notifications etc.)

## Fan-Out Pattern

```
Publisher → SNS Topic → SQS A → Consumer A
                     → SQS B → Consumer B
                     → SQS C → Consumer C
                     → Lambda
                     → HTTP webhook
```

One publish; many subscribers each get copy.

Pros:
- Decouple producer from subscribers
- Add subscribers without touching producer
- Each subscriber has own queue (own pace, retries)

## Subscription Filter

Filter messages per subscriber:
```json
{
  "event_type": ["order.created", "order.updated"]
}
```

Subscriber gets only matching.

Without filter: subscriber gets all topic messages; filters in app.

With filter: SNS filters; subscriber receives only relevant. Saves cost.

## Message Attributes

```bash
aws sns publish --topic-arn ... --message "..." --message-attributes '{
  "event_type": {"DataType": "String", "StringValue": "order.created"}
}'
```

Filters match attributes.

## FIFO SNS

```bash
aws sns create-topic --name myTopic.fifo --attributes FifoTopic=true
```

Strict ordering with MessageGroupId. Pair with FIFO SQS.

## Retries

Per subscriber type:
- HTTP/HTTPS: retried (custom policy)
- Lambda: retried (Lambda's retry policy)
- SQS: queued (subscriber handles retries from SQS)
- Email/SMS: best-effort

For HTTP: configure delivery policy with backoff.

## DLQ

Failed deliveries to DLQ:
```bash
aws sns set-subscription-attributes --subscription-arn ... --attribute-name RedrivePolicy --attribute-value '{"deadLetterTargetArn":"arn:sqs:..."}'
```

For investigation / replay.

## Cross-Account / Cross-Region

Cross-account: SNS topic policy allows another account to subscribe.

Cross-region: subscribe to topic from another region (SNS supports).

## Email / SMS

Direct end-user delivery:
- Email: requires double opt-in (confirmation)
- SMS: per-message cost; per-country pricing varies

For transactional / alerts.

For marketing: better use SES (Email) or Pinpoint (SMS / mobile).

## Mobile Push

- APNS (Apple)
- FCM (Google / Android)
- ADM (Amazon Fire)
- MPNS / WNS (Windows)

Per-platform endpoint per device. SNS sends to all platforms.

## Patterns

### Event Notification
```
Order created → SNS → all interested services
```

### Topic per Event Type
```
- orders-topic
- payments-topic
- shipments-topic
```

vs single topic with filtered subscriptions.

### SaaS Multi-Tenant
- Tenant-prefixed topics
- Or one topic; tenantId attribute; filtered subscriptions

### Alerting
```
CloudWatch Alarm → SNS → Email + Slack + PagerDuty
```

Multiple alerting endpoints from one alarm.

## Comparison

| | SNS | SQS | EventBridge |
|---|---|---|---|
| Pattern | Pub/Sub | Queue | Event bus |
| Push to consumer | Yes | Pull | Push |
| Filter | Per-subscription | No (DLQ only) | Rich JSON |
| Ordering | FIFO option | FIFO option | No |
| Throughput | High | Very high | Lower |
| Cost (1M) | $0.50 | $0.40 | $1.00 |

## When SNS

- Fan-out
- Push to many subscribers
- Real-time
- Simple filtering

## When EventBridge

- Rich routing
- AWS service integration
- SaaS partner events
- Schema registry

## When SQS

- Buffered queue
- Strict ordering (FIFO)
- Single consumer pool
- Retries / DLQ at consumer

## Cost

- $0.50 per million publishes
- $0.06 per 100k SMS (US)
- $0.085 per 100k Mobile Push
- $0.50 per 100k Email (after free tier)

For 10M API publishes/mo with SQS subscribers: $5.

## SNS Standard vs FIFO

Standard: at-least-once; possibly out-of-order.
FIFO: strict order; exactly-once within the 5-min dedup window.

## Best Practices

- DLQ for HTTP subscribers
- Filter policies (reduce subscriber work)
- Message attributes for routing
- Encryption (SSE-KMS)
- Cross-account topic policies tight
- Monitor delivery failures

## Common Mistakes

- No DLQ (failures lost)
- Wide subscription (consumer gets all; ignored)
- No retry on transient HTTP failures
- Sending sensitive data unencrypted

## Monitoring

CloudWatch:
- NumberOfMessagesPublished
- NumberOfNotificationsDelivered
- NumberOfNotificationsFailed
- PublishSize

Alert on failures.

## SNS as Schema-less Pub/Sub

Like EventBridge but without schema enforcement. For new: prefer EventBridge for richer features.

SNS still useful for:
- Direct user notifications (email, SMS, push)
- Existing apps
- Simple fan-out

## Two-Phase Validation

For HTTP/HTTPS subscriber: SNS sends confirmation; endpoint must reply 200 with token.

Prevents subscribing arbitrary endpoints.

## Cross-Region Fan-Out

```
Publish in region A → SNS → SQS A (us-east-1)
                           → SQS B (us-west-2)
                           → SQS C (eu-west-1)
```

Each region processes locally.

## Quick Refs

```bash
# Topic
aws sns create-topic --name myTopic

# Subscribe
aws sns subscribe --topic-arn ... --protocol sqs --notification-endpoint arn:sqs:...

# Publish
aws sns publish --topic-arn ... --message "..." --message-attributes ...

# Set DLQ
aws sns set-subscription-attributes --subscription-arn ... --attribute-name RedrivePolicy --attribute-value '{"deadLetterTargetArn":"..."}'
```

## Interview Prep

**Mid**: "SNS fan-out — design."

**Senior**: "SNS vs EventBridge."

**Staff**: "Multi-region pub/sub at scale."

## Next Topic

→ [T03 — EventBridge (Buses, Rules, Schemas)](T03-EventBridge.md)
