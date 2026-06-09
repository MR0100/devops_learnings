# L08/C07/T01 — Lambda Architecture & Execution Model

## Learning Objectives

- Understand Lambda internals
- Design effective functions

## Lambda

Serverless compute: write function; AWS runs on events. No server management.

## Execution Model

```
Event → Lambda service → Find/create instance → Init runtime → Init handler → Invoke handler → Return
```

Three phases:
- INIT (cold start)
- INVOKE
- SHUTDOWN

## Instance Lifecycle

Each instance handles ONE invocation at a time. Multiple instances for concurrent invocations.

After invocation: instance kept warm for next (minutes typically). Reuse:
- Module-level globals persist
- DB connections persist
- Tmp dir state persists (/tmp; reused but not guaranteed)

Idle long: instance terminated.

## Cold Start

First invocation on new instance:
1. Download code from S3 (~ms)
2. Start runtime (Python, Node, ...)
3. Init code (module imports, global vars)
4. Invoke handler

Cold time: 100ms-10s depending on:
- Runtime (Python/Node fast; Java/.NET slow)
- Package size
- VPC attachment (slower)
- Init code complexity

## Warm Invocation

Subsequent: skip steps 1-3. Just invoke handler. ~ms.

## Exploit Warm

```python
import boto3
s3 = boto3.client("s3")    # module-level; persists across invocations

def handler(event, context):
    # s3 already initialized
    s3.get_object(...)
```

vs:
```python
def handler(event, context):
    s3 = boto3.client("s3")   # initialized every invocation (slow)
    ...
```

Use module-level for expensive setup.

## Limits

| | Limit |
|---|---|
| Execution time | 15 min |
| Memory | 128 MB - 10 GB |
| /tmp size | 512 MB - 10 GB |
| Code size | 250 MB (50 MB zipped) or 10 GB container image |
| Payload | 6 MB sync, 256 KB async |
| Env vars total | 4 KB |
| Concurrent | 1000/region default (raise) |

## Memory + CPU

Memory determines CPU allocation:
- 128 MB: small CPU
- 1769 MB: 1 vCPU
- 10 GB: ~6 vCPU

Increase memory for CPU-bound functions; often cheaper overall (less duration).

## Pricing

```
$0.20 per 1M requests
$0.0000166667 per GB-second
```

1M requests × 1s × 1 GB = $16.87.

Free tier: 1M requests + 400k GB-sec/mo permanently.

## Runtimes

Officially supported:
- Python 3.x
- Node.js
- Java
- .NET
- Ruby
- Go (custom runtime)
- Custom Runtime (build with provided.al2)
- Container images (any runtime)

## Container Image Lambda

```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY app.py ${LAMBDA_TASK_ROOT}
CMD ["app.handler"]
```

Build, push to ECR, create Lambda from image. Up to 10 GB.

For: heavy ML models, large deps.

## Layers

Reusable packages across functions:
- Shared deps (numpy, pandas)
- Custom code
- Up to 5 layers per function

Layer ZIP loaded at /opt.

## Event Sources

Many triggers:
- API Gateway (HTTP)
- S3 events
- DynamoDB Streams
- SQS
- SNS
- EventBridge (scheduled / event-driven)
- Kinesis
- Cognito
- ALB
- Function URL (direct HTTPS)
- IoT, MQ, Kafka (MSK)

## Sync vs Async

**Sync**: Client waits; sees response. (API Gateway, ALB)

**Async**: Client returns immediately; Lambda processes later. (S3, SNS, EventBridge)

Async has retries (2 default + DLQ).

## Function URL

Direct HTTPS endpoint:
```
https://<unique>.lambda-url.region.on.aws/
```

No API Gateway. Cheaper / simpler. Lacks API GW features (custom domain, throttling, auth).

## IAM Execution Role

Lambda assumes this role. Has permissions for:
- CloudWatch Logs (mandatory)
- AWS services Lambda accesses

Define minimal:
```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

## VPC

Lambda by default: no VPC; AWS-managed network with Internet.

In VPC: access private resources (RDS, internal LB):
- Need ENI per concurrency (uses subnet IPs)
- Cold start slower

Best practice: use VPC only if needed. Use VPC endpoints (no NAT cost).

## Configuration

```bash
aws lambda create-function \
  --function-name myFn \
  --runtime python3.11 \
  --role arn:aws:iam::123:role/myRole \
  --handler app.handler \
  --zip-file fileb://code.zip \
  --memory-size 512 \
  --timeout 30 \
  --environment "Variables={KEY=value}"
```

## Environment Variables

Plain text in function. For secrets:
- Use Secrets Manager / Parameter Store at runtime
- KMS-encrypted env var (Lambda decrypts on init)

## Logs

Auto to CloudWatch:
- /aws/lambda/<function-name>
- Per invocation log stream

Cost: $0.50/GB ingestion. Watch INFO logs in tight loops.

## Metrics

CloudWatch built-in:
- Invocations
- Errors
- Throttles
- Duration
- ConcurrentExecutions

## X-Ray

Distributed tracing:
- Per invocation trace
- Sub-segments (DB call, S3 call)
- Service map (visualize chain)

Enable per function; ~$5/M traces.

## Lambda Powertools

Library (Python, Node, Java) with utilities:
- Structured logging
- Metrics (EMF)
- Tracing
- Idempotency
- Validation
- Batch processing
- Feature flags

For prod Lambda: use Powertools.

## Concurrency

Default 1000 concurrent across all Lambda in region.

Per function: reserved concurrency (guarantee + cap).

```bash
aws lambda put-function-concurrency --function-name myFn --reserved-concurrent-executions 100
```

Reserved 100: function always has 100 available; others share remaining.

## Async Retries

Default 2 retries with backoff. DLQ for failures:
```bash
aws lambda put-function-event-invoke-config --function-name myFn \
  --destination-config '{"OnFailure":{"Destination":"arn:aws:sqs:..."}}'
```

## SQS as Trigger

```
SQS → Lambda
```

Lambda polls SQS; processes batches.

Throughput: scales with concurrency.

If function fails: message returned to queue; retry.

## DynamoDB Streams as Trigger

```
DynamoDB → Stream → Lambda
```

Polls stream; processes records.

Ordered per partition. Concurrency per shard.

## Patterns

### Sync API
API Gateway → Lambda → DynamoDB; return result.

### Async Event Processing
S3 → Lambda → write to elsewhere.

### Cron / Schedule
EventBridge schedule → Lambda → daily task.

### Glue / Webhook
HTTP → Lambda → enqueue.

## Best Practices

- Module-level for expensive init
- Right memory size (test)
- Short timeout (catch hangs)
- Powertools
- Structured logs
- Idempotency
- DLQ
- Monitor errors / throttles

## Common Mistakes

- Init inside handler
- Long timeout (cost on hang)
- No error handling
- Returning to client large data (6 MB sync limit)
- Lambda calling Lambda calling Lambda
- Forgetting VPC ENI consumption

## Quick Refs

```bash
# Create
aws lambda create-function ...

# Update code
aws lambda update-function-code --function-name myFn --zip-file fileb://code.zip

# Invoke
aws lambda invoke --function-name myFn --payload '{}' out.json

# Logs
aws logs tail /aws/lambda/myFn --follow
```

## Interview Prep

**Junior**: "What is Lambda."

**Mid**: "Cold start mitigation."

**Senior**: "Lambda + RDS connection scaling."

**Staff**: "When NOT Lambda."

## Next Topic

→ [T02 — Concurrency, Reserved & Provisioned Concurrency](T02-Concurrency.md)
