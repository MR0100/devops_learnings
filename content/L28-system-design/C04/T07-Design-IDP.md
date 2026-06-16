# L28/C04/T07 — Design an Internal Developer Platform

## Learning Objectives

- Design IDP
- Self-service

## Requirements

### Functional
- Self-service service creation
- Standard CI/CD
- Observability included
- Cost tracking
- Documentation

### Non-Functional
- 1000+ engineers
- Many services
- 99.9% available
- Easy onboarding

## Estimation (derived — the ROI case)

An IDP's "capacity" is human leverage, so estimate the payoff, not QPS:
```
engineers          = 1,000
hours_saved/eng/wk = 2        (no hand-rolling CI, infra tickets, dashboards)
weekly_hours_saved = 1,000 × 2 = 2,000 eng-hours/week
```
That's ~50 FTE-equivalents of toil removed weekly — which justifies a platform team of, say, 8–10:
```
leverage_ratio ≈ 1,000 engineers served / 10 platform engineers = 100:1
```
The portal's request load is trivial (a few hundred internal users, low QPS) — Backstage is **not** a scaling problem. The real "scale" axis is **catalog size and template count**: 500+ services, dozens of golden-path templates the platform team must keep current. **Derived insight: size the platform team for maintenance leverage, not the portal for traffic.** Below ~100 engineers the ratio doesn't pay off — build vs buy tilts to buy/OSS (C06/T01).

## Components

### Portal
Backstage:
- Service catalog
- Docs
- Templates
- Plugins

### Templates
- New service scaffolds
- IaC included
- Pipeline included

### IaC Layer
- Crossplane / Terraform
- Self-service infra

### CI/CD
- Standard pipelines
- Templated

### Observability
- Auto-instrumented
- Dashboards included

### Cost
- Per-service
- Showback

### Docs
- Auto-generated
- Linked

### Secrets
- Vault integration
- Workload Identity

## Architecture

```
Devs → Backstage portal
              ↓
        Templates (cookiecutter)
              ↓
        Repos + IaC + pipeline
              ↓
        Deploy to K8s
              ↓
        Observability + cost
```

## Service Template

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: webapp
spec:
  parameters: ...
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
    - id: github
      action: publish:github
    - id: register
      action: catalog:register
```

## Golden Paths

(See L28/C05/T02.)

Standardized workflows.

## Crossplane

K8s-native cloud resources:
```yaml
kind: PostgreSQLInstance
spec:
  ...
```

Self-service infra.

## Deep Dive: Platform as a Product

The failure mode of IDPs is treating them as a project (build it, declare victory) instead of a product (continuously earn adoption). Run it like a product:
- **Adoption is the metric, not features**: track % of services on the golden path, time-to-first-deploy for a new service, and platform NPS. If adoption is low, the platform is wrong, not the engineers.
- **Self-service or it doesn't count**: any step that requires filing a ticket to the platform team defeats the purpose — the team becomes the bottleneck it was meant to remove. Templates + Crossplane self-service infra mean *zero* tickets for the common path.
- **Paved road, not mandate** (see C06/T02): the golden path is the easiest path, so teams choose it; deviating is allowed but the deviating team owns the operational cost. Consistency without coercion.
- **The team maintains leverage**: 8–10 platform engineers keep templates current, backport security fixes, and own the shared concerns (CI, observability, secrets) so 1000 product engineers don't each reinvent them — the ~100:1 ratio from the estimation.

## Real Examples

### Spotify
Backstage (created it).

### Netflix
Custom; sophisticated.

### Many SaaS
Backstage adoption.

## Trade-Offs

- Build vs buy
- Standardize vs flexibility
- Curated vs free-for-all

## Best Practices

- Backstage
- Templates / golden paths
- Auto-everything (CI/CD, obs)
- Self-service infra
- Cost visible

## Common Mistakes

- No templates (chaos)
- Required tickets (defeats purpose)
- No metrics on platform success

## Quick Refs

```
Components:
- Portal (Backstage)
- Templates
- IaC (Crossplane)
- CI/CD
- Observability
- Cost
- Docs

Goal: self-service for devs
```

## Interview Prep

**Senior**: "What actually goes into an IDP, beyond 'install Backstage'?" — Backstage is just the portal; the platform is the wiring behind it: golden-path templates that scaffold repo + CI + manifests + dashboards + runbook, a self-service infra layer (Crossplane/Terraform) so devs provision a database without a ticket, GitOps deploy, and observability/secrets/cost auto-wired in. Each piece alone isn't a platform — the value is that they compose into a one-command "new service to prod" path.

**Staff**: "Design an IDP for 1000 engineers — how do you justify it and how big is the team?" — Justify it as leverage: ~2 hours/engineer/week of toil removed is ~50 FTE-equivalents, which pays for an 8–10 person platform team serving 1000 — roughly 100:1. The portal itself is low-QPS and not a scaling problem; the real maintenance load is keeping 500+ catalog entries and dozens of templates current. I'd size the team for that maintenance leverage, not the portal for traffic.

**Principal**: "Your IDP shipped but adoption is stuck at 40% — what's wrong and what do you do?" — The platform is the problem, not the engineers. Forty percent means the golden path has friction — it's slower, less flexible, or missing a use case teams need, so they route around it. I'd treat it as a product: interview the non-adopters, instrument where they drop off, fix the friction, and make the paved road genuinely the *easiest* path rather than mandating it. If a whole category (say, ML services) has no template, that's a roadmap gap, not non-compliance. Adoption %, time-to-first-deploy, and platform NPS are the metrics I'd manage to.

## Next Topic

→ [T08 — Design a Rate Limiter](T08-Design-Rate-Limiter.md)
