# L14/C01 — Service Mesh Concepts

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Problems-Solved.md) | What Problems Does a Mesh Solve | 1 hr |
| [T02](T02-Data-Control-Plane.md) | Data Plane vs Control Plane | 0.5 hr |
| [T03](T03-Sidecar-Ambient.md) | Sidecar vs Sidecarless (Ambient Mesh) | 1 hr |

## What a Service Mesh Solves

In a microservices architecture, every service-to-service call has cross-cutting concerns:

| Concern | What it Means |
|---|---|
| **mTLS** | Encrypted, authenticated service-to-service |
| **Retries** | Auto-retry transient failures |
| **Timeouts** | Bound how long calls take |
| **Circuit Breaking** | Stop calling a failing dependency |
| **Load Balancing** | Distribute calls (round-robin, least-conn, locality-aware) |
| **Observability** | Uniform metrics, traces, logs |
| **Traffic Shifting** | Canary, A/B, blue/green at L7 |
| **Authorization** | Service-to-service policy |
| **Rate Limiting** | Per-caller quotas |

Without a mesh, each service implements these (or skips them). With a mesh, the network handles them.

## Architecture

```
[Control Plane]
   - Config: who can talk to whom, routing, mTLS policy
   - Distributes config to sidecars
   - Aggregates telemetry

         │ xDS (Envoy config protocol)
         ▼

[Data Plane]
   - Sidecar proxies (Envoy, linkerd2-proxy)
   - Intercept ALL traffic from/to the app
   - Apply policy (mTLS, retries, etc.)
   - Emit metrics/traces
```

The app code is unchanged. The mesh inserts a sidecar between app and network.

## Data Plane

The proxy that handles each request. Almost always **Envoy** (for Istio, Consul Connect; linkerd2 uses a custom Rust proxy).

Per pod: Envoy intercepts traffic via iptables/eBPF rules. Applies config from the control plane.

## Control Plane

Distributes configuration. Examples: istiod (Istio), Linkerd Controllers, Consul, Cilium agent.

### xDS APIs
Envoy uses xDS (dynamic discovery) to receive config:
- CDS — Cluster Discovery
- EDS — Endpoint Discovery
- LDS — Listener Discovery
- RDS — Route Discovery
- SDS — Secret Discovery

Control plane implements these as gRPC servers.

## Sidecar Pattern

Each pod has 2 containers:
- App container
- Sidecar proxy (Envoy, ~50-100 MB memory)

iptables rules redirect pod's network traffic through the sidecar.

### Pros
- Per-pod policy
- Works across orchestrators
- Mature

### Cons
- Memory/CPU overhead per pod
- Adds latency (small but non-zero)
- Coupled to pod lifecycle
- Hard to upgrade sidecars at scale

## Ambient Mesh (Istio's Sidecarless)

Two layers:
- **ztunnel** — per-node L4 proxy for mTLS
- **waypoint** — optional L7 proxy per namespace/service

No sidecars in pods. Lower overhead.

### Pros
- Lower per-pod overhead
- Easier upgrades (node-level)
- Migrate one service at a time

### Cons
- Newer; less battle-tested
- Slightly different model

## Cilium Service Mesh (eBPF-based)

Uses eBPF in the kernel to do mesh functions without sidecars:
- L4 routing without proxy
- mTLS via eBPF (newer)
- Envoy embedded at node level for L7 features
- Lower overhead, faster than sidecar meshes for L4

## When You Need a Mesh

| Yes | No |
|---|---|
| 50+ microservices | Few services (< 10) |
| Multi-language fleet (each service implementing retries differently) | Single language, shared libs |
| Need mTLS everywhere | Network-perimeter trust adequate |
| Sophisticated traffic management (canary, mirror) | Simple deploys are enough |
| Multiple teams, no shared library | Single team, central platform |

> Don't adopt a mesh because everyone is. Adopt when you've felt the pain a mesh solves.

## Cost of a Mesh

- **Operational**: control plane, sidecar injection, upgrades, debugging
- **Performance**: ~1-5ms latency per hop; 50-200 MB memory per pod (sidecar)
- **Complexity**: extra layer to debug
- **Hiring**: deep mesh expertise is rare

For an org of 200+ engineers with 100+ services, mesh is usually worth it. Under that, often not.

## Alternatives

Before adopting a mesh, consider:
- **Library-based** (e.g., gRPC built-in retry; Resilience4j) — language-specific but no infra
- **API Gateway only** — for external traffic; not S2S
- **Network policy + DNS** — basic isolation without mesh complexity
- **Service mesh-lite**: just mTLS via SPIFFE/SPIRE

## Interview Themes

- "What problems does a service mesh solve?"
- "Compare sidecar and ambient mode"
- "When NOT to use a mesh"
- "How does iptables redirect work?"
- "xDS — what is it?"
