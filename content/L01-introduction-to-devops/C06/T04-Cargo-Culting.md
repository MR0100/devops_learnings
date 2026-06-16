# L01/C06/T04 — Cargo-Culting Practices

## Learning Objectives

- Define cargo-culting in the engineering context and explain the cause/side-effect confusion at its core
- Identify the most common cargo-cult adoptions and the conditions their originators actually had
- Detect cargo-culting in your own org with a small set of diagnostic questions
- Lead a team through the discipline of differentiating a real practice from theater

## Prerequisites

The category errors (T01) and the "DevOps team" anti-pattern (T02), since several cargo-cult adoptions are just those errors dressed in a famous company's clothes. The DORA + SPACE measurement framing from C05 is the antidote referenced throughout.

## What "Cargo Cult" Means

The term comes from post-WWII Pacific islands, where some communities built straw replicas of runways, control towers, and headsets after the wartime airbases left — faithfully imitating the *actions* that had preceded cargo arriving, without understanding that those actions were **side effects of a supply chain, not the cause of the cargo**. The planes never came back, because the rituals were never what summoned them.

In engineering:

> Cargo-culting is adopting the *artifacts* of high-performing teams (microservices, Kubernetes, blameless postmortems, SRE) without understanding the *conditions* that made those artifacts work.

The artifact is the straw runway. The conditions — the platform investment, the test infrastructure, the psychological safety, the headcount — are the missing supply chain. Copy the artifact without the conditions and you get the *cost* of the practice with none of its *benefit*.

## Famous Cargo-Cult Adoptions

### Microservices "Because Netflix"
- **Netflix had**: ~250+ services, a deep internal platform, dedicated platform engineering, and the org size to give each service a team
- **You have**: 4 services, 15 engineers, and a shared on-call
- **Result**: a *distributed monolith* — all the network latency, partial-failure modes, and operational overhead of microservices, with none of the team-independence benefit, because the same handful of engineers still touch every service

### Kubernetes "Because Google"
- **Google had**: planet-scale workloads, a decade of Borg experience, and deep in-house orchestration expertise
- **You have**: 5 services that fit comfortably on 3 VMs
- **Result**: six months of platform work and a permanent operational tax (upgrades, CNI, RBAC, autoscaling) for zero business-value uplift — a managed PaaS or plain VMs would have shipped the same product sooner

### Blameless Postmortems "Because Etsy"
- **Etsy had**: deep, leadership-backed psychological safety and a genuine culture of learning
- **You have**: a postmortem template and a "blameless" header on the doc
- **Result**: postmortem *theater* — the meeting happens, the doc gets filled in, the VP still names names in the hallway, and the action items never land

### Trunk-Based Development "Because Google"
- **Google had**: a massive automated test farm, near-instant CI, and pervasive feature-flagging
- **You have**: 30-minute CI, partial test coverage, and no feature flags
- **Result**: a broken trunk, fear of committing, and *slower* delivery than the branching model you abandoned

### SRE "Because the Book"
- **Google had**: SRE teams with hiring authority, real error-budget enforcement power, and scaled tooling
- **You have**: the same ops engineers, renamed, with no authority to halt a launch
- **Result**: rebranded ops, identical outcomes, plus the morale cost of a promise that wasn't kept

| Practice | Condition the originator had | Failure mode when copied without it |
|---|---|---|
| Microservices | Many teams, deep platform | Distributed monolith |
| Kubernetes | Scale + orchestration expertise | Complex platform, no uplift |
| Blameless postmortems | Leadership-backed psych safety | Postmortem theater |
| Trunk-based dev | Huge test infra + feature flags | Broken trunk, fear of commit |
| SRE | Authority + error-budget power | Rebranded ops |

## How to Detect Cargo-Culting in Your Org

Ask four questions. If the answers are vague, you're probably imitating outputs:

1. **What problem are we solving?** If the answer is "modernization," "best practice," or "everyone's doing it" — suspect cargo-cult. Real adoptions name a specific pain.
2. **What were our metrics *before* this?** If we can't state the baseline (deploy frequency, lead time, MTTR, change-failure rate), we can't prove improvement — and unprovable improvement is belief, not engineering.
3. **What conditions does this practice require?** If we haven't enumerated and checked them (test infra, team count, psychological safety, headcount), we're copying the artifact and skipping the supply chain.
4. **What's our exit strategy?** If we can't describe how we'd reverse it, we've committed to a belief, not run an experiment.

## A Litmus Test

You can usually spot cargo-culting from outside the room — listen for an adopted artifact paired with a mismatched or absent cause:

- "We're moving to microservices to improve scalability" — *but the bottleneck is a single un-indexed database*
- "We're adopting Kubernetes to be cloud-native" — *but there's no cloud strategy and five services on three VMs*
- "We do blameless postmortems" — *but the VP names names in the readout*
- "We have SLOs" — *but no error-budget policy, so nothing ever changes when they're breached*
- "We're trunk-based now" — *but CI takes 30 minutes and there are no feature flags*

In each case the words describe the runway; the supply chain is missing.

## The Right Way to Adopt Practices

```
   1. IDENTIFY the actual problem   ← use DORA + SPACE, name the metric
            │
   2. GENERATE hypotheses          ← include the famous option AND simpler ones
            │
   3. PILOT + MEASURE              ← contained scope, baseline vs after
            │
   4. SCALE only if metrics moved  ← otherwise revert; you have an exit plan
```

1. **Identify the actual problem** using DORA + SPACE — name the metric you're trying to move
2. **Generate hypotheses** — list microservices/K8s/SRE *alongside* the boring, simpler alternatives (a faster DB index, a monolith split into two, a managed PaaS)
3. **Pilot and measure** in a contained scope against a real baseline
4. **Scale only if the metrics actually moved** — and if they didn't, revert, because you defined an exit strategy up front

This discipline applies to *every* tool and practice this course covers, including the ones it recommends.

## Common Mistakes

- **Naming a tool as the goal** — "adopt Kubernetes" is never a goal; "cut lead time from days to hours" is, and K8s may or may not be the means
- **Skipping the baseline** — adopting without measuring before, then being unable to prove the change helped (or hurt)
- **Ignoring the originator's conditions** — copying Netflix's architecture without Netflix's platform team
- **Theater over substance** — running the ritual (the postmortem meeting, the SLO dashboard) while the enabling condition (safety, an error-budget policy) is absent
- **No exit strategy** — making a change irreversible, which converts an experiment into a faith commitment

## Best Practices

- **Start from the problem and the metric**, never from the artifact — DORA + SPACE first
- **Always list a simpler alternative** to the famous practice; make the famous one earn its place
- **Pilot small, measure honestly, scale or revert** — treat practice adoption as a falsifiable experiment
- **Enumerate the required conditions explicitly** and check whether you have them before you copy the artifact
- **Name an exit strategy up front** — if you can't describe how to reverse it, you're not experimenting, you're believing

## Quick Refs

```text
Cargo-cult detector (4 questions):
  1. What problem?        → "modernization"/"best practice" = red flag
  2. Metrics before?      → no baseline = can't prove anything
  3. Conditions required? → unchecked = copying the artifact, not the cause
  4. Exit strategy?       → none = belief, not experiment

Litmus pairings (artifact + mismatched cause):
  microservices ↔ the bottleneck is the DB
  Kubernetes    ↔ no cloud strategy
  blameless PM  ↔ the VP names names
  SLOs          ↔ no error-budget policy
```

Mnemonic: **Copy the conditions, not the artifacts — the straw runway never summons the plane.**

## Interview Prep

**Junior**: "What is cargo-culting in engineering?"
- Copying the practices of a famous high-performing team — microservices, Kubernetes, postmortems — without the conditions that made them work, so you get the cost without the benefit, like building a straw runway and expecting planes.

**Mid**: "How can you tell a practice is being cargo-culted?"
- The justification is "modernization" or "everyone does it" rather than a named problem and metric, there's no before/after baseline, and nobody has checked whether the team has the conditions the practice requires — like adopting trunk-based development without fast CI or feature flags.

**Senior**: "When have you avoided cargo-culting? What was the conversation?"
- I'd give a concrete example where a team wanted a famous practice — say microservices — and I reframed it around the actual bottleneck (often the database), proposed a simpler alternative, set a metric and baseline, and either piloted small or talked them out of it, so we solved the real problem instead of importing someone else's solution.

**Staff**: "Your team is pitching a Kubernetes migration because 'everyone's moving to K8s.' What questions do you ask?"
- What problem are we solving and what metric proves it? What are our current numbers? What constraints and scale do we actually have? What's the real cost — platform headcount and ongoing operational tax? What are the simpler alternatives (PaaS, plain VMs, ECS)? Do we have the team capacity to run it? And what's our exit strategy if it doesn't move the metric — because "everyone's doing it" is the straw runway, not the supply chain.

**Principal**: "A new VP wants the org to 'adopt SRE.' What's your guidance?"
- I'd start by asking what problem SRE is meant to solve and what reliability outcome we're targeting, then explicitly avoid the rename trap — SRE without hiring authority and a real error-budget policy is just relabeled ops; I'd pilot with one team, define what authority and budget enforcement SRE will genuinely have, set a baseline, and measure before/after, scaling only if reliability and toil actually improve.

## Closing Note for L01

You've now finished L01. The mental model you should walk away with:

- DevOps is cultural + organizational + technical, not just tools
- DORA + SPACE measure outcomes; tools enable them
- Anti-patterns are common; staff engineers recognize them quickly
- Career progression rewards force multipliers, not heroes

## Next Lecture

→ [L02 — Linux & Operating System Internals](../../L02-linux-and-os-foundations/README.md)
