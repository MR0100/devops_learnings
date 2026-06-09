# L01/C06/T02 — The Anti-Pattern of a "DevOps Team"

## Learning Objectives

- Recognize the failure mode in detail
- Understand why it happens repeatedly
- Propose alternative structures

## The Pattern

1. Leadership reads about DevOps
2. Forms a "DevOps team" to drive adoption
3. Maps responsibilities: dev codes, DevOps team deploys
4. Two years later: same problems as before, with a new label

## Why It Happens

- Easy org chart change (rename "Ops")
- Looks like progress to executives
- Doesn't require dev teams to change behavior
- Avoids the harder conversations about incentives

## What the Reality Looks Like

```
   Before:                   After:
   ┌─────┐  ┌────┐          ┌─────┐  ┌────────┐
   │ Dev │→ │Ops │          │ Dev │→ │ DevOps │
   └─────┘  └────┘          └─────┘  └────────┘
            ▲                          ▲
            handoff                   handoff (same problem)
```

Nothing about the workflow changed; only the label.

## When This Anti-Pattern *Is* OK

Briefly, in transitional periods:

- A platform team is being seeded out of former ops engineers
- The "DevOps team" has a clear sunset plan or product-team model
- The team is *explicitly* a platform team, not a service desk

But these are exceptions, not the rule.

## Healthy Alternatives

### Pattern 1: Embedded SRE / DevOps in Product Teams
- 1 SRE per 5–6 product engineers
- Product team owns deploy; SRE coaches and consults

### Pattern 2: Platform Team
- Builds an internal platform product
- Product teams consume the platform
- No handoffs for routine work

### Pattern 3: Hybrid (Most Common)
- Platform team for foundational concerns
- Embedded SREs for highest-traffic services
- Product teams own deploy for everything else

## Conversion Plan

If you inherit a DevOps-team anti-pattern:

1. **Audit** — what does the team actually do? Categorize as platform work vs ticket work
2. **Communicate** — talk to dev teams. What pain do they have? What would they self-serve if they could?
3. **Pilot** — pick one product team. Have them own deploy. Pair with a DevOps engineer.
4. **Productize** — turn the pilot's reusable parts into platform offerings
5. **Scale** — over 2–4 quarters, dissolve the "DevOps team" into platform team + embedded SREs
6. **Measure** — DORA improves; on-call burden tracked

## Pitfalls in Conversion

- Skipping the pilot — devs will reject overnight changes
- Underestimating the cultural work — devs may resist on-call
- Letting the platform team revert to ticket-driven — needs strong PM-style ownership
- Losing the operational expertise — keep DevOps engineers; don't fire them, redeploy them

## Interview Prep

**Senior**: "Why is a 'DevOps team' often an anti-pattern?"
- Recreates the silo. Devs still hand off. Bottleneck moved, not removed.

**Staff**: "You inherit a DevOps team that's a service desk. Walk me through 6 months of transformation."

**Principal**: "Defend or reject: every company at 50+ engineers needs a Platform team."

## Next Topic

→ [T03 — The NoOps Myth](T03-NoOps-Myth.md)
