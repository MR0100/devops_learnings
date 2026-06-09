# L28/C06 — Tradeoff Discussions

## Topics

- **T01 Build vs Buy vs Open Source** — Sourcing decisions
- **T02 Centralized vs Federated Platforms** — Organizational
- **T03 Tool Sprawl Management** — Consolidation

## Build vs Buy vs Open Source

A constant decision for staff engineers.

### Build (In-House)
**Pros**:
- Full control
- Tailored to needs
- No license cost
- IP ownership

**Cons**:
- Initial cost
- Ongoing maintenance
- Talent risk (who maintains?)
- Slower time-to-market

**When**:
- Differentiation (core product)
- Specific needs no vendor addresses
- Strategic capability

### Buy (Commercial)
**Pros**:
- Fast adoption
- Vendor maintenance + support
- Documented + supported
- Predictable cost

**Cons**:
- License cost ($)
- Vendor lock-in
- Less flexibility
- Vendor risk (acquisition, sunset)

**When**:
- Non-differentiating ("table stakes")
- Mature problem area
- Vendor + product align with strategy

### Open Source
**Pros**:
- Free license
- Source available
- Community support
- Can customize

**Cons**:
- Self-operate (significant cost!)
- "Free as in puppy"
- Quality varies
- May go commercial

**When**:
- Industry-standard tools (K8s, Postgres, Prometheus)
- Team has expertise to operate
- Customization required

### Total Cost
Don't forget hidden costs:
- Build: dev time + maintenance + opportunity cost
- Buy: license + integration + dep on vendor
- OSS: ops effort + integration + risk

A "free" OSS often costs more in ops than a paid vendor.

## Real-World Examples

### CI/CD
- Build (Buck-style monorepo CI at Meta): $$$$ but matches scale
- Buy (CircleCI, Buildkite): simple ops, decent cost
- OSS (Jenkins, GitHub Actions self-hosted): cost-effective, ops effort

### Observability
- Build: rare; only at hyperscaler
- Buy: Datadog $$$$, but huge feature set
- OSS: Prometheus + Loki + Tempo + Grafana, ops effort but mature

### Database
- Build: extremely rare (Spanner, Aurora are essentially Google/AWS in-house)
- Buy: Snowflake, MongoDB Atlas, Aurora
- OSS: Postgres, MySQL self-managed

### Service Mesh
- Build: only at huge scale
- Buy: Tetrate (managed Istio), HashiCorp Consul Enterprise
- OSS: Istio, Linkerd, Consul OSS

## Centralized vs Federated Platforms

### Centralized
- One platform team
- All teams use central tools
- Consistency
- Less flexibility

### Federated
- Per-domain platform teams
- Domain expertise
- Less consistency
- More cost

### Hybrid
- Central core (shared)
- Domain-specific extensions
- Modern compromise

### When
- Small org → centralized
- Large org (1000+ engineers) → federated
- 100-500 → hybrid

## Tool Sprawl

Symptoms:
- 3 different log aggregators
- 5 different deployment tools
- 4 secret managers
- Each acquired team brought tools

### Pain
- Engineers re-learn per team
- Inconsistent practices
- More dependencies (more incidents)
- Cost (multiple licenses)

### Consolidation
- Inventory tools
- Categorize (essential vs duplicate)
- Pick standard per category
- Migration plan
- Sunset old tools

Don't underestimate cost: 6 months to 2 years for consolidation.

## Vendor Lock-In

Real but often overstated. Categories:
- **Hard lock-in**: managed services (DynamoDB, BigQuery, Spanner)
- **Soft lock-in**: open standards but configured (K8s, Kafka)
- **Negligible**: VMs, blob storage

Avoid lock-in by:
- Use standards (OCI, OpenTelemetry)
- Abstract per-vendor (data access layer)
- Pay for portability where strategic

But don't over-rotate: trying to "avoid lock-in" with bespoke abstractions adds enormous cost.

## Standardization vs Innovation

### Risks of Over-Standardization
- Innovation stifled
- New patterns hard to introduce
- Senior engineers leave
- Org calcifies

### Risks of Under-Standardization
- Tool sprawl
- Inconsistency
- New engineers paralyzed
- Junior teams struggle

### Balance
- Standardize foundations (deploy, observability, security)
- Innovate at boundaries (per-team experiments)
- Graduate successful experiments to standard

## Build/Buy Decision Framework

For each capability, ask:
1. Is this core to our competitive advantage? (build)
2. Does a vendor solve this for less than build cost? (buy)
3. Is there a mature OSS solution? (OSS if we can operate)
4. Do we have the team to maintain (build or OSS)?
5. What's the total cost (TCO) over 3 years?

## Tooling Inventory Cadence

Annual:
- What tools do we have?
- What do they cost?
- Who uses them?
- What's overlapping?
- What's stale?

Output: keep / consolidate / sunset decisions.

## Communicate Decisions

For each tool consolidation:
- Decision document (why)
- Migration plan
- Owner
- Timeline
- Sunset announcement

Don't surprise teams; bring them along.

## Anti-Patterns

- **Build everything** — burnout team; reinvent wheels
- **Buy everything** — high cost; less ownership
- **Each team picks** — sprawl
- **Top-down only** — bottom-up wisdom lost
- **Reorgs every year** — never get to value
- **No deprecation policy** — old tools never die

## Interview Themes

- "Build vs buy decision for X"
- "Tool sprawl — how consolidate?"
- "Vendor lock-in — when worth it?"
- "Centralized vs federated platform org"
- "Standardize without stifling innovation"
