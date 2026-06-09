# L08/C10/T03 — EventBridge (Buses, Rules, Schemas)

## Learning Objectives

- Build event-driven architecture
- Use EventBridge features

## EventBridge

Event bus with rule-based routing. Decouple services via events.

## Buses

- **Default bus**: AWS service events (S3, EC2, RDS, etc.)
- **Custom bus**: your events
- **Partner bus**: SaaS partners (Datadog, Auth0, MongoDB, Stripe, ...)

```bash
aws events create-event-bus --name my-app-bus
```

## Events

JSON:
```json
{
  "version": "0",
  "id": "abc-123",
  "detail-type": "Order Created",
  "source": "my.app",
  "account": "123",
  "time": "2026-06-09T10:00:00Z",
  "region": "us-east-1",
  "detail": {
    "order_id": "1",
    "amount": 100
  }
}
```

## Publish

```bash
aws events put-events --entries '[{
  "Source": "my.app",
  "DetailType": "Order Created",
  "Detail": "{\"order_id\":\"1\"}"
}]'
```

## Rules

Match events; route to targets:
```json
{
  "source": ["my.app"],
  "detail-type": ["Order Created"],
  "detail": {
    "amount": [{"numeric": [">", 100]}]
  }
}
```

```bash
aws events put-rule --name HighValueOrders --event-bus-name my-app-bus --event-pattern '{...}'
aws events put-targets --rule HighValueOrders --event-bus-name my-app-bus --targets ...
```

## Pattern Matching

Rich:
- Exact: `{"source": ["my.app"]}`
- Prefix: `{"detail-type": [{"prefix": "Order"}]}`
- Numeric: `{"amount": [{"numeric": [">", 100, "<", 1000]}]}`
- Suffix: `{"file": [{"suffix": ".csv"}]}`
- Anything-but: `{"status": [{"anything-but": "cancelled"}]}`
- Exists: `{"customer.email": [{"exists": true}]}`

Powerful filtering.

## Targets

Per rule (up to 5 typically):
- Lambda
- SQS
- SNS
- Step Functions
- ECS task
- Kinesis stream
- Firehose
- API Gateway
- Cross-account event bus
- HTTP endpoint (via API destinations)

One rule → multiple targets.

## Input Transformer

Reshape event before sending to target:
```json
{
  "InputPathsMap": {
    "id": "$.detail.order_id",
    "amount": "$.detail.amount"
  },
  "InputTemplate": "{\"orderId\":\"<id>\", \"value\":<amount>}"
}
```

Lambda receives transformed payload.

## Cross-Account

Bus A → Bus B (in another account):
- Bus B policy allows account A
- Rule in A: target = Bus B

For: multi-account event sharing.

## SaaS Partner Buses

Partner sends events to dedicated bus in your account:
- Stripe webhook → Partner bus → your rules
- No webhook receiver needed
- AWS handles auth, retry

For: Stripe, Auth0, Segment, MongoDB Atlas, Datadog, ...

## EventBridge Schedule

Replaces CloudWatch Events cron:
```bash
aws scheduler create-schedule \
  --name daily-cleanup \
  --schedule-expression "cron(0 9 * * ? *)" \
  --target '{"Arn":"arn:aws:lambda:...","RoleArn":"arn:..."}' \
  --flexible-time-window 'Mode=OFF'
```

Schedule per resource (vs single rule for many). Better limits.

## Archive + Replay

Archive events to retention period; replay later:
```bash
aws events create-archive --archive-name MyArchive --event-source-arn arn:aws:events:...:event-bus/my-app-bus --retention-days 365
```

Replay:
```bash
aws events start-replay --replay-name replay1 --event-source-arn ... --event-start-time ... --event-end-time ... --destination ...
```

For: debugging, reprocessing after fix, disaster recovery.

## Schema Registry

Auto-discover event schemas; codegen client:
```bash
aws schemas discover-schemas --event-bus-name my-app-bus
```

Generates schema; download client code.

For: typed events; team coordination.

## API Destinations

EventBridge sends to external HTTP endpoint:
- Auth methods: API Key, Basic, OAuth
- Retry policy
- Rate limit

For: webhook delivery managed by AWS.

## Pipes

Connect source → enrichment (optional Lambda) → target with filter:
```
DynamoDB Stream → Pipe (filter, transform) → EventBridge bus
SQS → Pipe → Lambda
Kinesis → Pipe → another Kinesis
```

Reduces Lambda code for simple routing.

## Cross-Region

Event bus per region. For cross-region:
- Bus replication (custom Lambda)
- Or send target in another region (cross-region invoke; some targets support)

## Pricing

- Custom events: $1/M
- Schedule: free baseline
- Cross-account: no extra
- Replay: standard event price

For 10M events/mo: ~$10. Cheap.

## When Use EventBridge

- Decouple via events
- Many sources / targets
- Rich filtering needed
- SaaS partner integration
- Replay needed
- Schema registry
- Schedule

## When SNS / SQS

- High-throughput fan-out: SNS may scale better
- Strict ordering: SQS FIFO
- Buffered queue: SQS

## Patterns

### Microservices Decoupled
Service A → EventBridge → Service B, C, D

Each service publishes events; subscribes to others.

### Saga Pattern
```
Order → events
  → InventoryReserved → Charge service
    → Charged → Ship service
      → Shipped → Notify
```

Each step publishes; next subscribes.

### Multi-Tenant SaaS
- Tenant ID in event
- Filter rules per tenant
- Bus per tenant if large isolation

### Event Sourcing
Append events to archive; rebuild state via replay.

## Best Practices

- Custom bus per major boundary (not all on default)
- Schema discipline
- Filter rules (don't process all)
- DLQ on targets
- Idempotent consumers
- Archive critical events
- Monitor delivery failures

## DLQ

For failed delivery:
```yaml
DeadLetterConfig:
  Arn: arn:aws:sqs:...
```

Per target. Investigate; replay.

## Idempotency

Consumers must be idempotent. EventBridge can deliver multiple times.

Use event ID:
```python
def handle(event):
    if processed(event["id"]):
        return
    do_work(event)
    mark_processed(event["id"])
```

## Common Mistakes

- All events on default bus (no isolation)
- No DLQ
- Wide pattern matches (target busy)
- Forgetting cross-region nuance
- Schema drift

## Monitoring

CloudWatch:
- MatchedEvents (rule matched)
- InvocationsCount (target invoked)
- FailedInvocations
- ThrottledRules
- DeadLetterInvocations

Alert on failures.

## Best Use

For new event-driven AWS: EventBridge.
For pure fan-out fast: SNS still simple.
For queue with retry: SQS.

Often combination.

## Quick Refs

```bash
# Bus
aws events create-event-bus --name my-bus

# Rule
aws events put-rule --name MyRule --event-bus-name my-bus --event-pattern '{...}'

# Target
aws events put-targets --rule MyRule --event-bus-name my-bus --targets 'Id=1,Arn=arn:lambda:...'

# Put event
aws events put-events --entries '[{"Source":"my.app","DetailType":"X","Detail":"{}","EventBusName":"my-bus"}]'

# Schedule
aws scheduler create-schedule --name daily --schedule-expression "rate(1 day)" --target ...
```

## Interview Prep

**Mid**: "EventBridge vs SNS."

**Senior**: "Schema registry use."

**Staff**: "Event-driven architecture at scale."

## Next Topic

→ [T04 — Kinesis Data Streams, Firehose, Analytics](T04-Kinesis.md)
