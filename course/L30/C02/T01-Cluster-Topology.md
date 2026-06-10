# L30/C02/T01 — Cluster Topology

## Learning Objectives

- Design multi-cluster
- Multi-region

## Topology

```
us-east-1 (Primary)
├─ EKS cluster (3 AZs)
├─ Apps + DB primary
└─ Aurora primary

us-west-2 (DR)
├─ EKS cluster (3 AZs)
├─ Apps standby
└─ Aurora replica

eu-west-1 (Geo)
├─ EKS cluster (3 AZs)
├─ Apps + cache
└─ Aurora replica
```

## Per Cluster

- 3 AZs
- Karpenter for nodes
- Spot mixed
- Multi-tenant namespaces

## Crossplane

K8s-native provisioning:
- Define cluster CR
- Crossplane creates EKS

## ArgoCD ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
spec:
  generators:
    - clusters: {}
  template:
    spec:
      destination:
        server: '{{server}}'
      source:
        path: apps/
```

Deploy to all clusters.

## Service Mesh

Istio multi-cluster:
- Cross-cluster service discovery
- mTLS

## Networking

- VPC peering or Transit Gateway
- Inter-cluster traffic

## DNS

- Per-region DNS
- Global LB / Route 53 failover

## Documentation

```
/clusters/
  us-east-1.md
  us-west-2.md
  eu-west-1.md

/network/
  topology.md
  routes.md
```

## Best Practices

- IaC for clusters
- GitOps deploy
- Service mesh
- Documented

## Common Mistakes

- Manual cluster creation
- No mesh (no cross-cluster discovery)
- Single ArgoCD (SPOF)

## Quick Refs

```
Pattern: Primary + DR + Geo
IaC: Crossplane / Terraform
Deploy: ArgoCD ApplicationSet
Mesh: Istio multi-cluster
```

## Next Topic

→ [T02 — Federation / Multi-Cluster Service Mesh](T02-Multi-Cluster-Mesh.md)
