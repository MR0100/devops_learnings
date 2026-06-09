# L01/C02/T03 — Breaking Down Silos

## Learning Objectives

- Understand why silos persist even when org charts unify teams
- Apply Conway's Law to predict architectural consequences of org structure
- Use Team Topologies as a toolkit for designing healthy collaboration

## Why Silos Exist

Silos aren't created by malice; they're created by:

- **Specialization** — depth requires focus
- **Incentive misalignment** — dev rewarded for features, ops for stability
- **Different time horizons** — feature roadmap vs uptime targets
- **Tooling boundaries** — JIRA for dev, ServiceNow for ops
- **Communication overhead** — Dunbar's number limits

## Conway's Law

> Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure.
> — Melvin Conway, 1968

Practical implications:
- A 3-team org will likely produce a 3-service architecture
- A monolithic team produces a monolith; microservices org → microservices
- *Inverse Conway maneuver*: change org to drive architecture

## Team Topologies (Skelton & Pais)

Four team types:

| Type | Purpose | Example |
|---|---|---|
| Stream-Aligned | Owns a product/value stream | "Payments team" |
| Enabling | Coaches stream-aligned teams in new skills | "Cloud Migration team" |
| Complicated Subsystem | Owns specialist domain | "Fraud ML team" |
| Platform | Provides internal product | "Internal Developer Platform team" |

Three interaction modes:

- **Collaboration** — temporary, high-bandwidth
- **X-as-a-Service** — consume product, low-bandwidth
- **Facilitating** — enabling team helps stream-aligned team

## Anti-Patterns

| Anti-Pattern | Symptom |
|---|---|
| DevOps Team | Recreates the dev-ops silo |
| Tools Team | Tool sprawl, low adoption |
| Shared Services Team | Bottleneck, queue-driven |
| "We're all one team" | Diffuse responsibility, no ownership |

## Practical Tactics

- **Cross-functional embedded engineers** (SRE in product team for a quarter)
- **On-call rotations that include devs**
- **Shared dashboards & language** (same SLOs, same vocabulary)
- **Lunch rotations** and informal communication channels
- **Shared retrospectives** across team boundaries

## Interview Prep

**Mid**: "What's Conway's Law?"

**Senior**: "Our product team blames the platform team for slow deploys; the platform team says product isn't using the tools correctly. How do you fix this?"
- Diagnose: collaboration mode mismatch. Define X-as-a-Service interface, set SLAs, create platform OKRs around adoption and DX.

**Staff**: "Design the team structure for a fintech startup at 50 engineers, projecting to 200."

## Next Topic

→ [T04 — Blameless Culture & Psychological Safety](T04-Blameless-Culture.md)
