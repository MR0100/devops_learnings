# L08/C07/T02 — Concurrency, Reserved & Provisioned Concurrency

## Learning Objectives

- Manage Lambda concurrency
- Use reserved/provisioned

## Concurrency

Number of invocations in flight at same time.

Default: 1000 per region (shared across all functions). Soft limit; raise via support.

## Per-Function Behaviors

Unreserved: function can use up to (region limit - reserved by others).

Reserved: guarantee minimum + cap maximum.

```bash
aws lambda put-function-concurrency \
  --function-name myFn \
  --reserved-concurrent-executions 100
```

myFn always has 100 available; cannot exceed 100.

## Why Reserved

### Protect Downstream
Function calls DB; DB has 200 connection limit. Reserve Lambda at 100; never exhausts DB.

### Guarantee Availability
Critical function: ensure at least N available even if other functions spike.

### Cap Cost
Worst-case cost capped at reserved × pricing.

## Provisioned Concurrency

Pre-initialize N instances; always warm; no cold start.

```bash
aws lambda put-provisioned-concurrency-config \
  --function-name myFn \
  --qualifier prod \
  --provisioned-concurrent-executions 50
```

50 instances always running, ready.

Cost:
- $0.0000041667/GB-second pre-warmed
- Plus normal invocation cost

For 1 GB function: ~$10.80/mo per instance pre-warmed.

50 × $10.80 = $540/mo provisioned. Plus invokes.

## When Provisioned

- Cold start unacceptable (e.g., synchronous API with strict SLA)
- Predictable traffic peak (pre-warm before)
- Heavy init (Java startup)

Otherwise: pay for nothing.

## Auto-Scale Provisioned

Application Auto Scaling can scale provisioned:
- Min: baseline (always warm)
- Max: peak
- Scale by ProvisionedConcurrencyUtilization

## Throttling

Exceed concurrency: TooManyRequestsException (429).

Sync invocation: returned to caller.
Async: retried (2 attempts); then DLQ.
SQS / Stream: returned to source; retried.

## Throttle Metrics

CloudWatch:
- Throttles (count)
- ConcurrentExecutions

Alert when throttles >0.

## Account Concurrency

Org-wide:
- Total invocations limited by account concurrency
- Reserve for critical
- Leave room for others

## Burst Limits

Beyond steady concurrency:
- Initial burst: 500-3000 (region-dependent)
- After: linear ramp-up (500/min)

For sudden spike: may throttle initially even under limit.

Pre-warm: provisioned concurrency.

## Concurrency Per Trigger

### SQS
Lambda polls; concurrency scales with queue depth.
- 5 polls × 10 messages = 50 concurrent
- Up to function concurrency

For high throughput: SQS partitioned reads.

### Kinesis / DynamoDB Streams
Concurrency = number of shards (one Lambda per shard).
- More shards = more parallel
- Plus parallelization factor (multiple Lambdas per shard)

### API Gateway
Direct request → invoke. Concurrency = request rate × duration.

### S3 Events
Async; spikes possible. Provisioned helps.

## Concurrency Math

Concurrent ≈ request rate × avg duration:
```
100 req/sec × 200ms = 20 concurrent
1000 req/sec × 500ms = 500 concurrent
```

Plan for peak.

## Async Event Pool

Lambda async events: queue managed by AWS.

Max age (default 6 hr; configurable to 1 sec - 6 hr): events expire if not processed.

DLQ for failures.

## Common Mistakes

- No reserved for critical (throttled by other funcs)
- Provisioned for sporadic (wasted)
- Forgetting burst limit (initial spike throttles)
- Sync invocation when async OK
- No DLQ for async

## Best Practices

- Reserved for critical; cap downstream impact
- Provisioned for latency-critical (with auto-scale)
- Monitor throttles
- DLQ for async
- Plan for burst

## Function Versions / Aliases

Lambda versions: snapshot of code + config.
Alias: pointer to version (e.g., "prod" → v3).

For provisioned: configure on alias (not $LATEST).

```bash
aws lambda publish-version --function-name myFn
aws lambda create-alias --function-name myFn --name prod --function-version 3
```

## Weighted Aliases (Canary)

```bash
aws lambda update-alias --function-name myFn --name prod \
  --function-version 4 \
  --routing-config 'AdditionalVersionWeights={"3"=0.9}'
```

10% to v4 (new); 90% to v3.

For: gradual rollout.

## Account-Level Reserve

Set min unreserved (preserve for unowned functions):
```bash
aws lambda put-account-settings --reserved-concurrent-executions 200
```

Account has 200 always for unreserved.

## Lambda Insights

Per-invocation metrics agent. Extra cost; deeper visibility.

## SnapStart (Java)

Snapshot warmed JVM; restore on invoke. 10× cold start improvement for Java.

Free; enable per function.

## Quick Refs

```bash
# Reserve concurrency
aws lambda put-function-concurrency --function-name myFn --reserved-concurrent-executions 100

# Remove reservation
aws lambda delete-function-concurrency --function-name myFn

# Provisioned
aws lambda put-provisioned-concurrency-config --function-name myFn --qualifier prod --provisioned-concurrent-executions 50

# Get status
aws lambda get-account-settings
```

## Interview Prep

**Mid**: "Reserved vs Provisioned."

**Senior**: "Throttling at scale — mitigate."

**Staff**: "Lambda concurrency for 100k QPS."

## Next Topic

→ [T03 — Lambda Layers, Extensions](T03-Layers-Extensions.md)
