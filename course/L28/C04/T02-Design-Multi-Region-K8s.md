# L28/C04/T02 — Design a Multi-Region Kubernetes Platform

## Learning Objectives

- Design K8s platform
- Multi-region

## Requirements

### Functional
- Deploy apps to K8s
- Multi-region
- Self-service for devs
- Observability
- Security

### Non-Functional
- 10+ regions
- 1000+ services
- 99.99% availability per service
- < 5 min deploy

## Components

### Control Plane
- Many clusters (per region per env)
- Crossplane / Cluster API
- Centralized control

### Clusters
- EKS / GKE / AKS
- Per region + env
- Multi-AZ

### Networking
- VPC peering
- Transit Gateway
- Service mesh (Istio multi-cluster)

### Storage
- EBS / Persistent Disk
- Cross-region replication for stateful

### Auth
- Workload Identity / IRSA
- Per-team RBAC

### Observability
- Prometheus + Mimir (long-term)
- Loki for logs
- Tempo for traces

### CI/CD
- GitOps (ArgoCD / Flux)
- ApplicationSet for multi-cluster

### Secrets
- Vault central
- External Secrets Operator

## Architecture

```
Devs → Git → ArgoCD (per-cluster)
  ↓
Cluster (per region + env)
  ↑
Vault, Prometheus, Loki (centralized)
```

## Multi-Cluster

ArgoCD ApplicationSet:
- Deploy to all matching clusters
- Per-cluster overrides

## Service Mesh

Istio multi-cluster:
- Cross-cluster service discovery
- mTLS

## Failover

- DNS / Anycast for region failover
- Per-service strategy

## Cost

- Spot for non-critical
- Karpenter
- Right-size pods
- Per-team cost (OpenCost)

## Self-Service

- Backstage portal
- Templated services
- Auto-creates K8s resources

## Security

- Pod Security Standards
- Network Policies (Cilium)
- Image signing
- Vault for secrets

## Scaling

- Many clusters
- Each cluster: HA control plane
- HPA / VPA / Karpenter

## Observability

- Per-cluster Prometheus
- Federated / remote-write to central Mimir
- Loki for logs
- Tempo for traces

## Real Examples

- Snap
- LinkedIn
- Pinterest
- Many FAANGM

## Trade-Offs

- Few big clusters: simpler; bigger blast
- Many small: complex; isolated

## Best Practices

- GitOps
- Standards (templates)
- Centralized observability
- Per-team isolation
- Disaster drills

## Common Mistakes

- One cluster everywhere (huge blast)
- No standards (chaos)
- No central observability
- Manual deploys

## Quick Refs

```
Components:
- Control plane (Crossplane / CAPI)
- Clusters (per region + env)
- Networking (VPC + mesh)
- Auth (IRSA / Vault)
- Observability (Prom + Loki + Tempo)
- CI/CD (ArgoCD)
- Self-service (Backstage)
```

## Interview Prep

**Staff**: "Design K8s platform."

**Principal**: "Multi-region."

## Next Topic

→ [T03 — Design a Metrics / Logging Pipeline at Scale](T03-Design-Metrics-Pipeline.md)
