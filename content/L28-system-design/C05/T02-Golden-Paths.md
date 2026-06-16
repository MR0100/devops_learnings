# L28/C05/T02 — Golden Paths

## Learning Objectives

- Apply golden paths
- Standardize

## Golden Path

Recommended way:
- "Use template X for new service"
- "Use library Y for HTTP"
- Standard observability

For: ease + consistency.

## Spotify Term

Spotify Backstage popularized.

## Per Use Case

### New Service
Template:
- Code skeleton
- Pipeline
- IaC
- Observability

```bash
backstage scaffold create service-webapp
```

### Add Endpoint
Standard library handles:
- Routing
- Auth
- Metrics

### Deploy
Standard pipeline runs:
- Build
- Test
- Deploy

For: opinions help dev.

## Benefits

- Faster start
- Best practices baked in
- Maintainable (everyone uses same)

## Not Forced

Devs can deviate:
- For valid reasons
- Document why

For: opinions, not mandates.

## Examples

### Web Service
- Go + Gin (or Java + Spring)
- Postgres
- ArgoCD deploy

### Worker
- Python + Celery
- SQS
- Same observability

### Frontend
- React + Vite
- S3 + CloudFront
- Lighthouse CI

## Maintain

Platform team:
- Updates templates
- Adds features
- Backports security

For: continuous.

## Track Adoption

```
# Services using golden path
80% (target: > 90%)
```

If low: investigate why; fix friction.

## Real Examples

### Spotify
Backstage golden paths.

### Stripe
Strong opinions.

### Many

## Best Practices

- Define for top use cases
- Easy onboarding
- Periodic update
- Track adoption
- Listen to friction

## Common Mistakes

- Force (resistance)
- Stale templates
- No metrics
- Too rigid

## Quick Refs

```
Golden Path:
- Templated
- Opinions
- Best practices baked in
- Devs free to deviate (rare)

Track: adoption %
```

## Interview Prep

**Junior**: "What's a golden path?" — The recommended, well-supported way to do a common task — 'use this template for a new service', 'use this library for HTTP'. It scaffolds the standard setup (code, CI, infra, observability) so engineers start from a working, best-practice baseline instead of a blank repo.

**Mid**: "Why golden paths instead of just documentation?" — Docs describe the right way; golden paths *do* it for you. A template that generates the repo, pipeline, manifests, and dashboards means best practices are baked in by default rather than depending on each engineer reading and remembering. It's the difference between 'you should add metrics' and 'metrics are already wired up'.

**Senior**: "How do you keep golden paths from becoming rigid mandates?" — Make them the easiest path, not the only one — engineers choose them because they're faster, and deviation is allowed for valid reasons (documented). The platform team's job is to remove friction so the path stays attractive, and to keep templates current (backport security fixes, add features) so they don't go stale and drive people off-road. Opinions, not handcuffs.

**Staff**: "How do you measure and improve golden-path adoption across an org?" — Track adoption % per use case (target >90%) and treat a low number as a signal to investigate friction, not to crack down. If a category of service has no template, that's a roadmap gap. I'd define paths for the top use cases (web service, worker, frontend), instrument where people drop off or deviate, listen to the friction, and iterate — running the golden paths as a product with the platform team as its owners. Forcing adoption breeds shadow workarounds; reducing friction earns it.

## Next Topic

→ [T03 — Backstage for Service Catalog](T03-Backstage.md)
