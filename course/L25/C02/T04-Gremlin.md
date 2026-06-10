# L25/C02/T04 — Gremlin

## Learning Objectives

- Use Gremlin
- Commercial chaos

## Gremlin

Commercial SaaS:
- UI-driven
- Many fault types
- Targeting (host, container, K8s)
- Reliability scoring

## Pros

- Easy onboarding
- Templates
- Support
- Multi-cloud

## Cons

- Cost ($$$)
- Vendor lock
- Less flexibility

## Faults

- Resource (CPU, memory, disk)
- State (process kill, reboot)
- Network (latency, loss, blackhole)
- Time (clock skew)

## Setup

```bash
# Install agent
curl -L https://gremlin.com/install | sh
```

## Attack via UI

Pick:
- Target
- Attack type
- Duration

Click run.

## Templates

- "Region failover"
- "DB primary down"
- "Cache evict"

For: quick start.

## Reliability Score

Gremlin scores resilience.

For: track improvement.

## Best Practices

- Use for guided
- Templates first
- Custom for specifics

## When Gremlin

- Want managed
- Budget OK
- Cross-platform

## When OSS

- Cost-sensitive
- K8s only (Chaos Mesh / Litmus)
- Want flexibility

## Quick Refs

```bash
gremlin attack ...
gremlin halt
```

## Interview Prep

**Mid**: "What's Gremlin."

**Senior**: "OSS vs Gremlin."

## Next Topic

→ [T05 — AWS Fault Injection Simulator (FIS)](T05-AWS-FIS.md)
