# L14/C01/T03 — Sidecar vs Sidecarless (Ambient Mesh)

## Learning Objectives

- Compare sidecar and ambient modes
- Decide

## Sidecar Mode (Standard)

Sidecar proxy injected into every pod:
```
Pod = app + Envoy
```

- Per-pod resources
- Full features
- Mature

## Sidecarless (Ambient)

Istio ambient mode:
```
Node level:
  ztunnel (1 per node) → handles L4 mTLS for all pods on node

Identity level:
  Waypoint proxy → L7 features per service/account
```

For: lower overhead, opt-in L7.

## Comparison

| | Sidecar | Ambient |
|---|---|---|
| Topology | Per-pod | Per-node ztunnel + optional waypoint |
| Overhead per pod | 50-200 MB | ~0 |
| Overhead per node | (sum of pods) | ztunnel ~100 MB |
| Pod restart for upgrade | Yes | No |
| L4 (mTLS, auth) | yes | yes |
| L7 (routing, retries) | yes | yes (waypoint) |
| Maturity | High | Beta-GA recent |

## Ambient Layers

### ztunnel (Layer 4)
- Per node
- Handles mTLS
- Authorization (L4)
- Cheap
- All pods on node use one

### Waypoint Proxy (Layer 7)
- Per service or service account
- L7 (HTTP routing, retries)
- Optional
- Deploy as standard pod

For: L7 only when needed; cheap L4 always.

## Why Ambient

- Cost: less RAM (no sidecar per pod)
- Operational: upgrade ztunnel without pod restart
- Friction: gradual L7 adoption
- App compat: less interference (no iptables in pod)

## Why Sidecar (Still)

- Maturity: years of production
- Per-pod isolation: blast radius
- L7 always (not opt-in)
- Ecosystem (debugging tools)
- Custom features

## Migration

Same Istio install supports both:
```yaml
# Disable sidecar injection
# Enable ambient
kubectl label namespace prod istio.io/dataplane-mode=ambient
```

Per namespace.

## Use Cases

### Sidecar
- Full features
- Strict per-pod
- Mature deploy

### Ambient
- Many low-traffic services
- Cost-conscious
- Gradual L7 rollout
- VM workloads (not pod-based)

## Architecture (Ambient)

```
Pod A (no sidecar)
  ↓ traffic
ztunnel (node A)
  ↓ mTLS to ztunnel on node B
ztunnel (node B)
  ↓ deliver
Pod B (no sidecar)

For L7 features:
ztunnel → waypoint proxy (L7 work) → ztunnel → Pod B
```

## ztunnel

- Rust-based
- HBONE (HTTP-Based Overlay Network Encapsulation)
- L4 mTLS
- L4 auth
- Lightweight

## Waypoint

- Standard Istio Envoy
- One per identity (service account)
- Deploy with `istioctl x waypoint apply`
- Opt-in per namespace / SA

```bash
istioctl x waypoint apply --enroll-namespace prod
```

## Identity

SPIFFE format: `cluster.local/ns/prod/sa/app`.

ztunnel issued certs per pod identity.

mTLS between ztunnels: identity-aware.

## Performance

### Sidecar Latency
~1-5 ms per hop.

### Ambient Latency
- L4 only: ~0.5-2 ms (ztunnel-to-ztunnel)
- With waypoint: ~1-3 ms (extra hop through waypoint)

For typical app: imperceptible.

## Resource Compare

For 100 pods:
- Sidecar: 100 × 100 MB = 10 GB
- Ambient: 5 nodes × 100 MB ztunnel = 500 MB + waypoints if used

Significant savings.

## Limitations (Ambient)

- Newer (less battle-tested)
- Some Istio features sidecar-only
- Documentation evolving
- Debug tools maturing

For prod: validate.

## Linkerd

Doesn't have ambient. Always sidecar (linkerd2-proxy in Rust; small).

Linkerd2-proxy is already light (~10-20 MB).

For ambient-like reasons: Linkerd "just works" lighter.

## Cilium Mesh

eBPF-based; no sidecar at all:
- Datapath in kernel (eBPF)
- L4 mTLS via kernel
- L7 via Envoy when needed

For: closest to "ambient" model from start.

## Which to Choose

```
Already on sidecar Istio + working → stay
New Istio adoption → ambient (if comfortable with beta)
Cost-conscious → ambient or Cilium mesh
Linkerd user → sidecar (it's fine)
Cilium CNI → Cilium mesh
```

## Best Practices

- Test ambient in non-prod first
- Monitor ztunnel resource usage
- Use waypoint sparingly (only where L7 needed)
- Mixed sidecar + ambient OK during migration
- Validate features used

## Common Mistakes

- Assume ambient = no proxy (it has ztunnel/waypoint)
- Skip L7 features that need waypoint
- Mix modes without understanding
- Underestimate ambient newness

## Status

Istio ambient: GA as of late 2024.

For new adopters: viable.

## Operational

### Sidecar
- Inject (auto via annotation)
- Restart pods on upgrade
- Per-pod tuning

### Ambient
- ztunnel as DaemonSet
- Upgrade DaemonSet (no pod restart)
- Waypoint deploys separately

For: ambient easier to operate at scale.

## Debugging

### Sidecar
```bash
kubectl exec POD -c istio-proxy -- pilot-agent
istioctl proxy-config POD
```

### Ambient
```bash
istioctl experimental ztunnel-config POD
```

Newer tools.

## Real-World

Some FAANGM adopting ambient for cost.

Linkerd in many smaller orgs (simpler, lighter).

Cilium mesh growing.

## Quick Refs

```bash
# Sidecar
kubectl label namespace ns istio-injection=enabled

# Ambient
kubectl label namespace ns istio.io/dataplane-mode=ambient
istioctl x waypoint apply --enroll-namespace ns
```

## Interview Prep

**Senior**: "Sidecar vs ambient."

**Staff**: "Mesh architecture choice."

**Principal**: "Mesh strategy for cost."

## Next Topic

→ Move to [L14/C02 — Istio](../C02/README.md)
