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

**Senior**: "Golden paths."

**Staff**: "Platform standards."

## Next Topic

→ [T03 — Backstage for Service Catalog](T03-Backstage.md)
