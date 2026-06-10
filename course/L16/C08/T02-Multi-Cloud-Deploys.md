# L16/C08/T02 — Multi-Cloud Deployments

## Learning Objectives

- Deploy across clouds
- Choose tooling

## Why Multi-Cloud

- Risk reduction
- Negotiation
- Region availability
- Customer requirements

(See L09/C03.)

## Spinnaker

```
Stage: Deploy
  Cloud: AWS
  Region: us-east-1
Stage: Deploy
  Cloud: GCP
  Region: us-central1
Stage: Deploy
  Cloud: Azure
  Region: eastus2
```

Parallel or sequential.

## ArgoCD

Per-cluster Application:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
spec:
  generators:
  - list:
      elements:
      - cluster: aws-prod
        url: ...
      - cluster: gcp-prod
        url: ...
      - cluster: azure-prod
        url: ...
  template:
    spec:
      destination:
        server: '{{url}}'
      source:
        path: apps/myapp/
```

ApplicationSet deploys to each.

## GitHub Actions

```yaml
deploy:
  strategy:
    matrix:
      cloud: [aws, gcp, azure]
  steps:
    - if: matrix.cloud == 'aws'
      uses: aws-actions/configure-aws-credentials@v4
    - if: matrix.cloud == 'gcp'
      uses: google-github-actions/auth@v2
    - if: matrix.cloud == 'azure'
      uses: azure/login@v2
    - run: deploy.sh
```

Per-cloud.

## Crossplane

```yaml
apiVersion: ec2.aws.crossplane.io/v1beta1
kind: Instance
metadata:
  name: my-vm-aws
spec:
  forProvider: ...
---
apiVersion: compute.gcp.crossplane.io/v1beta1
kind: Instance
metadata:
  name: my-vm-gcp
spec:
  forProvider: ...
```

K8s-native multi-cloud.

## Coordination

Across clouds:
- Sequential (US first, then EU)
- Canary (5% AWS, monitor, then GCP)
- Parallel (all at once)

## DNS-Based Failover

```
Route 53 latency-based → routes to:
  - AWS us-east-1
  - GCP us-central1
  - Azure eastus2
```

For: distribute traffic.

## Per-Cloud Manifests

Differences:
- LoadBalancer (cloud-specific annotations)
- Storage classes
- IAM bindings

Tools:
- Kustomize overlays
- Helm conditionals

```yaml
# Kustomize
overlays/
  aws/kustomization.yaml
  gcp/kustomization.yaml
  azure/kustomization.yaml
```

## Image Replication

Image in each cloud's registry:
```bash
crane copy ecr/myapp:v1 gcr/myapp:v1
crane copy ecr/myapp:v1 acr/myapp:v1
```

Pods pull from local cloud.

## Cross-Cloud DNS

```yaml
# Route 53 record per region
us-east-1.myapp.example.com → AWS
us-central1.myapp.example.com → GCP
eastus2.myapp.example.com → Azure

# Latency LBR
myapp.example.com → nearest
```

## State

Across clouds:
- Database: regional + replication
- Object: per-region with cross-region rules
- Cache: per-region

Avoid: cross-cloud writes (latency).

## Cost Per Cloud

Multi-cloud:
- Higher cost (less commits possible)
- Cross-cloud network
- Tooling complexity

For: justify with strategic value.

## Tools Comparison

| | Spinnaker | ArgoCD ApplicationSet | GitHub Actions matrix |
|---|---|---|---|
| Multi-cloud | yes | yes (per-cluster) | yes (matrix) |
| GitOps | partial | yes | yes (Git-driven) |
| Canary | rich (Kayenta) | with Rollouts | external |
| Maturity | high | high | medium |

## Best Practices

- Same artifact (image) all clouds
- Per-cloud Kustomize / Helm values
- Replicate images per cloud
- Per-cluster monitoring
- Document differences
- Pipeline test across all

## Common Mistakes

- One-size-fits-all manifests
- Image replication missed (cross-cloud pull cost)
- Single point control (Spinnaker single instance)
- Inconsistent deploy across clouds

## Quick Refs

```yaml
# Per-cloud kustomization
base/
overlays/
  aws/
  gcp/
  azure/

# ApplicationSet for multi-cluster
generators:
- list:
    elements:
    - cluster: ...
      url: ...
```

## Interview Prep

**Senior**: "Multi-cloud deploy strategy."

**Staff**: "Tooling choice."

**Principal**: "Multi-cloud platform."

## Next Topic

→ Move to [L16/C09 — Drone & Other CI Tools](../C09/README.md)
