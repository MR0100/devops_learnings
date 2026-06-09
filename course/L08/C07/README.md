# L08/C07 — Serverless on AWS

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Lambda-Architecture.md) | Lambda Architecture & Execution Model | 1 hr |
| [T02](T02-Concurrency.md) | Concurrency, Reserved & Provisioned Concurrency | 1 hr |
| [T03](T03-Layers-Extensions.md) | Lambda Layers, Extensions | 0.5 hr |
| [T04](T04-Cold-Starts.md) | Cold Starts & Mitigations | 1 hr |
| [T05](T05-Step-Functions.md) | Step Functions (Standard vs Express) | 1 hr |
| [T06](T06-EventBridge-SQS-SNS.md) | EventBridge, SQS, SNS | 1 hr |
| [T07](T07-API-Gateway.md) | API Gateway (REST, HTTP, WebSocket) | 1 hr |

## Lambda Execution Model

```
Trigger (API, S3, SQS, EventBridge, etc.)
   ↓
Lambda service
   ├── Cold start (init): download code → start runtime → init handler
   └── Warm: reuse existing micro-VM (Firecracker)
   ↓
Invoke handler (your code)
   ↓
Return / write to dest
```

### Limits (2026)

- Memory: 128 MB to 10,240 MB
- Timeout: 15 min max
- Package: 50 MB zipped, 250 MB unzipped (or 10 GB container image)
- /tmp: 512 MB default, up to 10,240 MB
- Env vars: 4 KB
- Concurrent invocations: 1000 default per region (raise via support)

### Pricing

- Per request ($0.20/M) + per GB-second compute
- ARM (Graviton) ~20% cheaper

## Concurrency

### Reserved Concurrency
- **Reserves** N from account pool for this function
- Caps function at N (also throttles others below)
- Use: ensure a critical fn always has capacity OR cap a downstream-stressing fn

### Provisioned Concurrency
- **Pre-warms** N execution environments
- Eliminates cold start for the provisioned N
- Costs ~$0.015/hr per provisioned environment
- Use: latency-sensitive endpoints

### Auto Scaling
Provisioned Concurrency can auto-scale via Application Auto Scaling target tracking.

## Layers & Extensions

### Layers
- Reusable code (shared libs, runtime extensions)
- Up to 5 layers per function
- Mount at `/opt/`

### Extensions
- Run alongside your function (in init phase + in execution)
- Use for: APM agents (Datadog, New Relic), security agents, Parameters & Secrets Lambda Extension (caching SSM/Secrets)

## Cold Starts

Cold start = first invocation in a new environment.

### Cold Start Breakdown
1. Code download from S3 (small if small package)
2. Runtime init (~50ms for Python/Node, 200ms+ for Java)
3. Handler init (your "outside the handler" code)
4. First invocation

### Mitigation
- **Smaller deployment package**
- **Provisioned Concurrency**
- **SnapStart** (Java only, snapshots init state)
- **Container image**: slower cold start but faster code download for large fns
- **Avoid heavy imports** in handler-scope code
- **Initialize once** (DB connections, SDK clients outside handler)

### Avoid Bursts of Cold Starts
- Provisioned Concurrency for known patterns
- Pre-warm via scheduled "warmer" pings (deprecated practice; PC is better)

## Step Functions

Orchestrate workflows of Lambda + AWS services.

### Standard Workflows
- Long-running (up to 1 year)
- Pay per state transition
- Full visibility
- Exactly-once execution

### Express Workflows
- Short-lived (5 min max)
- High volume (millions/sec)
- At-least-once
- Cheaper per execution

### Common Patterns
- **Saga**: multi-step transaction with compensation
- **Map/Fan-out**: process many items in parallel
- **Wait + Callback**: pause until external system replies
- **Error handling**: Retry/Catch states

## Eventbridge

Event bus for AWS service events + custom + 3rd-party SaaS.

### Concepts
- **Bus**: default (AWS service events) or custom
- **Rule**: matches events by pattern → routes to targets
- **Targets**: Lambda, SQS, SNS, Step Functions, EventBridge in other regions, etc.

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {"name": ["my-bucket"]}
  }
}
```

### Schemas & Discoverer
EventBridge discovers schemas of events flowing through; generates code bindings for type-safe handlers.

## SQS

Queue. Standard or FIFO.

### Standard
- At-least-once delivery
- Best-effort ordering
- ~Unlimited TPS
- Default

### FIFO
- Exactly-once processing (with deduplication)
- Strict ordering
- 300 TPS per group (3000 with batching)
- MessageGroupId for ordering scope

### Common Patterns
- Decouple producer from consumer
- DLQ (Dead Letter Queue) for failures
- Visibility timeout: time consumer has to process before message reappears
- Long polling (20s) reduces empty receives

## SNS

Pub/sub. Topic → many subscribers.

### Fanout pattern
```
SNS Topic
   ├── SQS queue A → consumer A
   ├── SQS queue B → consumer B
   ├── Lambda fn  → process
   └── HTTPS endpoint → 3rd-party webhook
```

### FIFO topic for ordering

## API Gateway

### Three Types

| | REST | HTTP | WebSocket |
|---|---|---|---|
| Features | Most (caching, throttling, validation) | Subset | Stateful WS |
| Cost | Higher | Lower (~70% cheaper) | per connection-minute |
| Latency | Higher | Lower | n/a |
| Use | Need rich features | Simple proxy | Real-time |

### Authorization
- IAM
- Cognito User Pools
- Lambda Authorizer (custom)
- JWT (HTTP API)

### Integrations
- Lambda Proxy (default)
- AWS service (e.g., directly to DynamoDB)
- HTTP backend
- Mock (testing)

### Common Issues
- 30-second integration timeout (long backends fail)
- Cold start of underlying Lambda
- Stage variables for dev/staging/prod

## Lambda Patterns

### Async Lambda → SQS → Lambda
```
API → Lambda (return 202) → SQS → Worker Lambda
```
Decouples; queues smooth spikes.

### Lambda → DynamoDB Streams → Lambda
CDC processing pipeline.

### Lambda + RDS = Problem
- Lambda scales to thousands of concurrent; RDS has limited connections
- Use RDS Proxy

### Lambda + VPC
- VPC-attached Lambda uses ENIs
- Cold start now fast (since 2019 Hyperplane)
- Reaches VPC services; doesn't reach Internet without NAT

## Interview Themes

- "Walk me through Lambda execution model"
- "Cold start mitigation strategies"
- "When Step Functions vs Lambda orchestrating itself?"
- "Compare SQS and SNS"
- "EventBridge — when over SNS?"
- "Design an async API with Lambda"
- "Lambda + RDS — what goes wrong?"
