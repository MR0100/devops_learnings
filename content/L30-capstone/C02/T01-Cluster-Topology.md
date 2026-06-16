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

## Why This Topology

The whole capstone exists to prove you understand **true multi-region** — not
just multi-AZ. Multi-AZ survives a datacenter failure; multi-region survives an
entire AWS region having a bad day (which has happened). The cost is real
complexity — cross-region state, data sovereignty, and a fatter bill — so the
project is as much about *justifying* the topology as building it.

### Primary / DR / Geo — and the Trade-offs

- **Primary (us-east-1)** — takes writes; everything else replicates from it.
- **DR (us-west-2)** — warm standby; promoted on a primary-region failure. The
  trade-off vs. active-active is simplicity (one writer, no conflict resolution)
  at the cost of an RTO/RPO window during promotion.
- **Geo (eu-west-1)** — serves European users locally for latency and often for
  data-residency reasons; reads locally, writes may still route to primary.

Active-active everywhere sounds better but buys you multi-region write conflicts
and a much harder consistency story; most teams start primary/DR and only go
active-active where the business case (latency, residency) demands it.

## Per Cluster

- 3 AZs (AZ-level HA inside each region)
- Karpenter for nodes
- Spot mixed (cost — see C05)
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

## Cost & Time Estimate

- **Time**: ~3–4 days to two healthy clusters with cross-cluster discovery;
  failover demo on top of that
- **Cost**: ~$600/month if left running (2 EKS control planes ~$146, 6×
  m6i.large ~$300, global DB ~$100, cross-region egress $20–50). **Bring it up
  for the demo, record it, tear it down** — do not leave multi-region running.

## Acceptance Criteria

- Two clusters in two regions, both provisioned from the same IaC/templates
- One ArgoCD ApplicationSet deploys the app to both with no per-cluster drift
- Cross-cluster service discovery works (a service in east is reachable from
  west via the mesh)
- The topology choice is documented with its RTO/RPO and cost implications

## Quick Refs

```
Pattern: Primary + DR + Geo (multi-region, not just multi-AZ)
IaC: Crossplane / Terraform     Deploy: ArgoCD ApplicationSet
Mesh: Istio multi-cluster       Bring up → demo → tear down (~$600/mo)
```

## Interview Prep

**Junior**: "What's the difference between multi-AZ and multi-region?" — Multi-AZ
spreads across availability zones inside one region, surviving a datacenter
failure. Multi-region spreads across whole regions, surviving an entire region
going down. Multi-region is more resilient but more complex and expensive,
mainly because of cross-region data and latency.

**Mid**: "Why primary/DR instead of active-active everywhere?" — Primary/DR has
a single writer, so there are no cross-region write conflicts to resolve — much
simpler. The cost is an RTO/RPO window while you promote the standby on failure.
Active-active gives lower failover impact but forces you to handle multi-region
writes and conflict resolution, which is a big jump in complexity. I'd start
primary/DR and only go active-active where latency or data-residency
requirements justify it.

**Senior**: "How do you keep two clusters from drifting apart?" — Provision both
from the same IaC modules and deploy with a single ArgoCD ApplicationSet
generated across clusters, so 'the app' is declared once and reconciled
everywhere. Per-cluster differences (region name, DB endpoint) are
parameterized, not forked. That way 'works in east, broken in west' can't happen
from config skew, and adding a third region is a config entry, not a rebuild.

**Staff**: "How do you decide whether multi-region is even worth it for a given
service?" — It's a cost/benefit and requirements conversation, not a default.
Multi-region roughly doubles infra cost and adds real operational burden
(cross-region state, failover testing, egress). I'd justify it only where the
business needs it: a hard availability SLA that a single region can't meet, a
latency requirement for a distant user base, or a data-residency/regulatory
mandate. For everything else, multi-AZ with a tested restore is usually the
right resilience-per-dollar. Stating *that* judgment — and being willing to say
'no, multi-AZ is enough here' — is what separates a staff answer from a
résumé-driven one.

## Next Topic

→ [T02 — Federation / Multi-Cluster Service Mesh](T02-Multi-Cluster-Mesh.md)
