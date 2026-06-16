# L14/C06 — Choosing a Mesh

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-When-Not-Needed.md) | When You Don't Need One | 0.5 hr |
| [T02](T02-Cilium-Mesh.md) | Cilium Service Mesh (eBPF) | 1 hr |

## When You Don't Need a Mesh

Honest assessment first. You DON'T need a mesh if:

- < 20 microservices
- Single-language stack with built-in retry/timeout
- TLS via ingress + private network is sufficient
- Observability via app-level OTel is in place
- No need for L7 traffic shifting at infrastructure level

Adopting a mesh too early adds complexity for little gain.

### Cheaper Alternatives

- **OpenTelemetry SDK** for observability
- **gRPC built-in** retries + timeouts
- **Resilience4j / Polly** libraries
- **NetworkPolicy** for service-level isolation
- **cert-manager** for TLS at ingress

## Cilium Service Mesh (eBPF)

Cilium is a CNI plugin. Its service mesh feature replaces sidecars with eBPF in the kernel.

### Architecture
```
[Cilium Agent] (DaemonSet, one per node)
   - Manages eBPF programs
   - L4 routing without proxy
   - L7 features via Envoy (one per node, optional)

[eBPF programs in kernel]
   - mTLS (via WireGuard or IPsec)
   - L4 load balancing
   - Network policy enforcement
   - Observability
```

### Advantages
- **No sidecars** → much lower memory/CPU per pod
- **L4 in kernel** → minimal latency
- **L7 via Envoy at node level** (when needed) — shared across pods on that node
- **Network policy + mesh in one tool**

### Limitations
- Newer; less mature than Istio
- L7 still requires Envoy (so when you use L7, you're back to Envoy)
- Tight coupling to Cilium as CNI

### When Cilium Mesh
- Already using Cilium CNI
- Want lower overhead than sidecars
- L4-heavy workloads
- Multi-cluster needs (Cluster Mesh)

## Decision Matrix

| Need | Pick |
|---|---|
| Rich L7 features, mature | **Istio** |
| Simplicity over features | **Linkerd** |
| Hybrid VM + K8s | **Consul Connect** |
| Already on Cilium CNI | **Cilium Service Mesh** |
| Just L7 LB, no mesh needs | **Envoy / Nginx** |
| < 10 services | **No mesh** |

## Mesh Adoption Anti-Patterns

- **Adopting before need is felt** — adds complexity preemptively
- **Mesh as cure for poor observability** — instrument apps first
- **Mesh as cure for poor authz** — fix app-level authz first
- **Force on every service** — opt-in per service initially
- **Underestimating ops cost** — staffing a mesh is real work

## Adoption Strategy (When You Do Adopt)

1. **Start with a single service**: enable mesh; measure overhead
2. **Use PERMISSIVE mTLS initially** so non-meshed traffic still flows
3. **Migrate one namespace at a time**
4. **Move to STRICT mTLS** only when all migrated
5. **Enable advanced features incrementally** (canary, AuthorizationPolicy)
6. **Train on-call on mesh debugging** before stake gets high

## Cost Awareness

### Per-Sidecar
- Memory: 50-200 MB
- CPU: 50-200 mCPU baseline
- Latency: 1-5 ms additional per hop

### Aggregate (10K pods example)
- Memory: 1 TB (for Envoy sidecars alone)
- CPU: 100-200 vCPU baseline
- That's $100K+/year of infra just for sidecars

Ambient or Cilium can cut this dramatically.

## Multi-Cluster Mesh

For multi-region or multi-cluster setups:

- **Istio multi-cluster** — primary or shared control plane modes
- **Linkerd multi-cluster** — service mirroring across clusters
- **Cilium ClusterMesh** — flat connectivity across clusters
- **Consul multi-DC** — federated

All add complexity. Use only when truly needed (cross-region traffic, etc.).

## Interview Themes

- "When NOT to use a mesh"
- "Compare mesh data plane choices"
- "Cilium vs Istio"
- "Migration strategy to mesh"
- "Cost of running a mesh at scale"
