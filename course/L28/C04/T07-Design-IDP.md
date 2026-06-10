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

## Platform Team

- Builds IDP
- Maintains
- Onboarding support

For: small team scales many devs.

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

**Staff**: "Design IDP."

**Principal**: "Platform engineering."

## Next Topic

→ Move to [L28/C05 — Platform Engineering](../C05/README.md)
