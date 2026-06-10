# L28/C05/T04 — Crossplane & Compositions

## Learning Objectives

- Use Crossplane
- Self-service infra

## Crossplane

K8s control plane for cloud:
- CRDs for cloud resources
- Provider per cloud
- Compositions for abstractions

## Install

```bash
helm install crossplane crossplane-stable/crossplane \
  -n crossplane-system --create-namespace
```

## Provider

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.x
```

## Resources

```yaml
apiVersion: rds.aws.crossplane.io/v1beta1
kind: DBInstance
metadata:
  name: my-db
spec:
  forProvider:
    region: us-east-1
    dbInstanceClass: db.t3.medium
    masterUsername: admin
```

Crossplane creates AWS RDS.

## Compositions

Abstract:
```yaml
apiVersion: example.org/v1alpha1
kind: PostgreSQLInstance
spec:
  parameters:
    storageGB: 100
```

Composition translates to AWS RDS + others.

For: dev simplicity.

## XRD

CompositeResourceDefinition:
- Define abstract API
- Compositions implement

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: postgresqlinstances.example.org
spec:
  group: example.org
  names:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                parameters:
                  type: object
                  properties:
                    storageGB:
                      type: integer
```

## Composition

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: aws-postgresql
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: PostgreSQLInstance
  resources:
    - name: db
      base:
        apiVersion: rds.aws.crossplane.io/v1beta1
        kind: DBInstance
        spec: ...
      patches:
        - fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
```

For: implementation behind abstraction.

## Dev Experience

Dev:
```yaml
kind: PostgreSQLInstance
spec:
  parameters:
    storageGB: 100
```

Doesn't know AWS RDS specifics.

For: self-service.

## Multi-Cloud

Different compositions per cloud:
```yaml
# AWS composition
# GCP composition
# Azure composition
```

Same abstract; cloud-agnostic developer.

## vs Terraform

| | Crossplane | Terraform |
|---|---|---|
| Mode | K8s declarative | imperative |
| State | K8s | backend |
| Reconciliation | continuous | apply only |
| Multi-cloud | native | yes |
| Maturity | growing | high |

## When Crossplane

- K8s-native
- Self-service abstractions
- GitOps for infra

## When Terraform

- Established
- Many providers
- Strong community

## Best Practices

- XRD for stable API
- Compositions per cloud
- Devs use XRs (composite resources)
- Platform team maintains compositions

## Common Mistakes

- Devs use raw resources (bypass abstraction)
- No compositions (defeats purpose)
- Complex compositions (hard maintain)

## Quick Refs

```yaml
Provider: per cloud
ManagedResource: cloud resource
XRD: abstract API
Composition: implementation
XR (Composite Resource): user-facing
```

## Interview Prep

**Senior**: "What's Crossplane."

**Staff**: "Self-service infra."

**Principal**: "Platform abstractions."

## Next Topic

→ Move to [L29 — FAANGM Interview Mastery](../../L29/README.md)
