# L27/C04/T02 — Health Checks for Failover

## Learning Objectives

- Design failover health checks
- Avoid false positives

(Complements L24/C01/T02.)

## DR Health Check

Triggers region failover:
- Per service
- From multiple checkers
- Robust to false positives

## Where

- LB (in-region)
- DNS (Route 53)
- Synthetic (external)

## Synthetic

External probes:
- Datadog Synthetic
- Pingdom
- StatusCake
- Custom Lambda

Pros: outside the region; sees real outage.

## Threshold

```
Unhealthy after 3 consecutive failures
Healthy after 2 consecutive successes
```

Avoid flapping.

## Multiple Checkers

```
N regions check
M must agree
```

For: avoid single false positive.

## Failover Decision

Should fail over if:
- Multiple checkers fail
- Sustained (not transient)

NOT for:
- One flap
- One region's network blip

## Manual Override

For:
- Maintenance
- Confirmed failure
- Avoid auto in some cases

## Health Endpoint

```python
@app.get('/health/deep')
def deep_health():
    # Check DB, cache, etc.
```

Slow if checks deps.

For LB: shallow.
For DR: maybe deep (but careful).

## Cascading

If health check hits DB:
- DB slow → health fails → DR failover
- But maybe DB temporarily slow

For: care.

## Test

Quarterly:
- Disable primary
- Verify failover triggers
- Measure RTO

## Best Practices

- External checkers
- Multiple
- Threshold against flap
- Manual override
- Test regularly

## Common Mistakes

- One checker (false positive)
- Flap (in/out)
- Auto-failover too aggressive
- No manual override

## Quick Refs

```
Health: per service
Checkers: external + multiple
Threshold: 3 fails
Test: quarterly
```

## Interview Prep

**Mid**: "DR health checks."

**Senior**: "Avoid false positive."

## Next Topic

→ [T03 — Failover Automation](T03-Failover-Automation.md)
