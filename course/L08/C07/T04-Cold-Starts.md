# L08/C07/T04 — Cold Starts & Mitigations

## Learning Objectives

- Diagnose cold starts
- Apply mitigations

## What

First invocation on a new Lambda instance. AWS:
1. Allocates compute
2. Downloads code
3. Initializes runtime
4. Runs init code (imports, globals)
5. Invokes handler

Time: 100ms - 10s typically.

## Cold Start Time Breakdown

| Runtime | Typical |
|---|---|
| Node.js | 200-400ms |
| Python | 200-500ms |
| Go (custom) | 100-300ms |
| .NET | 1-3s |
| Java | 3-10s |
| Container | 200ms-2s |

## When Cold Starts

- First invocation
- After idle (instance reaped after 5-15 min idle)
- Concurrent invocations beyond warm pool
- After code/config update
- Periodic infrastructure refresh

## Impact

- API latency spike
- Time-critical operations affected
- p99 latency dominated

For batch / async: usually OK.
For user-facing API: problematic.

## Diagnose

X-Ray traces show INIT segment duration.

CloudWatch metric `InitDuration`: cold start time.

Sample log:
```
REPORT RequestId: ... Duration: 123ms Init Duration: 1500ms
```

Init Duration present = cold start.

## Mitigations

### 1. Provisioned Concurrency

Pre-warmed instances. No cold start.

Cost: $0.0000041667/GB-sec pre-warm.

For 1 GB function, 50 provisioned: $540/mo.

Best for: high-traffic critical paths.

### 2. Smaller Package

Less code to download / init.

- Remove unused deps
- Layer separation
- Bundle strategically
- Webpack / esbuild minify

### 3. Init Optimization

Lazy import:
```python
# Slow (init time)
import pandas
import numpy
import boto3

# Fast (defer to first invoke)
def handler(event, context):
    import pandas  # only when called
```

Tradeoff: first warm invocation slightly slower.

### 4. Increase Memory

More memory → more CPU → faster init.

Test: function at 128 MB cold = 3s; at 1769 MB cold = 800ms.

Often cheaper overall (less wall time billed).

### 5. Avoid VPC

VPC attaches ENI; adds cold start. AWS improved 2019; now ~200ms overhead (was 10s).

If function doesn't need private resources: no VPC.

### 6. SnapStart (Java)

Snapshot warmed JVM; restore on cold. 10× faster Java cold start.

Free. Enable per function.

### 7. Runtime Choice

Switch to faster runtime (Python/Node/Go) if possible.

### 8. Container vs ZIP

Containers have unique cold start; can be optimized:
- Cache layers
- Use AWS-provided base
- Minimize image

### 9. Provisioned + Auto Scaling

Auto-scale provisioned based on utilization:
```
Min: baseline always warm
Max: peak
Target: 70% utilization
```

## Warming Strategies (Anti-Patterns)

### Ping Function
Schedule EventBridge → invoke every X minutes to keep warm.

Doesn't actually work well anymore:
- One ping keeps ONE instance warm
- New concurrent invocations still cold
- AWS varies instance lifetime

Provisioned concurrency replaced this.

### Self-Invoke
Function invokes itself periodically. Same issue.

Don't bother.

## When Provisioned Concurrency

Decision matrix:

| Use case | Provisioned? |
|---|---|
| Sync API < 1s latency target | Yes |
| Async event processing | No |
| Batch / cron | No |
| Java function in critical path | Yes |
| Periodic high traffic | Auto-scale provisioned |

## Cost vs Benefit

Provisioned cost vs Lambda invocation cost:
- 1 GB provisioned: $10.80/mo per instance
- 1 GB Lambda execution: $0.0000166667/sec

For 100 req/sec × 200ms: 20 concurrent.
- On-demand cold start impact: ~5% requests hit cold
- Provisioned 20: $216/mo

If business value of <100ms p99 > $216: provisioned.

## Snap (Container)

Container images: cold start optimization:
- Smaller base image
- Layer caching (AWS caches popular layers)
- AWS base images optimized
- Stratify (rarely-changed at bottom)

## Cold Start Per Concurrency

Each concurrent invocation = its own instance. First each = cold.

Burst from 0 → 100 concurrent: 100 cold starts.

Provisioned 100: 0 cold.

## Real Numbers

Python Lambda, 512 MB, no VPC:
- Cold: ~300ms (init) + handler
- Warm: handler only

VPC adds: ~200ms cold.

Java cold: 3s+ without SnapStart; ~500ms with.

## Strategies by Function Type

### Web API
- Provisioned concurrency
- Small package
- Avoid VPC
- Smallest viable runtime (Node/Python)

### Event Processor (async)
- No mitigation needed (async OK)
- Optimize for throughput

### ML Inference
- Container image with model
- Provisioned (cold start = load model)
- High memory

### Scheduled Job
- Don't care about cold
- Optimize cost

## Monitor

CloudWatch:
- Duration (total)
- InitDuration (cold)
- Throttles
- Errors

X-Ray Init segment per invocation.

Alert if InitDuration > target.

## Best Practices

- Profile actual cold start
- Avoid VPC unless needed
- Smallest viable runtime
- Lambda Powertools (don't reinvent)
- Lazy imports
- Provisioned for critical

## Common Mistakes

- Ping warmer in 2025 (use provisioned)
- Heavy init code
- All imports at top
- VPC when not needed
- 128 MB function with heavy work

## Quick Refs

```bash
# Provisioned
aws lambda put-provisioned-concurrency-config --function-name myFn --qualifier prod --provisioned-concurrent-executions 50

# Auto-scale provisioned
aws application-autoscaling register-scalable-target --service-namespace lambda --resource-id function:myFn:prod --scalable-dimension lambda:function:ProvisionedConcurrency --min-capacity 10 --max-capacity 100

# SnapStart (Java)
aws lambda update-function-configuration --function-name myFn --snap-start ApplyOn=PublishedVersions
```

## Interview Prep

**Mid**: "Lambda cold start — what."

**Senior**: "Mitigate cold start in API."

**Staff**: "Provisioned concurrency cost analysis."

## Next Topic

→ [T05 — Step Functions (Standard vs Express)](T05-Step-Functions.md)
