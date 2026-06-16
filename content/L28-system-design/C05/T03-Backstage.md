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

**Junior**: "What is Backstage?" — Spotify's open-source developer portal: a service catalog, software templates (scaffolder), TechDocs, and a plugin system, all behind one UI. It's the front door of an IDP, not the whole platform.

**Mid**: "How does the service catalog stay accurate?" — Each repo carries a `catalog-info.yaml` describing the component (type, owner, lifecycle, dependencies), and Backstage auto-discovers and registers them. Making that file mandatory (enforced in CI) is what keeps the catalog from rotting — a catalog full of dead entries is worse than none because people stop trusting it.

**Senior**: "How would you design the catalog and templates for a 500-service org?" — Model the entity graph deliberately: Components owned by Groups, grouped into Systems, exposing APIs, depending on Resources — so you get an accurate dependency graph and clear ownership for on-call routing. Templates encode the golden paths (scaffold repo + CI + manifests + dashboards + register in catalog), and TechDocs lives in-repo so docs ship with code. Plugins (ArgoCD, PagerDuty, cost, K8s) surface the right operational context on each service page.

**Staff**: "How do you make Backstage actually drive adoption rather than being a pretty catalog nobody updates?" — Wire it into the real workflow so it's load-bearing, not decorative: 'Create new service' goes through Backstage templates (so every new service is born in the catalog), `catalog-info.yaml` is CI-enforced, and the service page is where engineers get their dashboards, docs, and deploy status — so they have a reason to keep it current. I'd treat it as a product, measure adoption, and consider hosted (Roadie) to avoid the ops burden of running Backstage itself. The failure mode is adopting it without buy-in or workflow integration, after which the catalog goes stale and the whole thing is ignored.

## Next Topic

→ [T04 — Crossplane & Compositions](T04-Crossplane.md)
