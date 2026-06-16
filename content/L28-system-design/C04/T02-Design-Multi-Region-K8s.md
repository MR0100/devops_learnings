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

## Estimation (derived)

Capacity per region must survive losing a region — that's the headroom equation, derived:
```
total_peak        = 100,000 req/s   (assumed)
active_regions    = 3
steady_per_region = 100,000 / 3 ≈ 33k req/s
```
But if one of three regions fails, its load redistributes to the survivors:
```
load_after_loss   = total / (regions − 1) = 100,000 / 2 = 50k req/s per survivor
required_headroom = 50k / 33k ≈ 1.5×
```
So each region runs at ~66% of its provisioned capacity in steady state — provision **1.5× steady load** so any single region loss is absorbed without shedding traffic. (For N active regions the factor is N/(N−1): tighter as N grows — 4 regions need only 1.33×.)

Cluster count is derived from blast-radius policy, not picked arbitrarily:
```
clusters = regions × environments × (shards for blast-radius isolation)
```
~10 regions × {prod, staging} × ~2 prod shards ≈ dozens of clusters → you need fleet management (Cluster API / Crossplane), not hand-rolled clusters.

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

## Deep Dive: Failover & the Data Layer

The hard part of multi-region isn't the stateless tier — it's state. Split the decision:
- **Stateless services**: trivially active-active. Route 53 latency/health policy or anycast shifts traffic on a failed health check; surviving regions absorb it (sized via the 1.5× headroom above). Failover time ≈ health-check interval + DNS TTL, so keep TTLs low (30–60s) or use anycast for sub-second.
- **Stateful (the real cost)**: you cannot have synchronous, low-latency, multi-region writes — cross-region RTT is 50–200 ms (CAP/PACELC, C02/T04). Choose explicitly:
  - **Single write region + async global replica** (Aurora Global): fast local reads everywhere, one write region. Region loss = **promote a replica** (RPO seconds, RTO minutes, often manual to avoid split-brain).
  - **Active-active writes** (Spanner / DynamoDB Global Tables): write anywhere, but you pay consensus latency or accept LWW conflict resolution.

State the failover runbook: detect (health check) → shift stateless traffic (DNS/anycast) → promote DB replica if the write region is lost → reconcile. Practice it with game days; a failover path you've never exercised will fail when you need it.

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

**Senior**: "Why not just run one giant cluster across regions?" — Blast radius and the control plane. One cluster means one etcd quorum (which can't span high-latency regions) and a single failure domain — one bad upgrade or noisy tenant takes down everything. Many smaller clusters (per region + env) isolate failures; the cost is fleet management, which is why you bring in Cluster API / Crossplane and GitOps.

**Staff**: "Design a multi-region Kubernetes platform; how much capacity per region?" — Active-active stateless tier behind Route 53/anycast, GitOps (ArgoCD ApplicationSet) per cluster, centralized observability via remote-write to Mimir, and a service mesh for cross-cluster mTLS. Crucially I size each region at N/(N−1) of steady load — 1.5× for three regions — so losing one region is absorbed without shedding traffic, and I separate the stateless failover (DNS) from the stateful one (DB replica promotion).

**Principal**: "us-east-1 just went dark — walk me through what happens." — Health checks fail and Route 53 stops routing there; the surviving regions absorb the load using the pre-provisioned 1.5× headroom. If us-east-1 held the write primary (Aurora Global), we promote a replica in another region — RPO is seconds of async lag, RTO a few minutes, kept semi-manual to avoid split-brain. GitOps means the surviving clusters already run the same manifests, so there's nothing to deploy. The failure mode I most want to have rehearsed is the DB promotion, because an untested failover is the one that bites.

## Next Topic

→ [T03 — Design a Metrics / Logging Pipeline at Scale](T03-Design-Metrics-Pipeline.md)
