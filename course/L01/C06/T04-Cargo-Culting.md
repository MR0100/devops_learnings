# L01/C06/T04 — Cargo-Culting Practices

## Learning Objectives

- Define cargo-culting in the engineering context
- Identify common cargo-cult adoptions
- Lead a team through differentiation: practice vs theater

## What "Cargo Cult" Means

From the Pacific tradition of imitating actions of others in hope of recreating their results — even when the actions were just side effects, not causes. In engineering:

> Adopting the *artifacts* of high-performing teams (microservices, Kubernetes, postmortems) without understanding the *conditions* that made them work.

## Famous Cargo-Cult Adoptions

### Microservices Because Netflix
- Netflix: 250 services, deep tooling, strong platform engineering
- You: 4 services, 15 engineers, microservices add complexity without benefit
- Result: distributed monolith with all the network costs and none of the team-independence benefits

### Kubernetes Because Google
- Google: planet-scale, deep K8s expertise, custom Borg history
- You: 5 services that fit on 3 VMs, K8s adds 6 months of platform work
- Result: complex platform, no business value uplift

### Postmortems Because Etsy
- Etsy: deep psychological safety, leadership investment
- You: postmortem template + blameless statement, no follow-through
- Result: postmortem theater; action items never land

### Trunk-Based Development Because Google
- Google: massive test infrastructure, gigantic CI farm
- You: 30-minute CI, no feature flags, partial test coverage
- Result: broken trunk, fear of committing, slower delivery

### SRE Because the Book
- Google: SRE has hiring authority, error-budget enforcement, scaled tooling
- You: rename existing ops engineers, no power to push back
- Result: rebranded ops, no new outcomes

## How to Detect Cargo-Culting in Your Org

Ask:

1. **What problem are we solving?**  If "modernization" or "best practice", suspect cargo-cult.
2. **What were our metrics before this?** If we can't answer, we can't measure improvement.
3. **What conditions does this practice require?** If we haven't checked them, we're imitating outputs.
4. **What's our exit strategy?** If we can't reverse it, we're committing to belief.

## The Right Way to Adopt Practices

1. **Identify the actual problem** (use DORA + SPACE)
2. **Generate hypotheses** (microservices, K8s, SRE — *and* simpler alternatives)
3. **Pilot, measure** in a contained scope
4. **Scale only if metrics moved**

This applies to *every* tool/practice this course covers.

## A Litmus Test

You can usually tell cargo-culting from outside the room:

- "We're moving to microservices to improve scalability" (but the bottleneck is the DB)
- "We're adopting Kubernetes to be cloud-native" (but you have no cloud strategy)
- "We're doing blameless postmortems" (but the VP names names)
- "We have SLOs" (but no error budget policy)

## Interview Prep

**Senior**: "When have you avoided cargo-culting? What was the conversation?"

**Staff**: "Your team's pitching a K8s migration because 'everyone's moving to K8s.' What questions do you ask?"
- What problem? Current metrics? Constraints? Cost? Alternatives? Team capacity? Exit strategy?

**Principal**: "A new VP wants the org to 'adopt SRE'. What's your guidance?"
- Ask: what problem? Avoid renaming ops. Pilot with one team. Define what authority SRE will have. Measure before/after.

## Closing Note for L01

You've now finished L01. The mental model you should walk away with:

- DevOps is cultural + organizational + technical, not just tools
- DORA + SPACE measure outcomes; tools enable them
- Anti-patterns are common; staff engineers recognize them quickly
- Career progression rewards force multipliers, not heroes

## Next Lecture

→ [L02 — Linux & Operating System Internals](../../L02/README.md)
