# L30/C02/T02 — Federation / Multi-Cluster Service Mesh

## Learning Objectives

- Federate clusters
- Cross-cluster mesh

## Federation

### Cluster Federation
- API server federation (deprecated)
- ArgoCD: per-cluster
- KubeFed (limited adoption)

### Multi-Cluster Service Mesh
- Istio multi-cluster
- Linkerd multi-cluster
- Cilium cluster mesh

## Istio Multi-Cluster

Modes:
- Primary-Remote
- Multi-Primary

```bash
istioctl install --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1
```

## Cross-Cluster Service Discovery

Service in cluster A reachable from cluster B:
- mTLS
- DNS or env
- Mesh-aware

```yaml
# Istio ServiceEntry
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
spec:
  hosts:
    - foo.cluster-b.local
  location: MESH_INTERNAL
  ports:
    - number: 80
      protocol: HTTP
  endpoints:
    - address: foo.cluster-b.local
```

## Why a Mesh (and Which One)

Without a mesh, a service in cluster A reaching one in cluster B means
hand-managed DNS, no shared identity, and TLS you wire yourself. A multi-cluster
mesh gives you three things for free across the cluster boundary: **service
discovery** (B's services look local to A), **mTLS** (encrypted, identity-based
traffic), and **locality-aware failover** (prefer-local, fail-to-remote). That
last one is what makes the C02/T03 failover demo possible without DNS games.

### Trade-offs Between the Options

- **Istio multi-cluster** — most features (rich traffic policy, locality LB,
  multi-primary HA) but the heaviest to operate; sidecars add latency/resource
  overhead (ambient mode reduces this).
- **Linkerd multi-cluster** — simplest, lowest overhead, opinionated; fewer
  knobs, which is a feature for most teams.
- **Cilium Cluster Mesh** — operates at L3/L4 via eBPF (no sidecar), so pod IPs
  are routable across clusters with very low overhead; less L7 policy richness
  than Istio.

For the capstone, picking *and justifying* one (e.g. "Istio for the locality LB
I need to demo failover") is the senior signal — there's no single right answer.

## Cilium Cluster Mesh

```bash
cilium clustermesh enable
cilium clustermesh connect --destination-context other-cluster
```

Pod IPs become routable across clusters via eBPF — no sidecar, low overhead.

## Failover

Service in cluster A unhealthy:
- Mesh routes to cluster B
- Locality-based LB

```yaml
trafficPolicy:
  localityLbSetting:
    enabled: true
    failover:
      - from: us-east-1
        to: us-west-2
```

## Use Cases

### Geographic
Users → nearest cluster.

### Failover
Cluster down → other.

### Multi-Tenant
Tenant per cluster.

## Best Practices

- One control plane per cluster
- Federated config (Git-based)
- mTLS across
- Locality LB

## Common Mistakes

- Tightly coupled (single ArgoCD for all)
- No mTLS cross-cluster
- Manual config sync

## Acceptance Criteria

- A shared trust root so workload identity (mTLS) spans both clusters
- A service in cluster A can call a service that only exists in cluster B, by
  its normal name, encrypted
- Locality LB demonstrably prefers local endpoints and fails over to the remote
  cluster when local ones are unhealthy

## Quick Refs

```
Mesh: Istio (most features) / Linkerd (simplest) / Cilium (eBPF, no sidecar)
Discovery: ServiceEntry / Cluster Mesh    Failover: Locality LB
Shared root CA → mTLS across clusters      GitOps: ArgoCD ApplicationSet
```

## Interview Prep

**Junior**: "What does a service mesh do?" — It handles service-to-service
networking concerns — discovery, mutual TLS, retries, traffic routing — outside
the application, usually via a sidecar proxy. The app just makes a normal call;
the mesh secures and routes it.

**Mid**: "What does going *multi-cluster* with the mesh add?" — It extends
discovery, mTLS, and traffic policy across the cluster boundary. A service in
one cluster can call a service in another by its normal name, encrypted with a
shared identity, and the mesh can do locality-aware load balancing — keep
traffic local but fail over to the other cluster's endpoints when the local ones
are unhealthy.

**Senior**: "Istio vs Linkerd vs Cilium for multi-cluster — how do you choose?"
— Istio has the richest traffic management and locality failover but is the most
to operate; I'd pick it when I genuinely need that policy surface (like the
locality LB for a failover demo). Linkerd is the simplest and lowest-overhead —
a great default when you don't need Istio's knobs. Cilium Cluster Mesh works at
L3/L4 over eBPF with no sidecar, so it's the lowest-overhead path to
cross-cluster pod connectivity, at the cost of less L7 richness. The decision is
driven by which capabilities you actually need versus the operational cost
you're willing to carry.

**Staff**: "A team wants a multi-cluster mesh mainly for cross-region failover.
Is that the right tool?" — Sometimes, but I'd separate the concerns. A mesh
gives you in-mesh, request-level locality failover with identity preserved — great
for east-west traffic between services. But user-facing, north-south failover
(an entire region down) is usually better handled at DNS/anycast (Route 53,
Global Accelerator) because it doesn't depend on the failing region's mesh
control plane being reachable. So the staff answer is: use the mesh for
east-west mTLS and locality routing, and a global traffic manager for north-south
region failover — and don't make the mesh a single point of failure for the very
event it's supposed to survive.

## Next Topic

→ [T03 — Cross-Region Failover](T03-Multi-Cluster-Failover.md)
