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

**Junior**: "What's the difference between horizontal and vertical scaling?" — Vertical is a bigger box (more CPU/RAM); horizontal is more boxes sharing the load. Vertical is simpler with no code changes but hits a hard ceiling and is a single point of failure; horizontal scales nearly without limit and gives HA, at the cost of distributed-systems complexity.

**Mid**: "When would you pick vertical?" — For stateful systems that are hard to distribute (a primary database), when you need a quick fix, or when licensing is per-host. The usual pattern is vertical first (m5.large → m5.4xlarge) because it's cheap effort, then horizontal (read replicas, then sharding) once you hit the instance ceiling.

**Senior**: "Why is the stateless/stateful distinction the crux of scaling?" — Stateless services scale horizontally trivially — put a load balancer in front and add instances, no coordination. State is what's hard: it forces sharding, replication, sticky sessions, or a distributed cache, all of which add consistency and failover complexity. So the first design move is to push state out of the app tier (into a DB/cache/session store) so the compute tier stays cheaply horizontal.

**Staff**: "Design the scaling strategy for a typical web system end to end." — Stateless web/API tier horizontal behind an LB with HPA on CPU/RPS; cache as a horizontal cluster (Redis); database vertical first then horizontal via read replicas for read scaling and sharding for write scaling; workers horizontal pulling from a queue (which also gives backpressure). The principle is to combine both axes per tier — vertical where state makes horizontal expensive, horizontal everywhere it's cheap — and to right-size before scaling out so you're not paying for idle capacity.

## Next Topic

→ [T02 — Sharding & Partitioning](T02-Sharding.md)
