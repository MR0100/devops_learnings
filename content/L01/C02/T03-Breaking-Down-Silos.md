# L01/C02/T03 — Breaking Down Silos

## Learning Objectives

- Explain why silos persist even when the org chart merges teams
- Apply Conway's Law (and the inverse maneuver) to predict architectural consequences of org structure
- Use Team Topologies as a toolkit for designing healthy collaboration
- Recognize the team anti-patterns that recreate the dev-vs-ops wall under a new name

## Why Silos Exist

The "dev vs ops wars" weren't caused by bad people. Silos are the *default* outcome of rational forces, which is why they re-form the moment you stop fighting them:

- **Specialization** — depth requires focus; a kernel expert and a React expert can't both be everything
- **Incentive misalignment** — dev is rewarded for shipping features, ops for stability; these directly conflict at the deploy boundary
- **Different time horizons** — a quarterly feature roadmap vs. a 99.95% annual uptime target
- **Tooling boundaries** — Jira for dev, ServiceNow for ops; the tools encode and reinforce the divide
- **Communication overhead** — coordination cost rises with team size (Dunbar's number caps a coherent group near ~150)
- **Conway's Law pressure** — the architecture itself ossifies the boundaries the org created

Merging two teams on paper changes none of the underlying forces. Without realigning incentives and interfaces, the silo simply re-forms inside the "unified" team.

## The Classic Dev-vs-Ops Wall

```
   DEV                              OPS
   "ship features fast"             "keep prod stable"
   rewarded for change       │      rewarded for no change
        │                    │              │
        ▼                    │              ▼
   throws build         ──►  WALL  ──►   catches build,
   over the wall             │           blamed for outages
                             │
   Result: change-averse ops, frustrated dev,
           slow lead time, blame on incidents.
```

Every DevOps practice in this chapter exists to dissolve this wall: shared on-call (shared incentive), IaC (shared tooling), blameless postmortems (shared learning), and "you build it, you run it" (shared ownership).

## Conway's Law

> Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure.
> — Melvin Conway, 1968

Practical implications:
- A 3-team org will tend to produce a 3-service architecture, with the team boundaries becoming the API boundaries
- A single monolithic team produces a monolith; a microservices org tends to produce microservices
- The interfaces between systems mirror the interfaces (and friction) between teams
- **Inverse Conway maneuver**: deliberately *restructure the org* to drive the architecture you want — if you want loosely-coupled services, build loosely-coupled, autonomous teams first

The corollary for DevOps: you cannot org-chart your way out of a coupling problem you've already shipped, but you can shape future architecture by shaping team boundaries now.

## Team Topologies (Skelton & Pais)

The modern toolkit for designing team boundaries on purpose. Four fundamental team types:

| Type | Purpose | Example | Cognitive load it manages |
|---|---|---|---|
| Stream-Aligned | Owns a product / value stream end-to-end | "Payments team" | Owns its full slice; minimized handoffs |
| Enabling | Coaches stream-aligned teams in new skills | "Cloud Migration team" | Temporary uplift, then exits |
| Complicated-Subsystem | Owns a specialist domain too deep to spread | "Fraud ML team" | Absorbs deep complexity for others |
| Platform | Provides an internal product / paved road | "Internal Developer Platform team" | Reduces others' load via self-service |

The unifying idea is **cognitive load**: a team can only own so much. Topologies exist to keep each stream-aligned team's load survivable.

Three interaction modes — the *only* sanctioned ways teams should interact:

- **Collaboration** — temporary, high-bandwidth, two teams working closely to discover something new (expensive; don't make it permanent)
- **X-as-a-Service** — one team consumes another's product with minimal coordination (low-bandwidth; the steady state for platforms)
- **Facilitating** — an enabling team helps another team get unblocked, then leaves

A healthy org makes most relationships X-as-a-Service, uses Collaboration deliberately and temporarily, and treats persistent high-bandwidth coupling as a smell.

## Anti-Patterns

| Anti-Pattern | Symptom | Why it recreates the silo |
|---|---|---|
| The "DevOps Team" | A new team sits between dev and ops | Just relabels Ops; the wall moves, it doesn't fall |
| Tools Team | Builds tools no one adopts | Reactive, ticket-driven, disconnected from users |
| Shared Services Team | Every team queues behind one team | Becomes the new bottleneck and blame target |
| "We're all one team" | No clear ownership of anything | Diffuse responsibility; incidents have no owner |
| Permanent Collaboration | Two teams always pairing | Hides a missing service boundary / unclear ownership |

## Practical Tactics

- **Cross-functional embedded engineers** — rotate an SRE into a product team for a quarter so empathy and skills cross the boundary
- **On-call rotations that include developers** — the single most effective wall-dissolver (see T05)
- **Shared dashboards and shared language** — same SLOs, same vocabulary, same source of truth
- **Inner-source** — let any team read, fork, and PR another's code instead of filing a ticket
- **Shared retrospectives** across team boundaries after cross-cutting incidents
- **Informal channels** — lunch rotations, guilds, internal tech talks reduce coordination friction below the formal-process threshold

## Common Mistakes

- **Renaming Ops to "DevOps"** — the highest-frequency anti-pattern; the wall just gets a new sign
- **Merging org charts without realigning incentives** — the silo re-forms inside the merged team within weeks
- **Making every relationship Collaboration** — high-bandwidth coupling everywhere is exhausting and hides missing service boundaries
- **Ignoring cognitive load** — piling ownership onto a stream-aligned team until it can't operate any of it well
- **Treating a platform team as a ticket queue** — reverts it to a Shared Services bottleneck

## Best Practices

- **Design team boundaries on purpose** using Team Topologies, then expect the architecture to follow (Conway)
- **Default to X-as-a-Service**; reserve Collaboration for genuine, time-boxed discovery
- **Use the inverse Conway maneuver** when you want a target architecture — change the org first
- **Align incentives across the old wall** — shared SLOs and shared on-call beat any reorg
- **Cap and measure cognitive load** — if a team owns more than it can reason about, split the stream or add a platform

## Quick Refs

```
Conway's Law: system structure mirrors org communication structure.
Inverse Conway: change the org to get the architecture you want.

Team Topologies — 4 types:
  Stream-Aligned · Enabling · Complicated-Subsystem · Platform
Interaction modes:
  Collaboration (temp, high-BW) · X-as-a-Service (steady) · Facilitating
Core constraint: team cognitive load.

Anti-pattern alarm: a "DevOps team" = Ops with a new logo.
```

## Interview Prep

**Junior**: "What's Conway's Law?"
- The principle that a system's architecture ends up mirroring the communication structure of the org that built it — three teams tend to produce three services with the team boundaries as the API boundaries.

**Mid**: "Why is creating a 'DevOps team' considered an anti-pattern?"
- Because it usually just relabels the old Ops team and inserts a new wall between dev and operations; the boundary and the handoff persist, which is exactly what DevOps is trying to dissolve.

**Senior**: "Our product team blames the platform team for slow deploys; the platform team says product isn't using the tools correctly. How do you fix this?"
- This is a collaboration-mode mismatch — I'd define a clear X-as-a-Service interface with documented SLAs, give the platform team OKRs tied to adoption and developer experience, and run a short, time-boxed collaboration to close the immediate gap before reverting to the low-bandwidth steady state.

**Staff**: "Design the team structure for a fintech startup at 50 engineers, projecting to 200."
- Start with stream-aligned teams around value streams (payments, onboarding, ledger), stand up a platform team early to cap their cognitive load, add a complicated-subsystem team for the genuinely deep domain (fraud/risk), use enabling teams to spread skills during the growth phase, and apply the inverse Conway maneuver so the service boundaries are designed before the org hits 200 and ossifies them.

## Next Topic

→ [T04 — Blameless Culture & Psychological Safety](T04-Blameless-Culture.md)
