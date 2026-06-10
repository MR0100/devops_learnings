# L30/C04/T03 — Self-Service Provisioning

## Learning Objectives

- Self-service infra
- No tickets

## Goal

Dev:
- Need DB → click button → get DB

No:
- Ticket
- Wait
- Manual setup

## Crossplane

```yaml
apiVersion: example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: my-app-db
spec:
  parameters:
    storageGB: 100
```

Composition translates to AWS RDS.

## Backstage Integration

Template creates Crossplane resource:
```yaml
steps:
  - id: create-resource
    action: kubernetes:apply
    input:
      manifest: |
        apiVersion: example.org/v1alpha1
        kind: PostgreSQLInstance
        metadata:
          name: ${{ parameters.name }}
        spec:
          ...
```

## Workflow

```
Backstage UI
  → Pick template "PostgreSQL DB"
  → Fill: size, name
  → Submit
  → Backstage creates Crossplane CR
  → Crossplane creates AWS RDS
  → DB ready
  → Connection info → Vault → app reads
```

## Without Crossplane

Alternative:
- Argo Workflows
- Terraform Cloud API
- Custom controllers

## Policy

```yaml
# Limit dev resources
kind: ResourceQuota
spec:
  hard:
    pods: "10"
    persistentvolumeclaims: "5"
```

For: prevent runaway.

## Cost Visibility

- Tag created resources
- Per-team
- Per-service

## Auto-Cleanup

For ephemeral:
```yaml
spec:
  ttl: 7d   # auto-destroy after
```

For: dev environments.

## Best Practices

- Self-service common needs
- Quotas
- Cost visible
- Auto-cleanup ephemeral
- Document

## Common Mistakes

- Too rigid (defeats purpose)
- No quotas
- No cost tracking
- Permanent ephemeral

## Quick Refs

```
Tools: Crossplane / Argo / TF Cloud
Quotas: ResourceQuota
TTL: auto-cleanup
Cost: tagging
```

## Next Topic

→ Move to [L30/C05 — Project 5: Cost-Optimized Spot-Heavy Workload Platform](../C05/README.md)
