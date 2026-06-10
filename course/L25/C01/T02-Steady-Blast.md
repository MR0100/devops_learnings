# L25/C01/T02 — Steady State, Blast Radius

## Learning Objectives

- Define steady state
- Limit blast

## Steady State

What's normal?
- Metrics in expected range
- Error rate
- Latency
- Throughput

Pre-experiment: measure.

## Examples

### Web Service
- Availability 99.95%
- p99 latency 200ms
- Error rate 0.05%
- 5000 RPS

### Background Job
- Queue depth < 100
- Processing rate 100/sec
- Failed jobs < 1%

### Multi-Tier
Composite SLI.

## Measure

```promql
# Availability
1 - (errors / total)

# p99
histogram_quantile(0.99, ...)

# Throughput
rate(requests[5m])
```

## Document

Before experiment:
- Baseline metrics
- Time window
- Stability period

## Blast Radius

How much affected:
- Pods
- Region
- % traffic
- Duration

Limit:
- Smaller better
- Recover quickly

## Levels

### Local
One pod / instance.
Minimal blast.

### Regional
One AZ / region.
Medium blast.

### Global
Whole service.
Big blast; production rare.

## Limit Strategies

### Percentage
Affect 1% of traffic / pods.

```yaml
selector:
  pods:
    namespace: prod
    sample:
      fixed: 1   # 1 pod
```

### Duration
5 minutes; auto-recover.

### Conditional
Stop if error rate > 5%.

## Stop Conditions

```yaml
abort:
  conditions:
    - metric: error_rate
      threshold: 0.05
```

Auto-abort.

## Recovery

After:
- Auto-revert
- Verify steady state
- Document

## Production vs Dev

### Dev
Larger blast OK.

### Staging
Larger blast.

### Production
Smallest possible.
Build up trust.

## Gradual

```
Week 1: 1 pod for 1 min
Week 2: 10 pods for 5 min
Week 3: 1 AZ for 10 min
Week 4: 1 region for 30 min
```

## Observability

During:
- Watch metrics
- Customer impact
- Cascading effects

For: see real-time.

## Communication

Before:
- Announce in channel
- Customer comm if needed

For: avoid confusion (real outage vs experiment).

## Examples

### Pod Kill
1 pod / 30 sec / 10 min.
Verify auto-replace.

### Network Latency
100ms added on 5% of pods.
Verify circuit breakers.

### Region Failure
Block traffic to us-east-1 for 30 min.
Verify failover.

## Best Practices

- Baseline measured
- Hypothesis clear
- Blast radius small
- Stop conditions auto
- Observers ready
- Recovery tested

## Common Mistakes

- No baseline
- Too big blast
- No stop conditions
- No observers
- Slow recovery

## Quick Refs

```
Steady state: baseline metrics
Blast: scope of impact

Limit:
- % affected
- Duration
- Auto-abort
```

## Interview Prep

**Mid**: "Steady state."

**Senior**: "Blast control."

**Staff**: "Chaos at prod."

## Next Topic

→ [T03 — Maturity Levels](T03-Maturity-Levels.md)
