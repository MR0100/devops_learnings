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

**Junior**: "What is Crossplane?" — A Kubernetes control plane for cloud infrastructure: it adds CRDs so you can declare an RDS instance or S3 bucket as a Kubernetes object, and a provider reconciles it into the real cloud resource — continuously, like any other K8s controller.

**Mid**: "How is Crossplane different from Terraform?" — Both provision cloud resources declaratively, but Crossplane runs as a continuously-reconciling K8s controller (drift is auto-corrected, state lives in the cluster) whereas Terraform applies on demand against a state backend. Crossplane is GitOps-native and fits an IDP cleanly; Terraform is more mature with a far larger provider ecosystem. It's not either/or — many shops keep Terraform for breadth and use Crossplane for the self-service abstraction layer.

**Senior**: "What problem do Compositions and XRDs actually solve?" — They let the platform team publish a *simplified, opinionated* API. An XRD defines an abstract resource (`PostgreSQLInstance` with just `storageGB`), and a Composition implements it as the real cloud resources (RDS + subnet group + parameter group) with org defaults baked in. Developers consume the simple API and never touch RDS specifics — that's the self-service win, and it enforces standards (encryption, backups) by construction rather than by review.

**Principal**: "How do you build a multi-cloud self-service infra platform with this, and what's the catch?" — Define stable abstract APIs (XRDs) that devs depend on, then back each with cloud-specific Compositions (AWS/GCP/Azure) so the developer-facing contract is cloud-agnostic and you can change the implementation underneath. The platform team owns the Compositions; devs only ever create composite resources. The catches I'd flag: devs bypassing the abstraction to use raw managed resources defeats the purpose (lock it down via RBAC), Compositions can grow complex and become their own maintenance burden, and Crossplane is younger than Terraform so provider coverage and edge-case maturity need checking before betting a critical path on it. The abstraction is leverage, but a leaky or over-engineered one costs more than it saves.

## Next Topic

→ Move to [L29 — FAANGM Interview Mastery](../../L29-interview-mastery/README.md)
