# L30/C04/T01 — Service Catalog

## Learning Objectives

- Build Backstage catalog
- Service discovery

## Backstage

```bash
npx @backstage/create-app
```

## Catalog

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: My service
  tags: [web, api]
  links:
    - url: https://github.com/org/my-service
      title: Repo
spec:
  type: service
  lifecycle: production
  owner: team-a
  system: main
```

## Auto-Discovery

```yaml
# app-config.yaml
catalog:
  locations:
    - type: github-discovery
      target: https://github.com/org/*
```

Scans repos for catalog-info.yaml.

## API Spec

```yaml
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: my-api
spec:
  type: openapi
  lifecycle: production
  owner: team-a
  definition: |
    openapi: 3.0.0
    ...
```

For: API discovery.

## System / Domain

```yaml
kind: System
metadata:
  name: payments
spec:
  owner: team-a
  domain: ecommerce
```

For: hierarchy.

## Owner Display

```yaml
kind: Group
metadata:
  name: team-a
spec:
  type: team
  children: []
```

## Best Practices

- catalog-info.yaml mandatory
- Auto-discovery
- Standard structure
- Ownership clear

## Common Mistakes

- Stale entries
- No ownership
- Missing API specs

## Quick Refs

```yaml
kinds: Component / API / System / Domain / Group / User / Resource

Discovery:
  github-discovery
  github-org
```

## Next Topic

→ [T02 — Golden Path Templates](T02-Golden-Templates.md)
