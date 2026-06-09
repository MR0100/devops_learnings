# L08/C11/T03 — X-Ray Tracing

## Learning Objectives

- Use X-Ray for distributed tracing
- Interpret traces

## X-Ray

AWS distributed tracing. Trace request flow across services.

For:
- Latency bottlenecks
- Error sources
- Service dependencies
- Performance optimization

## Concepts

- **Trace**: end-to-end request
- **Segment**: work in one service
- **Sub-segment**: work within service (DB call, HTTP request)
- **Annotations**: indexed metadata
- **Metadata**: non-indexed metadata

## Instrumentation

### Lambda
Enable Tracing in function config:
```bash
aws lambda update-function-configuration --function-name myFn --tracing-config Mode=Active
```

X-Ray captures:
- Init duration
- Invocation duration
- Errors

### ECS / EKS / EC2
Install X-Ray daemon (sidecar / DaemonSet):
- Listens on UDP 2000
- Forwards to X-Ray service

App SDK sends segments to daemon.

### SDK Auto-Instrumentation

Python:
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.boto3.patch import patch_all
patch_all()

# All boto3 calls now traced
import boto3
s3 = boto3.client("s3")
s3.list_buckets()    # creates X-Ray sub-segment
```

Node:
```javascript
const AWSXRay = require("aws-xray-sdk");
const AWS = AWSXRay.captureAWS(require("aws-sdk"));
```

## Custom Sub-Segments

```python
with xray_recorder.in_subsegment("db_query") as subsegment:
    subsegment.put_annotation("query_type", "SELECT")
    result = db.query(...)
    subsegment.put_metadata("rows_returned", len(result))
```

## Annotations vs Metadata

Annotations: indexed; queryable in service map filters.
Metadata: stored but not indexed.

```python
xray_recorder.put_annotation("user_id", user_id)    # filterable
xray_recorder.put_metadata("request_body", body)    # stored
```

Annotations: simple types (string, number, bool).

## Sampling

X-Ray samples requests (default 1 req/sec + 5% rest).

For higher: configure sampling rule:
```bash
aws xray create-sampling-rule --sampling-rule '{
  "RuleName": "MyApp",
  "ServiceName": "*",
  "ServiceType": "*",
  "Host": "*",
  "HTTPMethod": "*",
  "URLPath": "/api/critical/*",
  "FixedRate": 1.0,
  "ReservoirSize": 100,
  "Priority": 1
}'
```

100% sample on critical paths; less elsewhere.

## Service Map

Visual graph of services + dependencies:
- Boxes: services
- Lines: calls
- Color: error rate / latency

Click for trace list.

## Traces View

Per trace:
- Timeline (waterfall)
- Each segment's duration
- Errors highlighted
- Annotations / metadata

## Searching

Filter:
- Service name
- HTTP method / status
- Annotation values
- Latency > N
- Errors

For: investigation.

## Errors

X-Ray records:
- Fault (5xx)
- Error (4xx)
- Throttle (429)

Per segment.

## Distributed Context

Trace ID propagates across service calls via headers:
- X-Amzn-Trace-Id

Downstream services attach to same trace.

API Gateway, ALB, Lambda, SDKs propagate automatically.

For HTTP custom: pass header manually.

## OpenTelemetry

Industry standard for tracing. AWS distro (ADOT):
- Send to X-Ray
- Send to Honeycomb, Datadog, etc.
- Multi-backend

For new: OTel (multi-vendor); X-Ray as backend if AWS preferred.

## When NOT X-Ray

- Non-AWS workload (use Datadog, Jaeger, etc.)
- Already have OTel stack
- Sub-millisecond timing critical (X-Ray sampling impacts)

## Pricing

- $5 per million traces recorded
- $0.50 per million scanned (queries)

For 10M req/mo at 10% sample: 1M traces × $5 = $5/mo. Cheap.

## Integration

X-Ray auto:
- Lambda (just enable)
- API Gateway
- ALB
- App Runner
- SNS / SQS
- ECS / EKS (with daemon)
- DynamoDB / S3 / RDS (via SDK)

For others: manual SDK instrument.

## Lambda Insights vs X-Ray

| | Lambda Insights | X-Ray |
|---|---|---|
| Focus | Lambda perf | Distributed flow |
| Per | Function | Request |
| Cost | Per function | Per trace |
| When | Single function | Multi-service flow |

Use both. Insights for Lambda; X-Ray for tracing.

## Insights / Anomaly Detection

X-Ray Insights: auto-detect anomalies (X-Ray service feature).
- Sudden error rate spike
- Latency increase
- New service unhealthy

## Best Practices

- 100% sample critical path; lower elsewhere
- Annotate user_id, tenant_id (filter by)
- Custom sub-segments for major operations
- Propagate context across systems
- OpenTelemetry for multi-backend

## Common Mistakes

- All in one segment (no granularity)
- No annotations (can't filter)
- 100% sample everywhere (cost)
- Trace context dropped at SQS → Lambda (configure)

## SQS / SNS Trace Continuation

Trace context lost across SQS → Lambda by default. To continue:
- Include trace context in message attributes
- Re-attach in consumer

Lambda Powertools helps.

## CloudWatch ServiceLens

Combines X-Ray + CloudWatch + Synthetics. Unified view.

## Custom Sample Rule Example

```json
{
  "RuleName": "Sensitive",
  "URLPath": "/api/critical",
  "FixedRate": 1.0,
  "ReservoirSize": 100,
  "Priority": 100
}
```

Higher priority wins.

## Anti-Pattern: No Tracing

For distributed system: tracing essential. Without it: debugging is grep + guess.

## Quick Refs

```bash
# Enable on Lambda
aws lambda update-function-configuration --function-name myFn --tracing-config Mode=Active

# Sampling rule
aws xray create-sampling-rule --sampling-rule ...

# Get trace
aws xray batch-get-traces --trace-ids ...

# Query
aws xray get-trace-summaries --start-time ... --end-time ... --filter-expression 'service("api") { responsetime > 5 }'
```

## Interview Prep

**Mid**: "X-Ray basics."

**Senior**: "Trace latency issue in microservices."

**Staff**: "OTel vs X-Ray."

## Next Topic

→ [T04 — Managed Prometheus & Grafana](T04-Managed-Prom-Grafana.md)
