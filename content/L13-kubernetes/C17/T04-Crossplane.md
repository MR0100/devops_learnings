# L13/C17/T04 — Crossplane

## Learning Objectives

- Use Crossplane for IaC
- Provision cloud via K8s API

## Crossplane

K8s control plane for cloud:
- Cloud resources as CRs
- K8s API manages cloud
- GitOps-friendly
- Reusable abstractions

## Comparison

| | Terraform | Crossplane |
|---|---|---|
| Style | CLI/Cloud | K8s-native |
| State | TF state | etcd |
| Reconciliation | One-shot | Continuous |
| API | HCL | K8s YAML |
| Distribution | Modules | Configurations (Helm-style) |

For K8s-native + GitOps: Crossplane.
For multi-tool: Terraform.

## Install

```bash
helm install crossplane crossplane-stable/crossplane -n crossplane-system --create-namespace
```

## Providers

Install per cloud:
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.40
```

Plus auth:
```bash
kubectl create secret generic aws-creds -n crossplane-system --from-file=credentials=./creds
```

```yaml
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-creds
      key: credentials
```

## Cloud Resources

Apply RDS, S3, etc., as CRs:
```yaml
apiVersion: rds.aws.crossplane.io/v1beta1
kind: DBInstance
metadata:
  name: my-db
spec:
  forProvider:
    region: us-east-1
    dbInstanceClass: db.t3.micro
    allocatedStorage: 20
    engine: postgres
    masterUsername: admin
    masterUserPassword:
      generateRandom: true
  providerConfigRef:
    name: default
```

Crossplane provisions RDS instance.

## Composite Resource (XR)

User-facing abstraction. Composed of multiple managed resources:

```yaml
apiVersion: example.org/v1
kind: WebDatabase
metadata:
  name: my-app
spec:
  parameters:
    storageGB: 50
    region: us-east-1
```

Internally creates:
- RDS DBInstance
- DBSubnetGroup
- Security Group
- Secret

User just sees WebDatabase.

## Composition

Templates how XR becomes managed resources:
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: web-database
spec:
  compositeTypeRef:
    apiVersion: example.org/v1
    kind: WebDatabase
  resources:
  - name: db
    base:
      apiVersion: rds.aws.crossplane.io/v1beta1
      kind: DBInstance
      spec:
        forProvider:
          dbInstanceClass: db.t3.micro
          engine: postgres
    patches:
    - fromFieldPath: spec.parameters.storageGB
      toFieldPath: spec.forProvider.allocatedStorage
    - fromFieldPath: spec.parameters.region
      toFieldPath: spec.forProvider.region
```

Like Helm template but for cloud.

## XRD (XR Definition)

Define CR API for users:
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: webdatabases.example.org
spec:
  group: example.org
  names:
    kind: WebDatabase
    plural: webdatabases
  claimNames:
    kind: WebDatabaseClaim
    plural: webdatabaseclaims
  versions:
  - name: v1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            properties:
              parameters:
                properties:
                  storageGB:
                    type: integer
                  region:
                    type: string
```

User applies WebDatabaseClaim; gets infrastructure.

## Claims

Namespaced version of XR. For app teams:
```yaml
apiVersion: example.org/v1
kind: WebDatabaseClaim
metadata:
  name: my-claim
  namespace: my-app
spec:
  parameters:
    storageGB: 100
    region: us-east-1
```

Crossplane creates underlying.

## Use Cases

### Platform Team
Define standard offerings:
- WebDatabase (RDS + networking + security)
- Cache (ElastiCache + SG + subnets)
- Bucket (S3 + lifecycle + encryption)

App teams just claim. Don't see Terraform / cloud details.

### Multi-Cloud
Same XR; per-cloud Composition:
- Composition.aws: → RDS
- Composition.gcp: → Cloud SQL

User claims; platform routes.

### Multi-Region
Per-region Composition.

## Comparison: Terraform Module

| | Crossplane Composition | TF Module |
|---|---|---|
| User API | K8s CR | TF block |
| Distribution | Configuration Package | Module repo |
| State | etcd | Backend |
| Reconciliation | Continuous | One-shot |
| Self-service | K8s native | Terraform CLI |

For K8s-native self-service: Crossplane.

## Providers Available

- AWS, Azure, GCP
- Helm (deploy chart)
- Kubernetes (manage K8s)
- GitHub (repo creation)
- Vault
- Datadog
- ...

For: anything with API.

## Drift Reconciliation

Crossplane continuously reconciles:
- Cloud resource changed externally
- Crossplane detects
- Reverts to CR-defined state

Like K8s controllers. Vs Terraform (drift detection on demand).

## GitOps + Crossplane

CRs in Git → ArgoCD → applied → Crossplane provisions cloud.

For: GitOps for infrastructure.

## Operations

```bash
# Resources
kubectl get providers
kubectl get providerconfigs
kubectl get xrd
kubectl get composition

# Cloud resources
kubectl get dbinstances
kubectl get buckets

# Claims
kubectl get webdatabaseclaims -A
```

## Production Considerations

- Provider rate limits (cloud API)
- Crossplane uptime (cluster availability affects cloud ops)
- Secrets management (provider creds)
- RBAC (who can claim what)
- Backup of Crossplane CRs

## When Crossplane

- K8s-first organization
- Want self-service platform
- GitOps for infrastructure
- Multi-cloud abstractions

## When Terraform

- Existing TF investment
- Outside K8s context
- Mature ecosystem
- Specific provider features

For most: pick one. Some combine (Crossplane for app infra; TF for foundational).

## Limitations

- Provider coverage less mature than TF
- Some cloud features not yet supported
- Crossplane up = cloud ops; downtime risks

## Compositions Library

Upbound (commercial) provides:
- Configurations (pre-built XRs)
- Marketplace
- Cloud-managed control plane

For organizations wanting maintained.

## Best Practices

- XRs for app teams (simple)
- Compositions for platform team (rich)
- Separate control plane cluster (HA, isolated)
- Backup XR / Composition definitions
- Test compositions before publishing
- Monitor Crossplane health

## Common Mistakes

- Putting Crossplane in workload cluster
- No HA control plane
- Wide credentials
- Forget claim RBAC

## Multi-Tenant

Per-team namespaces:
- Each team has Claims in own ns
- Different Compositions per team
- RBAC controls

## Inspection

```bash
# All resources for an XR
kubectl get xresource my-xr -o yaml

# Composed resources
kubectl get managed
```

## Quick Refs

```bash
# Install
helm install crossplane crossplane-stable/crossplane -n crossplane-system

# Provider
kubectl apply -f provider-aws.yaml

# XRD + Composition
kubectl apply -f xrd.yaml -f composition.yaml

# Claim
kubectl apply -f claim.yaml

# Get status
kubectl describe webdatabaseclaim my-claim
```

## Interview Prep

**Mid**: "Crossplane vs Terraform."

**Senior**: "Composition design for platform."

**Staff**: "Self-service infrastructure platform."

## Next Topic

→ Move to [L13/C18 — Cost Optimization](../C18/README.md)
