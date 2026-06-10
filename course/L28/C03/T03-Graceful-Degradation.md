# L28/C03/T03 — Graceful Degradation

## Learning Objectives

- Degrade gracefully
- Maintain core function

## Graceful Degradation

When component fails:
- Reduce features
- Core works
- Users see reduced but functional

vs Catastrophic:
- Everything dies

## Strategies

### Fallback
Recommendations service down:
- Show generic
- Cached

### Cache Stale
DB slow:
- Serve cached
- Eventual update

### Skip Optional
Nice-to-have features off:
- Comments disabled
- Search degraded

### Pre-Render
Show static; fetch dynamic later.

## Examples

### Amazon
Recommendations down:
- Page still loads
- "You might like..." replaced with generic

### Netflix
Personalization down:
- Show popular instead
- Stream still works

### News
Comments off; article still readable.

## Implementation

```python
try:
    recommendations = call_recs_service(timeout=1)
except (Timeout, ServiceUnavailable):
    recommendations = cached or popular_default

return render(page, recommendations=recommendations)
```

For: try, fall back.

## Circuit Breaker

Combined:
- Detect failure
- Open circuit
- Use fallback
- Try again later

## Feature Flags

Toggle features off:
- During incidents
- Reduce load
- Skip expensive

For: ops control.

## Cache TTL

Stale-while-revalidate:
- Serve stale up to X
- Refresh in background

For: never empty.

## Read-Only Mode

If write DB down:
- Reads still work
- "Cannot edit right now"
- Save to queue for later

## Design For

In design:
- Identify critical
- Identify nice-to-have
- Design failure paths

## Best Practices

- Critical path simplest
- Optional features degradable
- Caching with stale
- Feature flags
- Test degradation

## Common Mistakes

- All-or-nothing (fail catastrophically)
- Required everything
- No fallback
- Untested

## Quick Refs

```
Critical: must work
Optional: can degrade
Fallback: ready
Cache stale: OK
Feature flag: kill switch
```

## Interview Prep

**Mid**: "Graceful degradation."

**Senior**: "Design for failure."

**Staff**: "Resilience patterns."

## Next Topic

→ Move to [L28/C04 — Real-World System Designs](../C04/README.md)
