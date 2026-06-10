# L19/C09/T01 — SRE Org Structures (Embedded vs Central)

## Learning Objectives

- Understand SRE org models
- Pick right structure

## Models

### Embedded
SRE in product team.

### Central
Single SRE team owns shared platform.

### Hybrid
Both.

## Embedded SRE

```
Product Team A
├─ 5 devs
└─ 1 SRE

Product Team B
├─ 5 devs
└─ 1 SRE
```

Pros:
- Close to product
- Deep context
- Tight integration

Cons:
- Dispersed
- SRE community weak
- Can drift to operations
- Knowledge silos

## Central SRE

```
Platform SRE Team (10)
   ↓ provides infra
Many product teams self-serve
```

Pros:
- Strong SRE community
- Reusable platform
- Standards
- Specialized

Cons:
- Distance from product
- Bottleneck
- Less context

## Hybrid

```
Central SRE (5): platform + standards
Embedded SRE (1 per team): product-specific

Both coordinate.
```

For: balance.

## When Embedded

- Mature product
- Specialized needs
- Tight integration

## When Central

- Many small products
- Want consistency
- Platform-heavy

## When Hybrid

- Large org
- Some products need depth
- Some can self-serve

## Reporting

### Embedded
Reports to product manager.

Risk: ops-heavy; eng work drops.

### Central
Reports to SRE leadership.

Pure SRE identity.

### Hybrid
Embedded: dotted line to product, solid to SRE leadership.

For: maintain SRE identity.

## Platform SRE

Central platform:
- K8s
- Monitoring
- CI/CD
- Database operations
- Security tooling

Product teams build on platform.

## Self-Service Tools

Central SRE provides:
- Service templates
- Monitoring SDK
- Deploy pipelines

Product teams: use.

For: scale.

## SRE Per Service

Some orgs:
- 1 SRE per 5-10 devs

Cap engineering load.

## Maturity

Org maturity:
- Start: central, do everything
- Grow: embed for critical
- Scale: hybrid

## Common Anti-Patterns

### Central All
Bottleneck; can't scale.

### Embedded Only
No standards; reinvention.

### SRE = Ops
SREs only paged; no engineering.

### SRE = Janitor
Cleanup work only.

For: real SRE = engineering + ops.

## SRE Headcount

Rough:
- 1 SRE per 10-20 devs (mature)
- 1 SRE per 5-10 (intensive)

## SRE Skills

- Software engineering
- Operations
- System design
- Performance
- Resilience

For: hire engineers, train ops.

## Reporting Structure

```
CTO
├─ VP Eng (product)
│  ├─ Team A (5 devs + 1 SRE)
│  └─ Team B (5 devs + 1 SRE)
└─ VP SRE
   ├─ Platform SRE (10)
   └─ Embedded SREs (dotted line)
```

For: identity + work integration.

## Career Path

SRE careers:
- IC: engineer → senior → staff → principal
- Manager: SRE lead → senior manager → director → VP

## Compensation

SRE often paid equal to dev.

Reflects engineering nature.

## Real Examples

### Google
Central + embedded.

### Netflix
Mostly central platform.

### Many startups
SRE = DevOps; ops + engineering.

### FAANGM
Multiple models; central + embedded common.

## Best Practices

- Pick model deliberately
- Hybrid for scale
- SRE identity preserved
- Career paths
- Compensation parity
- Toil cap enforced

## Common Mistakes

- SRE = on-call slaves
- No engineering time
- No platform investment
- Pure central (bottleneck)

## Decision Factors

- Org size
- Product count
- Maturity
- Skills available
- Culture

## Quick Refs

```
Embedded: in product team
Central:  shared platform
Hybrid:   both

Healthy SRE:
- Engineering > 50%
- Compensation parity
- Career path
- Identity
```

## Interview Prep

**Mid**: "SRE org models."

**Senior**: "Pick model."

**Staff**: "Org design."

## Next Topic

→ [T02 — Influence Without Authority](T02-Influence-Without-Authority.md)
