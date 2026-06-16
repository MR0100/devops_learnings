# L01/C06/T02 — The Anti-Pattern of a "DevOps Team"

## Learning Objectives

- Recognize the "DevOps team" silo failure mode in detail and explain why it recurs across orgs
- Distinguish the genuinely harmful version from the legitimate transitional and platform versions
- Map the anti-pattern onto the Team Topologies vocabulary and choose a healthier structure
- Run a concrete, staged conversion plan and anticipate where conversions stall

## Prerequisites

The three category errors from T01 — this topic zooms into Error 2. Familiarity with *Team Topologies* (Skelton & Pais) and the embedded-SRE / platform-team ideas from C04/T03 helps.

## The Pattern

It plays out almost identically everywhere:

1. Leadership reads about DevOps (a book, a conference, a competitor's blog post)
2. Forms a "DevOps team" to *drive adoption* — usually by renaming the existing Ops/Infra team
3. Divides responsibility along the old fault line: **dev writes code, the DevOps team deploys and operates it**
4. Two years later: the same handoff delays, the same blame, the same incidents — now with a more modern label

The seductive part is step 2: it requires no product team to change behavior, no on-call to be redistributed, and no hard conversation about incentives. It *looks* like a transformation while being an org-chart edit.

## Why It Happens (Repeatedly)

- **It's the easiest possible change** — rename a box; no workflows touched
- **It signals progress to executives** — there is now visibly "a DevOps team," which reads as commitment
- **It avoids the painful conversations** — product engineers don't have to carry pagers or own production
- **It preserves the existing power structure** — Ops keeps its turf, just with a fresher name
- **Conway's Law works against you** — a separate deploy team *guarantees* a deploy handoff in the architecture and the workflow; the silo reproduces itself in the system

## What the Reality Looks Like

```
   Before:                   After:
   ┌─────┐  ┌────┐          ┌─────┐  ┌────────┐
   │ Dev │→ │Ops │          │ Dev │→ │ DevOps │
   └─────┘  └────┘          └─────┘  └────────┘
            ▲                          ▲
            handoff                   handoff (same problem)
```

Nothing about the *flow of work* changed; only the label on the second box. The wall is repainted, not removed. Lead time, deploy frequency, and MTTR stay flat because the structural cause — a mandatory handoff between the people who write software and the people who run it — is exactly preserved.

## When This Pattern *Is* OK

The label "DevOps team" is not automatically fatal. It's healthy when it's genuinely one of these, with a clear charter:

- **A seeded platform team** — former ops engineers building a self-service product, not a deploy service desk
- **A transitional bridge** — explicitly time-boxed, with a sunset plan and a product-team end-state
- **An enabling team** (Team Topologies sense) — coaches that *temporarily* embed to upskill a product team, then leave

The smell test: if the team's job is to make product teams **more self-sufficient**, it's fine. If its job is to **deploy on behalf of** product teams indefinitely, it's the anti-pattern. The difference is direction of ownership, not the name on the door.

## Healthy Alternatives

### Pattern 1: Embedded SRE / DevOps in Product Teams
- Roughly 1 SRE per 5–6 product engineers, sitting *inside* the product team
- The product team owns its own deploy; the embedded SRE coaches, consults, and raises the reliability bar
- Best for high-traffic, high-stakes services that need deep reliability attention

### Pattern 2: Platform Team
- Builds and runs an **internal developer platform** as a product (golden paths, self-service env, observability baked in)
- Product teams *consume* the platform with no ticket and no handoff for routine work
- Best when duplication pain across many teams justifies a paved road (see C04/T03)

### Pattern 3: Hybrid (Most Common at Scale)
- A platform team for foundational concerns shared by everyone
- Embedded SREs for the few highest-traffic / highest-risk services
- Product teams own deploy for everything else, on the paved road

| Structure | Who deploys | Handoff for routine work? | Best when |
|---|---|---|---|
| "DevOps team" silo (anti-pattern) | The central team | Yes — every deploy | Never (steady state) |
| Embedded SRE | The product team | No | Few critical, high-traffic services |
| Platform team | The product team (self-service) | No | Broad duplication across many teams |
| Hybrid | Mostly product teams | No | 100+ engineers, mixed risk profile |

## Conversion Plan

If you inherit a "DevOps team" anti-pattern, do **not** flip everyone overnight — sequence it:

1. **Audit** — catalog what the team actually does. Tag each activity as *platform work* (reusable, productizable) vs *ticket work* (one-off requests that should become self-service)
2. **Communicate** — interview product teams. Where does it hurt? What would they self-serve today if they could? You're hunting for the highest-pain, highest-frequency request to automate first
3. **Pilot** — pick one willing product team. Have them own their deploy end to end, paired with a DevOps/platform engineer who builds the paved road alongside them
4. **Productize** — turn the pilot's reusable pieces (the pipeline template, the env-provisioning flow) into platform offerings other teams can adopt
5. **Scale** — over 2–4 quarters, dissolve the central "DevOps team" into a platform team plus embedded SREs; the central team stops *doing* deploys and starts *enabling* them
6. **Measure** — DORA metrics improve, and on-call burden is tracked and distributed rather than concentrated

## Pitfalls in Conversion

- **Skipping the pilot** — a big-bang reorg gets rejected; product teams need to *experience* self-service before they trust it
- **Underestimating the cultural work** — many product engineers will resist carrying a pager; this is a months-long change with leadership air cover, not a memo
- **Letting the platform team revert to a ticket queue** — without strong product/PM-style ownership, the new platform team quietly becomes the old service desk under a new name
- **Losing the operational expertise** — do *not* fire the DevOps engineers; their hard-won production knowledge is the asset. Redeploy them into platform and embedded roles
- **Mandating the platform before it's good** — forcing teams onto a half-built paved road breeds resentment; win adoption by being better than what they have

## Common Mistakes

- **Renaming "Ops" to "DevOps" and declaring victory** — the textbook version of the error
- **Believing the org chart is the work** — the chart changed; the flow of work didn't
- **Centralizing deploy "for safety"** — the central team becomes the single bottleneck *and* the single point of failure
- **Confusing a platform team with a deploy team** — one builds self-service; the other does the deploys; only the first scales
- **Sunsetting nothing** — a "transitional" DevOps team with no sunset plan is just the permanent anti-pattern wearing a disguise

## Best Practices

- **Direction over label** — measure whether the team makes product teams *more* or *less* self-sufficient; that's the whole diagnosis
- **Productize, don't service** — turn repeated requests into self-service paved roads, not faster ticket turnaround
- **Pilot, prove, then scale** — let one team's success sell the model to the rest
- **Keep the experts, change their charter** — redeploy ops talent into platform and embedded SRE roles
- **Track on-call distribution** — a healthy conversion spreads operational ownership; a failed one re-concentrates it

## Quick Refs

```text
Silo smell test:
  Does the team DEPLOY for product teams?      → anti-pattern (service desk)
  Does the team ENABLE product teams to deploy?→ healthy (platform/enabling)

Conversion order (never big-bang):
  Audit → Communicate → Pilot (1 team) → Productize → Scale → Measure

Team Topologies map:
  "DevOps team" silo   → no such healthy type; it's a mis-shaped complicated-subsystem/ops team
  Platform team        → "platform" interaction mode: X-as-a-Service
  Embedded SRE         → "enabling"/"stream-aligned" collaboration
```

Mnemonic: **A DevOps team that *deploys for you* is the old wall repainted; a platform team that *lets you deploy* is the wall removed.**

## Interview Prep

**Junior**: "Why is a separate 'DevOps team' often a problem?"
- Because it usually just renames the old Ops team and keeps the handoff — devs still throw code over a wall to be deployed, so the bottleneck moves instead of disappearing.

**Mid**: "When is a 'DevOps team' actually fine?"
- When it's a genuine platform or enabling team whose charter is to make product teams more self-sufficient — building a self-service paved road or temporarily coaching a team — rather than deploying on their behalf forever; the tell is the direction of ownership, not the name.

**Senior**: "Why is a 'DevOps team' often an anti-pattern, in one sentence?"
- It recreates the Dev↔Ops silo: developers still hand off, deploys still queue behind one team, so the bottleneck is moved, not removed — and Conway's Law bakes that handoff into the architecture.

**Staff**: "You inherit a DevOps team that's really a deploy service desk. Walk me through six months of transformation."
- Month 1: audit what they do (platform vs ticket work) and interview product teams for the highest-pain request; months 2–3: pilot self-service deploy with one willing team, paired to a platform engineer, and productize the reusable pieces; months 4–6: scale the paved road to more teams, redeploy the ops experts into platform/embedded roles rather than firing them, and dissolve the central deploy function while tracking DORA and on-call distribution to prove the silo actually dissolved instead of getting renamed again.

**Principal**: "Defend or reject: every company at 50+ engineers needs a platform team."
- Reject the absolute, accept the tendency — a dedicated platform team pays off only once duplication pain across teams exceeds the cost of staffing it, which is *often* true near 50–100 engineers but depends on architecture, cloud-native maturity, and how much self-service already exists; the right question isn't "do we need one" but "is the per-team cost of operational knowledge high enough that paying it once is cheaper than paying it N times."

## Next Topic

→ [T03 — The NoOps Myth](T03-NoOps-Myth.md)
