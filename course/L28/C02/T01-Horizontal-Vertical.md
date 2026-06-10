# L28/C02/T01 — Horizontal vs Vertical Scaling

## Learning Objectives

- Compare scaling
- Pick approach

## Vertical

Bigger machine:
- More CPU
- More RAM
- Faster disk

Pros:
- Simple
- No code changes

Cons:
- Limited (max instance size)
- Single point
- Cost (premium for big)

## Horizontal

More machines:
- Distribute load
- Add capacity

Pros:
- Near-infinite scale
- HA inherent
- Commodity hardware

Cons:
- Distributed complexity
- State management
- Network overhead

## When Vertical

- Stateful (DB)
- Limited scale needed
- Quick fix
- License costs (per host)

## When Horizontal

- Stateless apps
- High scale needed
- Cost-sensitive
- HA required

## Combine

Common:
- Web tier: horizontal
- Cache: horizontal (cluster)
- DB: vertical first, then horizontal (sharding)
- Workers: horizontal

## Stateless

Easy to horizontal:
- No state per instance
- Load balance
- Just add more

## Stateful

Hard to horizontal:
- DB sharding
- Cache cluster
- Sticky sessions

## Examples

### Web Server
Horizontal:
- Add servers
- ALB distributes

### DB
Initially vertical:
- m5.large → m5.4xlarge
Then horizontal:
- Sharding
- Read replicas

### Cache
Horizontal:
- Redis cluster

### Worker
Horizontal:
- More workers; queue pulls

## Auto-Scale

K8s HPA:
- Scale horizontal
- Based on metrics

## Cost

Horizontal usually cheaper:
- Commodity boxes
- Pay-as-you-grow
- No license per host

## Best Practices

- Stateless for horizontal
- DB shard when needed
- Auto-scale
- Right size first

## Common Mistakes

- Stateful in horizontal (state lost)
- Vertical past limits
- No auto-scale

## Quick Refs

```
Vertical: bigger box
Horizontal: more boxes

Stateless: horizontal easy
Stateful: complex

Combine in practice
```

## Interview Prep

**Mid**: "Scaling."

**Senior**: "When each."

**Staff**: "Scale architecture."

## Next Topic

→ [T02 — Sharding & Partitioning](T02-Sharding.md)
