# L07/C04/T03 — Serverless (Lambda, Cloud Functions, Azure Functions)

## Learning Objectives

- Design serverless apps
- Avoid common pitfalls

## What

Function as a Service: write function; provider runs it on events. No server management; auto-scale; pay per execution.

## Lambda (AWS)

```python
def lambda_handler(event, context):
    # event: payload
    # context: request metadata
    return {"statusCode": 200, "body": "ok"}
```

Triggers:
- HTTP via API Gateway / Function URL / ALB
- S3 events (object created)
- DynamoDB Streams
- SQS / SNS / EventBridge
- Kinesis, Kafka
- CloudWatch schedule (cron)
- Cognito triggers
- Custom (SDK invoke)

Limits:
- 15 min execution
- 10 GB RAM max
- /tmp 512 MB (or up to 10 GB with EFS)
- 250 MB code (50 MB zipped) or container image up to 10 GB

## Cloud Functions / Cloud Run Functions (GCP)

Similar; HTTP and event-driven.
Newer "Cloud Run Functions" is unified with Cloud Run; Knative-based.

## Azure Functions

C#, Node, Python, Java, PowerShell. Triggers: HTTP, Storage, Cosmos, Service Bus, EventGrid, Timer.

Hosting plans: Consumption (true serverless), Premium (no cold start), App Service (more control).

## Cold Start

First invocation after idle: provider provisions runtime + your code. Takes 100ms - 10s depending on:
- Language (Python/Node fast; Java/.NET slow)
- Package size
- VPC attachment (slower)
- Custom runtime / container image

Mitigations:
- Provisioned concurrency (Lambda): pre-warm; pay for idle
- Smaller package
- Avoid VPC if not needed
- Stay in supported runtime

## Pricing

```
Lambda:
$0.20 per 1M requests
$0.0000166667 per GB-second

1M requests × 1s × 1GB = $16.87
```

Cheap for sporadic. Expensive for steady (e.g., 24/7 = $4.32 per GB-second of base cost).

Provisioned concurrency: pay for keep-warm regardless of use.

## State

Stateless. Each invocation independent. State:
- DynamoDB / Firestore
- S3 / GCS
- Redis (ElastiCache, Memorystore)
- Session in JWT
- Outside function

In-memory globals persist across invocations on warm instance — exploit for connection pools:
```python
import boto3
# Module-level: reused on warm
s3 = boto3.client("s3")

def handler(event, context):
    # s3 already initialized
    ...
```

## Patterns

### API Backend
API Gateway → Lambda → DynamoDB.

```
GET /users/{id}
↓
API Gateway routes to GetUserFunction
↓
Lambda reads DDB; returns
```

### Event Processing
S3 → Lambda → process file.

```
File uploaded to S3
↓
S3 event triggers Lambda
↓
Lambda reads object; transforms; writes elsewhere
```

### Stream Processing
DynamoDB Streams / Kinesis → Lambda → side effect.

### Cron / Schedule
EventBridge schedule → Lambda → daily report.

### Webhooks
HTTP → API Gateway → Lambda → validate; enqueue.

### Glue
Auto-tag EC2 instances, rotate secrets, daily cleanups.

## Lambda Layers

Shared code across functions:
```bash
# Build layer
mkdir -p python/lib/python3.11/site-packages
pip install requests -t python/lib/python3.11/site-packages/
zip -r layer.zip python

aws lambda publish-layer-version --layer-name my-libs --zip-file fileb://layer.zip
```

Attach to function; loads at /opt.

## Container Image Lambda

Instead of zip, use container image (up to 10 GB):
```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY app.py ${LAMBDA_TASK_ROOT}
CMD ["app.lambda_handler"]
```

Push to ECR; create Lambda from image. Useful for ML models, large deps.

## VPC

Lambda in VPC: access private resources (RDS in private subnet). But:
- Need ENI per concurrency (uses subnet IPs)
- Cold start slower (ENI provisioning)

Many ops don't need VPC. Lambda has internet by default.

## Concurrency

Default 1000 simultaneous executions per region. Can request increase.

Per-function limit: reserve specific count. Prevent one function consuming all.

Provisioned concurrency: pre-init N instances; no cold start.

## Error Handling

Lambda retries on async invokes (event source like SQS, S3): 2 retries. Then DLQ if configured.

For sync (API Gateway): no auto retry; client must.

DLQ (dead letter queue): failed events go here for investigation.

## Step Functions

For multi-step workflows: orchestrator service.
- State machine (JSON definition)
- Each state can be a Lambda, ECS task, wait, parallel, choice
- Built-in error handling, retries
- Express vs Standard (different cost/latency)

```
[Start] → [Validate] → [Process] → (success) → [Notify]
                                  → (fail) → [Handle Error]
```

## Patterns to Avoid

### Lambda calling Lambda calling Lambda
Nesting = cost × delay. Use Step Functions instead.

### Long-running task in Lambda
Lambda 15 min max. Use Fargate / Batch for longer.

### Database connection pool issue
DB sees many concurrent connections (one per Lambda instance). Solution: RDS Proxy.

### Logging insane amounts to CloudWatch
$0.50/GB ingestion. Sample / structured / send to cheaper store.

### Hot path with cold start sensitivity
Provisioned concurrency or rewrite to container.

## When Serverless Wins

- Event-driven
- Sporadic / bursty
- Glue / automation
- Low-traffic API
- Background jobs
- Webhooks

## When Serverless Loses

- Sustained high traffic (cheaper on EC2/ECS)
- Long-running (15-min cap)
- Specialty hardware (GPU limited)
- Latency-critical (cold start)
- Stateful

## Observability

CloudWatch logs auto. Metrics: invocations, duration, errors, throttles.

X-Ray tracing for distributed (Lambda → DDB → other Lambda).

OpenTelemetry / Datadog / NewRelic agents available as layers.

## Cost Pitfalls

- Recursive trigger loop (Lambda updates S3 → triggers Lambda → updates S3...)
- Provisioned concurrency forgotten (paying for idle)
- High memory + low CPU usage (paying for memory you don't use)
- Logs at INFO + retention forever

## Local Dev

- AWS SAM (Serverless Application Model)
- Serverless Framework
- LocalStack (mock AWS locally)
- Test functions directly with mocks

```bash
sam local invoke -e event.json MyFunction
```

## Lambda Function URLs

Direct HTTPS endpoint without API Gateway. Simpler; cheaper. Lacks API Gateway features (custom domains, throttling).

## Lambda SnapStart

Java specifically: snapshot warmed JVM; restore on cold start. Dramatically faster Java cold starts.

## Interview Prep

**Junior**: "What is serverless?"

**Mid**: "Lambda cold start — mitigate."

**Senior**: "Design event-driven order pipeline with Lambda."

**Staff**: "Lambda or Fargate for $X workload — math."

## Next Topic

→ Move to [L07/C05 — Storage Family](../C05/README.md)
