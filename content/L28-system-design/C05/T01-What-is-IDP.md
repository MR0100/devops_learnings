# L28/C05/T01 — What an IDP Actually Is

## Learning Objectives

- Define IDP
- Goals

## IDP

Internal Developer Platform:
- Self-service for devs
- Abstract complexity
- Golden paths
- Reduces cognitive load

## Goals

- Devs ship faster
- Less Ops bottleneck
- Standards built-in
- Compliance automatic

## Components

- Portal (Backstage, Port)
- Templates
- CI/CD
- Observability
- Cost
- Docs
- IaC

(See L28/C04/T07.)

## Not IDP

- Just K8s
- Just Backstage
- Just CI/CD

Each component alone ≠ platform.

## Goldilocks

Right level of abstraction:
- Too low: complexity
- Too high: rigid

For: balance.

## Curate vs Free

Platform team:
- Curates
- Empowers self-service
- Doesn't gate

## ROI

For 100+ devs:
- IDP saves engineer time
- ROI in months

For small: maybe not.

## Real Examples

### Spotify
Backstage open-sourced.

### Netflix
Custom.

### Many large
Building.

## Best Practices

- Start small
- Iterate
- Adoption metrics
- User feedback

## Common Mistakes

- Build everything
- Force adoption
- No metrics
- Platform-as-product mindset missing

## Quick Refs

```
IDP:
- Portal
- Templates
- Self-service
- Observability
- Cost

Goal: dev velocity
```

## Interview Prep

**Junior**: "What is an Internal Developer Platform?" — A self-service layer that lets product engineers provision environments, deploy, and observe their services without filing tickets to ops. It abstracts the underlying complexity (K8s, cloud, CI) behind golden paths so engineers focus on business logic.

**Mid**: "Isn't an IDP just Backstage / just Kubernetes?" — No — any single component alone isn't a platform. Backstage is a portal, K8s is a runtime, CI is a pipeline. The IDP is the *integration*: templates + self-service infra + CI/CD + observability + secrets + cost, composed so that 'new service to prod' is one paved path. Mistaking one tool for the platform is the classic trap.

**Senior**: "When is an IDP worth building, and when is it not?" — It's leverage, so it pays off above ~100 engineers where the toil it removes (per-engineer hours/week) exceeds the platform team's cost. Below that, the ratio doesn't work — buy or adopt OSS instead of building (C06/T01). And even when you build, start small with the top 1–2 use cases and iterate on adoption, rather than boiling the ocean.

**Staff**: "How do you know your IDP is succeeding?" — Treat it as a product with metrics: adoption (% of services on the golden path), time-to-first-deploy for a new service, and developer satisfaction — not feature count. The right level of abstraction is Goldilocks: too low and devs still wrestle complexity, too high and they can't do anything non-standard. If adoption is low, the platform is wrong, not the engineers — and the failure mode is forcing adoption by mandate instead of making the paved road genuinely the easiest path.

## Next Topic

→ [T02 — Golden Paths](T02-Golden-Paths.md)
