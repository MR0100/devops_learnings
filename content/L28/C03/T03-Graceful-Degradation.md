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

**Junior**: "What is graceful degradation?" — When a component fails, the system reduces functionality instead of dying entirely — core features keep working while nice-to-haves turn off. Amazon's page still loads and sells when recommendations are down; it just shows generic suggestions.

**Mid**: "Give an example of designing for graceful degradation." — Wrap a non-critical dependency in a timeout + fallback: if the recommendations service doesn't answer in 1s, serve cached or popular defaults and render the page anyway. The key is deciding *ahead of time* what's critical (must work) versus optional (can degrade) so the failure path is designed, not improvised during an incident.

**Senior**: "How does graceful degradation combine with circuit breakers and feature flags?" — Circuit breakers detect a failing dependency and stop calling it (so you fail fast to the fallback instead of piling up timeouts), then periodically test recovery. Feature flags give ops a kill switch to shed expensive optional features during an incident to reduce load. Together: the breaker automatically routes around a dead dependency, the flag lets a human proactively trim load, and stale-while-revalidate caching keeps responses non-empty — layered defenses so the core path survives.

**Staff**: "Design a system that degrades gracefully under partial failure rather than collapsing." — Start by classifying every dependency as critical or optional and giving each optional one a defined fallback (cache, default, or skip). Keep the critical path as simple and dependency-light as possible so it has the fewest ways to fail. Add a read-only mode for write-DB outages (reads serve, writes queue for later), stale-while-revalidate so caches never go empty, circuit breakers around every cross-service call, and feature flags as kill switches. Then *test* it — game-day the degraded paths — because an untested fallback is just a second bug waiting for the worst moment. The failure mode I'm designing out is all-or-nothing, where one optional dependency takes down the whole page.

## Next Topic

→ Move to [L28/C04 — Real-World System Designs](../C04/README.md)
