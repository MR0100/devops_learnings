# L01/C01/T04 — DevOps vs Agile vs SRE vs Platform Engineering

## Learning Objectives

- Differentiate four overlapping concepts by their origin, focus, and primary artifact
- Use a side-by-side matrix to answer FAANGM-style "what's the difference" questions
- Recognize that these are complementary, not competing

## Quick Definitions

| Term | Origin | Primary Focus | Primary Artifact |
|---|---|---|---|
| **Agile** | 2001 (Snowbird) | Iterative software development | Working software each sprint |
| **DevOps** | 2009 (Debois) | End-to-end software delivery | Continuous delivery pipeline |
| **SRE** | 2003 (Google) | Reliability as engineering | Error budget + SLO |
| **Platform Engineering** | 2020+ (Team Topologies) | Cognitive load reduction | Internal Developer Platform |

## The Matrix

| Dimension | Agile | DevOps | SRE | Platform Engineering |
|---|---|---|---|---|
| Primary problem | Slow, inflexible development | Wall between dev and ops | Operating at scale | Cognitive load on product teams |
| Cultural emphasis | Customer collaboration, change | Shared ownership | Embracing risk, blameless | Treating internal tools as products |
| Org structure | Cross-functional product teams | Cross-functional product teams | SRE teams embedded or central | Platform team + Stream-aligned teams |
| Key metric | Working software, velocity | DORA (DF, LT, MTTR, CFR) | SLI / SLO / Error budget | Developer experience, platform adoption |
| Hires | Software engineers | Dev + Ops (later, the same) | Software engineers focused on prod | Software engineers building tools for engineers |
| Tools focus | Backlogs, sprints | CI/CD, IaC, monitoring | Observability, capacity, incident | Self-service portal, golden paths |

## Where They Overlap

- **Agile and DevOps**: both want short feedback loops and iterative delivery
- **DevOps and SRE**: both want reliable production; SRE is one way to "do DevOps"
- **SRE and Platform Engineering**: both treat ops as engineering; platform abstracts ops for product teams
- **DevOps and Platform Engineering**: platform teams provide the "DevOps experience" as a product

## Where They Differ (Important)

### DevOps vs SRE

> "Class SRE implements Interface DevOps" — Liz Fong-Jones (paraphrased from a Google talk)

DevOps = principles. SRE = an opinionated implementation.

- DevOps says "monitor your systems"; SRE says "define an SLO with 99.9% availability over 30 days, then alert on burn rate"
- DevOps says "automate everything"; SRE says "if toil exceeds 50% of an SRE's time, get more engineers or kill the toil"
- DevOps says "shared ownership"; SRE says "if a service can't meet its SLO, it gets handed back to dev to operate"

### DevOps vs Platform Engineering

- DevOps: every team does CI/CD, IaC, monitoring
- Platform Engineering: a *platform team* builds reusable infrastructure that other teams consume as a product

The reason for the shift: at scale (say, 50+ engineering teams), having every team rebuild observability, secret management, deployment is wasteful and inconsistent.

### Agile vs DevOps

- Agile stops at "code committed"
- DevOps continues to "code in production, observed, with feedback"

A team can be "very Agile" and still ship to production once a quarter. That's the gap DevOps fills.

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

Each addresses a layer of the same problem: building, shipping, and running software that delights customers.

## Interview Prep

**Mid**: "Is DevOps the same as SRE?"
- No. DevOps is a movement/principles. SRE is Google's opinionated, measurable, software-engineering-focused implementation.

**Senior**: "When would your company adopt Platform Engineering instead of just 'doing DevOps'?"
- When team count and cognitive load make duplication wasteful. Usually ~50 engineers / ~5+ teams.

**Staff**: "Critique the statement: 'We have an SRE team, so we don't need DevOps.'"
- Conflates roles with practices. SRE *is* one shape of DevOps. The statement reveals misunderstanding of both.

## Next Topic

→ [T05 — The Business Case for DevOps (DORA Metrics Intro)](T05-Business-Case-DORA.md)
