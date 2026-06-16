# L28/C06/T01 — Build vs Buy vs Open Source

## Learning Objectives

- Apply a structured framework to build / buy / open-source decisions
- Reason about total cost of ownership, not just license price
- Map the decision to real platform categories (CI/CD, observability, databases, mesh)

## The Constant Staff-Engineer Decision

For every capability — CI/CD, observability, secrets, databases — a staff engineer repeatedly answers: do we **build** it, **buy** it, or run **open source**? There is no universal answer; there is a framework.

## The Three Options

### Build (In-House)

| Pros | Cons |
|---|---|
| Full control | High initial cost |
| Tailored to exact needs | Ongoing maintenance forever |
| No license cost | Talent risk — who maintains it? |
| IP ownership | Slower time-to-market |

**Choose when**: it's a core differentiator, no vendor addresses your specific need, or it's a strategic capability.

### Buy (Commercial)

| Pros | Cons |
|---|---|
| Fast adoption | License cost ($$$) |
| Vendor maintenance + support | Vendor lock-in |
| Documented + supported | Less flexibility |
| Predictable cost | Vendor risk (acquisition, sunset) |

**Choose when**: the capability is "table stakes" (non-differentiating), the problem is mature, and a vendor aligns with your strategy.

### Open Source

| Pros | Cons |
|---|---|
| Free license | You self-operate (significant cost!) |
| Source available | "Free as in puppy" |
| Community support | Quality varies |
| Customizable | Project may go commercial / abandoned |

**Choose when**: there's an industry-standard tool (Kubernetes, Postgres, Prometheus), your team can operate it, and you need customization.

## Total Cost of Ownership

The single most important reframe: **license price is not the cost.**

```
Build TCO = dev time + perpetual maintenance + opportunity cost
Buy   TCO = license + integration + dependency on vendor roadmap
OSS   TCO = ops effort + integration + operational risk
```

A "free" OSS tool often costs **more** than a paid vendor once you count the engineers operating it. Self-hosting Prometheus + Loki + Tempo + Grafana is free to license and very much not free to run at scale.

## Real-World Examples

| Category | Build | Buy | OSS |
|---|---|---|---|
| **CI/CD** | Monorepo CI at Meta scale ($$$$, matches scale) | CircleCI, Buildkite (simple ops) | Jenkins, self-hosted GitHub Actions (cheap, ops effort) |
| **Observability** | Rare — only at hyperscalers | Datadog ($$$$, huge feature set) | Prometheus + Loki + Tempo + Grafana (mature, ops effort) |
| **Database** | Extremely rare (Spanner/Aurora *are* in-house) | Snowflake, MongoDB Atlas, Aurora | Postgres, MySQL self-managed |
| **Service Mesh** | Only at huge scale | Tetrate (managed Istio), Consul Enterprise | Istio, Linkerd, Consul OSS |

The pattern: build only where you have hyperscaler-grade scale or genuine differentiation; otherwise buy the table stakes and run OSS where the tool is an industry standard and you have the team.

## The Decision Framework

For each capability, ask in order:

1. Is this **core to our competitive advantage**? → lean **build**
2. Does a vendor solve this for **less than build cost**? → lean **buy**
3. Is there a **mature OSS** solution? → lean **OSS** *if we can operate it*
4. Do we have the **team to maintain** it (build or OSS)?
5. What's the **3-year TCO** of each path?

If you can't staff the operation of an OSS tool, "free" OSS is the most expensive option — choose buy.

## Common Mistakes

- Comparing license cost instead of TCO (ignoring ops headcount for OSS)
- Building non-differentiating table-stakes tooling ("not invented here")
- Buying for a core differentiator and losing strategic control
- Adopting OSS with no team able to operate it at 3 a.m.
- Ignoring vendor risk (acquisition, price hikes, product sunset)

## Best Practices

- Decide on TCO over a 3-year horizon, not sticker price
- Build only where it's a genuine differentiator or no vendor fits
- Buy the mature, non-differentiating problems and spend your engineers elsewhere
- Run OSS where it's an industry standard *and* you can staff the operation
- Write the decision down (a short ADR) so the reasoning survives re-litigation

## Quick Refs

```
Build → differentiator, no vendor fit, strategic, can maintain
Buy   → table stakes, mature problem, vendor aligns, predictable cost
OSS   → industry standard, customization needed, team can operate

TCO(Build) = dev + maintenance + opportunity cost
TCO(Buy)   = license + integration + vendor dependency
TCO(OSS)   = ops effort + integration + risk
```

## Interview Prep

**Junior**: "What are the three sourcing options?" — Build in-house, buy a commercial product, or adopt open source.

**Mid**: "When would you build instead of buy?" — When the capability is a core differentiator, no vendor meets the need, and you have the team to maintain it.

**Senior**: "Why is 'free' open source often the most expensive option?" — License is free but you carry the full operational cost; at scale the ops headcount can exceed a vendor's price — that's TCO, not sticker price.

**Staff**: "Walk me through a build/buy/OSS decision for observability at a 300-engineer company." — Observability is table stakes, not a differentiator, so don't build; compare Datadog's license + data-gravity lock-in against the ops cost of self-hosting the Grafana stack over 3 years; factor team maturity, on-call burden, and exit cost; document the call as an ADR.

## Next Topic

→ [T02 — Centralized vs Federated Platforms](T02-Centralized-vs-Federated-Platforms.md)
