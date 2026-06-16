# L14 — Service Mesh

## Overview

A service mesh manages service-to-service communication: mTLS, retries, traffic shifting, observability. The layer above Kubernetes. Heavyweight; not always justified.

**6 chapters, 12 topics.**

## Chapter Map

### [C01](C01/) — Service Mesh Concepts
- T01 What Problems Does a Mesh Solve
- T02 Data Plane vs Control Plane
- T03 Sidecar vs Sidecarless (Ambient Mesh)

### [C02](C02/) — Istio
- T01 Architecture (istiod, Envoy)
- T02 Traffic Management (VirtualService, DestinationRule, Gateway)
- T03 Security (mTLS, AuthorizationPolicy)
- T04 Observability
- T05 Ambient Mode

### [C03](C03/) — Linkerd
- T01 Architecture (linkerd2-proxy in Rust)
- T02 Simpler Tradeoffs vs Istio

### [C04](C04/) — Consul Connect
- T01 HashiCorp Stack Integration

### [C05](C05/) — Envoy Standalone
- T01 Filters, Clusters, Listeners
- T02 xDS APIs

### [C06](C06/) — Choosing a Mesh
- T01 When You Don't Need One
- T02 Cilium Service Mesh (eBPF)

## What a Mesh Buys You

- **mTLS by default** between services
- **Retries, timeouts, circuit breaking** without app changes
- **Traffic splitting** (canary, A/B) without app changes
- **L7 routing** based on headers, methods, paths
- **Observability** — uniform metrics, traces from sidecars
- **Policy** — service-to-service authorization

## What a Mesh Costs

- CPU & memory overhead per pod (sidecar ~50–200MB)
- Operational complexity (control plane, certs)
- Debugging is harder (more hops)
- Upgrades coordinated
- Latency added (small but non-zero)

## Sidecar vs Ambient (Sidecarless)

| | Sidecar | Ambient |
|---|---|---|
| Topology | Sidecar per pod | Per-node proxy (ztunnel) + waypoint proxies |
| Overhead | Higher (one per pod) | Lower |
| Maturity | Mature | Newer |
| Use | Default | Coming |

## Mesh Comparison

| | Istio | Linkerd | Cilium SM |
|---|---|---|---|
| Data plane | Envoy | linkerd2-proxy (Rust) | Envoy + eBPF |
| Footprint | Heavy | Light | Light |
| Features | Most | Focused | eBPF-native |
| Best for | Full features | Simplicity + security | eBPF-curious orgs |

## Interview Themes

- "What does a service mesh do?"
- "When would you NOT use a mesh?"
- "Compare sidecar vs ambient mode"
- "Compare Istio and Linkerd"

## Next

→ [L15 — CI/CD Fundamentals & Pipeline Design](../L15-cicd-fundamentals/README.md)
