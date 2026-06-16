# L30/C04/T02 — Golden Path Templates

## Learning Objectives

- Build templates
- Self-service

## Why Golden Paths

A golden path is the **paved road**: the supported, opinionated way to build a
service that comes with CI, observability, security, and deployment already
wired. It's the mechanism that delivers the capstone's promise — a new service
running in minutes instead of days — and, just as importantly, it's how a
platform team spreads good practice *without* mandating it. You don't write a
policy saying "everyone must add SBOM scanning"; you make the template do it, and
the easy path becomes the right path.

### The Key Tension: Paved Road, Not a Cage

The defining trade-off of golden paths is **standardization vs. flexibility**. Too
rigid and teams route around the platform (shadow infra, the platform team
becomes a blocker); too loose and you've standardized nothing. The senior framing
is that the golden path should be *optional but overwhelmingly attractive* —
teams take it because it's faster and safer, and they keep the option to step off
for genuinely different needs. Adoption is earned, not enforced.

### What a Good Template Includes

- Repo scaffold + `catalog-info.yaml` (auto-registers — C04/T01)
- Pre-built CI (the scan-sign-SBOM pipeline from C01/T05, by reference)
- K8s manifests + a ServiceMonitor (observability on day one)
- A Grafana dashboard and a runbook stub
- OTel instrumentation wired (so correlation works out of the box — C03/T04)

## Template

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: webapp-template
  title: Create New Web Service
spec:
  parameters:
    - title: Service Info
      properties:
        name:
          type: string
          title: Service Name
        team:
          type: string
          title: Owner Team
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          team: ${{ parameters.team }}
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?owner=org&repo=${{ parameters.name }}
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
```

## Skeleton

```
skeleton/
  catalog-info.yaml
  README.md
  src/
    main.go
  .github/
    workflows/
      ci.yml
  Dockerfile
  deploy/
    chart/
      ...
```

## Values

```yaml
# In catalog-info.yaml
metadata:
  name: ${{ values.name }}
spec:
  owner: ${{ values.team }}
```

Replaced when scaffolded.

## Multiple Templates

```
templates/
  webapp/
  worker/
  cli/
  library/
```

Per use case.

## Use

Backstage UI:
1. Pick template
2. Fill params
3. Create
4. Auto: repo + register

## Update / Day-2 Problem

Template owners update the skeleton, but **existing services don't auto-update** —
this is the hard, often-skipped part of golden paths. A template improves
day-one; keeping the 200 services scaffolded last year current is day-two. Real
answers: a "renovate"-style bot that opens PRs to pull template changes
(CI workflow bumps, base-image updates) into existing repos, or treating the
shared pieces (CI workflow, base Helm chart) as *referenced* dependencies rather
than copied files so a single bump propagates. Mentioning this drift problem
unprompted is a strong senior signal.

## Best Practices

- Cover top use cases
- Include CI/CD
- Include observability
- Include IaC
- Document

## Common Mistakes

- Too rigid
- Stale skeleton
- No CI/CD
- No observability

## Acceptance Criteria

- One form submission produces a repo with CI, manifests, a dashboard, and a
  `catalog-info.yaml`, and registers it in the catalog
- The generated service builds and deploys with no manual edits
- The scaffolded CI already includes the security gates (no team has to add
  them)
- You can articulate the day-2 update story (how existing services get template
  improvements)

## Quick Refs

```yaml
kind: Template
spec:
  parameters: ...
  steps:
    - fetch:template      # render skeleton with values
    - publish:github      # create repo
    - catalog:register    # auto-register in catalog
```
```
Golden path = paved road: optional but overwhelmingly attractive
Includes: CI + observability + security + manifests by default
Day-2: bot PRs or referenced deps so existing services don't rot
```

## Interview Prep

**Junior**: "What's a golden path template?" — A pre-built starter for a new
service that already includes CI, deployment manifests, and observability, so a
developer fills a short form and gets a working, standardized service instead of
copying boilerplate from another repo.

**Mid**: "What should a golden-path template bundle, and why?" — Repo scaffold,
a ready CI pipeline (with the security scanning and signing built in), K8s
manifests, a dashboard, and instrumentation — everything needed to be
production-shaped on day one. Bundling it means good practice spreads by default:
every new service gets SBOM scanning and observability without anyone
remembering to add them.

**Senior**: "How do you balance standardization against team autonomy?" — The
golden path has to be *optional but the obviously better choice* — faster and
safer than rolling your own — so teams adopt it because they want to, not because
they're forced. If it's a cage, teams build shadow infrastructure to escape it
and the platform team becomes a blocker. So I'd keep escape hatches for genuinely
different needs, measure adoption as the real success metric, and treat low
adoption as a product problem (the path isn't good enough) rather than a
compliance problem. Standardize the 80% common case; don't try to template the
20% long tail.

**Staff**: "You shipped a great template, but a year later the 200 services made
from it are all on outdated CI and base images. What went wrong and how do you
fix it?" — The mistake was treating the template as a one-time scaffold (copy)
instead of a living dependency. Copied boilerplate is dead the moment it's
generated — there's no link back to the source to update. The fix is to make the
shared pieces *referenced*, not copied: the CI pipeline is a reusable workflow
called by version, the base Helm chart is a dependency, the base image is pinned
and bumped centrally — so one change propagates by re-resolution. For the parts
that genuinely must be copied, run an automated bot (Renovate-style) that opens
PRs across all repos to pull template deltas, making the update a one-click
review per team rather than a manual migration. The staff insight is that the
day-2 update story *is* the platform — a template anyone can outgrow in a quarter
isn't a paved road, it's a snapshot.

## Next Topic

→ [T03 — Self-Service Provisioning](T03-Self-Service.md)
