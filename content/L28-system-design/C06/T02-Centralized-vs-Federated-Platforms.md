# L28/C06/T02 — Centralized vs Federated Platforms

## Learning Objectives

- Compare centralized, federated, and hybrid platform-team models
- Match the model to org size and stage
- Avoid the failure modes of both extremes (sprawl vs bottleneck)

## The Organizational Question

Once an org has more than a handful of teams, someone must decide *who owns the platform* — the shared infrastructure, tooling, and paved roads every product team depends on. The answer shapes consistency, velocity, and cost.

## The Three Models

### Centralized

One platform team owns the tooling; all product teams consume it.

- **+** Consistency across the org (one way to deploy, observe, secure)
- **+** Economies of scale; less duplicated effort
- **−** Less flexibility for domain-specific needs
- **−** The platform team can become a **bottleneck**

### Federated

Each domain (or large product group) has its own platform team with domain expertise.

- **+** Deep domain fit; teams move fast within their area
- **+** No central bottleneck
- **−** Less consistency; the same problem solved N different ways
- **−** Higher total cost (duplicated platform effort)

### Hybrid

A central core platform (shared paved road) plus domain-specific extensions.

- **+** Consistency where it matters, flexibility where it counts
- **+** The modern compromise most large orgs converge on
- **−** Requires clear boundaries (what's core vs what's extensible)

## Matching Model to Org Size

| Org size | Recommended model | Rationale |
|---|---|---|
| Small (< 100 eng) | **Centralized** | One team can serve everyone; consistency is cheap |
| Mid (100–500 eng) | **Hybrid** | Central core + domain extensions balances both |
| Large (1000+ eng) | **Federated** (with a thin shared core) | Domains need autonomy; a single team can't keep up |

The transitions aren't sharp — they track coordination cost. When the central team becomes the thing everyone waits on, it's time to federate the parts that are slowing teams down.

## The Paved Road Pattern

The dominant modern approach (Netflix, Spotify, etc.): the platform team provides a **paved road** — a well-supported, opinionated default path (golden CI/CD pipeline, standard observability, blessed deployment).

- Teams that take the paved road get support, upgrades, and guardrails for free.
- Teams with genuine reason to deviate **can** leave the road — but then they own the operational burden.

This keeps consistency high without mandating it by decree, and it scales the central team's leverage (build once, many consume).

## Failure Modes

### Over-Centralized

- Platform team is a bottleneck; every team waits on tickets
- Product velocity drops; teams route around the platform (shadow IT)
- The platform doesn't fit domain needs, so adoption stalls

### Over-Federated

- Tool sprawl (see T03) — every domain picks its own everything
- New engineers re-learn the stack on every team move
- Duplicated effort; higher cost; inconsistent security posture

## Common Mistakes

- Forcing a centralized model onto a 1000+ engineer org (instant bottleneck)
- Federating a 50-person startup (premature, wasteful duplication)
- Mandating the paved road with no escape hatch (teams revolt or route around it)
- No clear ownership boundary in a hybrid model (core vs extension is fuzzy)
- Treating the org model as permanent rather than re-evaluating as you grow

## Best Practices

- Pick the model that fits your **current** size and revisit it as you scale
- Prefer the paved-road pattern: opinionated defaults, optional deviation with owned cost
- In hybrid, draw an explicit line between the shared core and domain extensions
- Measure platform-team lead time; a rising queue is the signal to federate
- Graduate successful domain experiments into the central core over time

## Quick Refs

```
Centralized → one platform team, max consistency, bottleneck risk
Federated   → per-domain teams, max autonomy, sprawl + cost risk
Hybrid      → central core + domain extensions (modern default)

Small org   → centralized
100–500     → hybrid
1000+       → federated (thin shared core)

Paved road  → supported default path; deviate but own the cost
```

## Interview Prep

**Junior**: "Centralized vs federated platform teams — what's the difference?" — Centralized is one shared platform team; federated gives each domain its own.

**Mid**: "Which would you pick for a 1000-engineer company?" — Federated with a thin shared core; one central team can't keep up at that scale without becoming a bottleneck.

**Senior**: "What's the paved-road pattern and why does it work?" — An opinionated, well-supported default path that teams get rewarded for taking; deviation is allowed but the deviating team owns the operational cost — consistency without mandate.

**Staff**: "How do you evolve platform org structure as a company grows from 50 to 2000 engineers?" — Start centralized, shift to hybrid (core + extensions) around mid-size, federate the slow parts as the central team's lead time rises, keep a thin shared core for security/observability/deploy standards, and use the paved road to scale leverage throughout.

## Next Topic

→ [T03 — Tool Sprawl Management](T03-Tool-Sprawl-Management.md)
