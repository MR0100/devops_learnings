# L01/C01/T04 — DevOps vs Agile vs SRE vs Platform Engineering

## Learning Objectives

- Differentiate four overlapping concepts by their origin, focus, and primary artifact
- Use a side-by-side matrix to answer FAANGM-style "what's the difference" questions crisply
- Recognize that these are complementary layers, not competing alternatives
- Diagnose which one your org actually needs next, and defend the choice

## Prerequisites

The history that produced these four (L01/C01/T02) and a culture-first definition of DevOps (L01/C01/T01).

## Quick Definitions

| Term | Origin | Primary Focus | Primary Artifact |
|---|---|---|---|
| **Agile** | 2001 (Snowbird) | Iterative software development | Working software each sprint |
| **DevOps** | 2009 (Debois) | End-to-end software delivery | Continuous delivery pipeline |
| **SRE** | 2003 (Google) | Reliability as engineering | Error budget + SLO |
| **Platform Engineering** | 2019+ (Team Topologies) | Cognitive load reduction | Internal Developer Platform |

One-line mental model: **Agile** is how you decide *what* to build, **DevOps** is how you *deliver* it, **SRE** is how you keep it *reliable*, **Platform Engineering** is how you make all of that *reusable* across many teams.

## The Matrix

| Dimension | Agile | DevOps | SRE | Platform Engineering |
|---|---|---|---|---|
| Primary problem | Slow, inflexible development | Wall between dev and ops | Operating at scale | Cognitive load on product teams |
| Cultural emphasis | Customer collaboration, change | Shared ownership | Embracing risk, blameless | Internal tools as products |
| Org structure | Cross-functional product teams | Cross-functional product teams | SRE teams embedded or central | Platform team + stream-aligned teams |
| Key metric | Velocity, working software | DORA (DF, LT, MTTR, CFR) | SLI / SLO / error budget | DX, platform adoption |
| Who's hired | Software engineers | Dev + Ops (later, the same) | SWEs focused on production | SWEs building tools for engineers |
| Tools focus | Backlogs, sprints, boards | CI/CD, IaC, monitoring | Observability, capacity, incident | Self-service portal, golden paths |
| Failure mode | Feature factory, no outcomes | "DevOps team" silo (new wall) | SLO theater, ignored budgets | Platform no one adopts |
| Time horizon | Sprint (1–2 weeks) | Per-deploy (minutes–hours) | Rolling SLO window (28–30 days) | Quarter/roadmap |

## Where They Overlap

- **Agile and DevOps**: both want short feedback loops and iterative delivery; DevOps is "Agile applied to the whole delivery system, including ops"
- **DevOps and SRE**: both want reliable production; SRE is one opinionated *way to do* DevOps
- **SRE and Platform Engineering**: both treat ops as engineering; the platform abstracts the operational layer for product teams
- **DevOps and Platform Engineering**: a platform team delivers the "DevOps experience" to product teams as a product, instead of asking every team to assemble it themselves

## Where They Differ (Important)

### DevOps vs SRE

> "Class SRE implements Interface DevOps" — popularized by Google's SRE advocacy

DevOps = principles. SRE = an opinionated, measurable implementation.

- DevOps says "monitor your systems"; SRE says "define an SLO of 99.9% availability over 28 days, then alert on the burn rate"
- DevOps says "automate everything"; SRE says "if toil exceeds 50% of an SRE's time, fix it or add headcount"
- DevOps says "shared ownership"; SRE says "if a service can't meet its SLO, the error budget freezes feature work — or it gets handed back to the dev team to operate"

The practical tell: **SRE attaches numbers to DevOps slogans.** "Reliable" becomes 99.95%; "automate toil" becomes a 50% cap; "embrace risk" becomes a quantified error budget you're *allowed* to spend.

### DevOps vs Platform Engineering

- DevOps: *every* team does its own CI/CD, IaC, and monitoring
- Platform Engineering: a *platform team* builds reusable infrastructure that other teams consume as a product, with a roadmap and adoption metrics

The reason for the shift: at scale (say, 50+ engineering teams), every team rebuilding observability, secret management, and deployment is wasteful and inconsistent. The platform pays that cost once.

### Agile vs DevOps

- Agile stops at "code committed / story done"
- DevOps continues to "code running in production, observed, with feedback flowing back"

A team can be *very* Agile and still ship to production once a quarter. That deployment gap is exactly what DevOps fills.

### SRE vs Platform Engineering

- SRE owns *reliability* of running services (SLOs, on-call, capacity, incident response)
- Platform Engineering owns the *developer experience* of building and shipping services (paved roads, self-service, golden paths)

They frequently coexist: the platform provides reliability primitives (auto-instrumented observability, safe deploy paths), and SRE sets and defends the reliability targets on top.

## The Unified Picture

```
                Business Outcomes
                       ▲
                       │
            ┌──────────┴──────────┐
            │ Continuous Delivery │
            │  (the OUTCOME you   │
            │   want from all     │
            │   of these)         │
            └────┬────┬────┬──────┘
                 │    │    │
        ┌────────┘    │    └────────┐
        │             │             │
    ┌───▼───┐    ┌────▼───┐    ┌───▼─────────┐
    │ Agile │    │ DevOps │    │  SRE / IDP  │
    └───────┘    └────────┘    └─────────────┘
       dev          delivery       reliability /
       loop         loop           platform
```

Each addresses a layer of the same problem: building, shipping, and running software that delights customers. None of these is a replacement for another — adopting SRE does not mean dropping DevOps any more than adopting DevOps means dropping Agile.

## A Decision Guide: Which Do You Need Next?

| Symptom | Likely missing layer |
|---|---|
| Building the wrong things; no customer feedback | **Agile** (shorten the build–measure–learn loop) |
| Code sits in a release queue; deploys are scary, rare events | **DevOps** (CI/CD, IaC, shared ownership) |
| You deploy fast but break things; no agreed reliability target | **SRE** (SLOs, error budgets, blameless incident process) |
| 50+ teams each rebuilding the same infra; onboarding takes weeks | **Platform Engineering** (an IDP with golden paths) |

Adopting these out of order is a classic mistake: a platform with no CD underneath, or SLOs on a system you can't deploy reliably, just adds ceremony.

## Common Mistakes

- **Treating them as competitors** — "we chose SRE over DevOps" is a category error; SRE *is* a way to do DevOps
- **Title confusion** — assuming an "SRE team" means you've "done DevOps"; roles are not practices
- **Skipping layers** — standing up a platform team at 15 engineers before any duplication pain exists
- **SLO theater** — defining SLOs nobody alerts on or enforces, so the error budget is decorative
- **Agile = velocity** — optimizing story points while production stays broken; Agile without DevOps is a feature factory
- **Platform-as-mandate** — forcing teams onto a platform before it's better than their status quo, breeding resentment

## Best Practices

- **Adopt principles before packaging** — get shared ownership and CD working before formalizing SRE or a platform team
- **Sequence by bottleneck** — fix the layer that's actually blocking outcomes, using the decision guide above
- **Make reliability numeric** — replace "be more reliable" with an SLO and an error budget the whole team can see
- **Treat the platform as a product** — roadmap, user research, adoption metrics; never "build it and they will come"
- **Keep teams cross-functional** — none of these four justifies recreating the dev/ops wall as a new silo
- **Measure the right thing per layer** — DORA for delivery, SLO burn for reliability, DX/adoption for the platform

## Quick Refs

```
Mnemonic — what each layer answers:
  Agile     → WHAT to build (iteratively, with feedback)
  DevOps    → HOW to deliver it (commit → production, fast & safe)
  SRE       → HOW to keep it reliable (SLOs, error budgets, toil caps)
  Platform  → HOW to make it reusable (golden paths, self-service)

One-liner for the interview:
  "SRE is an opinionated implementation of DevOps;
   Platform Engineering delivers the DevOps experience as a product."
```

## Interview Prep

**Junior**: "What's the difference between Agile and DevOps?"
- Agile is iterative development that stops at "code done"; DevOps extends that loop all the way to code running in production, observed, with feedback — it fills the deployment gap Agile leaves open.

**Mid**: "Is DevOps the same as SRE?"
- No — DevOps is a movement of principles ("automate everything," "shared ownership"), while SRE is Google's opinionated, measurable implementation that attaches numbers to those principles via SLOs, error budgets, and a 50% toil cap.

**Senior**: "When would your company adopt Platform Engineering instead of just 'doing DevOps'?"
- When team count and cognitive load make duplication wasteful — typically around 50+ engineers / 5+ teams each rebuilding the same observability, secrets, and deploy plumbing — at which point you productize that knowledge once as an IDP rather than paying for it per team.

**Staff**: "Critique the statement: 'We have an SRE team, so we don't need DevOps.'"
- It conflates a role with a set of practices: SRE *is* one shape of DevOps, so the sentence is self-contradictory; the real risk it signals is an SRE team operating as a siloed ticket queue — exactly the dev/ops wall DevOps exists to remove.

## Next Topic

→ [T05 — The Business Case for DevOps (DORA Metrics Intro)](T05-Business-Case-DORA.md)
