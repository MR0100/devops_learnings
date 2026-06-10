# L28/C05/T03 — Backstage for Service Catalog

## Learning Objectives

- Use Backstage
- Catalog services

## Backstage

Spotify open-source IDP:
- Service catalog
- Templates
- Tech docs
- Plugins

## Install

```bash
npx @backstage/create-app
cd my-backstage
yarn dev
```

## Service Catalog

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: My service
  tags: [web, api]
spec:
  type: service
  lifecycle: production
  owner: team-a
  system: main
```

Each repo: catalog-info.yaml.

## Auto-Discovery

Backstage:
- Reads repos
- Registers components
- Maintains catalog

## Templates

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: webapp
spec:
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
    - id: github
      action: publish:github
      input:
        repoUrl: ${{ parameters.repoUrl }}
```

Use:
- Backstage UI: "Create new service"
- Pick template
- Fill params
- Auto: create repo, register

## TechDocs

```yaml
spec:
  metadata:
    annotations:
      backstage.io/techdocs-ref: dir:.
```

Markdown in repo:
- Auto-rendered
- Searchable

## Plugins

Many:
- GitHub
- ArgoCD
- Datadog
- PagerDuty
- Kubernetes
- Cost
- Custom

## Software Catalog

Components, Systems, Resources, Users, Groups.

For: org-wide view.

## Dependency Graph

Auto-rendered:
- Service A depends on Service B
- Visual

## API Spec

```yaml
spec:
  type: openapi
  definition: |
    openapi: 3.0.0
    ...
```

OpenAPI in catalog.

## SaaS

Roadie: hosted Backstage.

For: avoid hosting.

## Best Practices

- catalog-info.yaml mandatory
- Auto-discovery
- TechDocs everywhere
- Templates for common
- Plugins for integrations

## Common Mistakes

- Adopt without buy-in
- Stale catalog (entries die)
- No TechDocs
- Few templates

## Quick Refs

```yaml
# Component
kind: Component
spec: { type, owner, lifecycle }

# Template
kind: Template
spec: { steps: [...] }

# API
kind: API
spec: { type: openapi, definition: ... }
```

## Interview Prep

**Mid**: "What's Backstage."

**Senior**: "Catalog design."

**Staff**: "IDP with Backstage."

## Next Topic

→ [T04 — Crossplane & Compositions](T04-Crossplane.md)
