# L14/C03/T01 — Linkerd Architecture (linkerd2-proxy in Rust)

## Learning Objectives

- Install Linkerd
- Understand architecture

## Linkerd

CNCF-graduated service mesh:
- Rust-based proxy (linkerd2-proxy)
- Smaller, faster, simpler than Istio
- Strong defaults

## Components

### Control Plane
- linkerd-destination (service discovery)
- linkerd-identity (mTLS CA)
- linkerd-proxy-injector (webhook)

### Data Plane
- linkerd2-proxy (sidecar)
- Rust; ~10-20 MB RAM
- HTTP/2 native

## Install

```bash
# CLI
curl -sL run.linkerd.io/install | sh

# Pre-check
linkerd check --pre

# Install CRDs
linkerd install --crds | kubectl apply -f -

# Install
linkerd install | kubectl apply -f -

# Check
linkerd check
```

## Inject

```bash
kubectl get deploy myapp -o yaml | linkerd inject - | kubectl apply -f -
```

Or annotation:
```yaml
metadata:
  annotations:
    linkerd.io/inject: enabled
```

## Architecture Diagram

```
Pod
├─ App
└─ linkerd2-proxy (sidecar)
   ↕
linkerd-destination (control)
   ↕
linkerd-identity (CA)
```

## linkerd2-proxy

Written in Rust:
- Memory-safe
- Small footprint (~10-20 MB)
- HTTP/2-first
- Fast

For: stable, secure proxy.

## Identity

Auto-issued certs:
- Per-pod
- Auto-rotated (24h)
- TLS 1.3
- ECDSA

## mTLS Default

mTLS enabled by default for all meshed traffic. No config needed.

For: zero-config security.

## Linkerd Viz

Observability extension:
```bash
linkerd viz install | kubectl apply -f -
linkerd viz dashboard
```

UI: dashboard, tap, top, profiles.

## Linkerd Tap

Live request inspection:
```bash
linkerd viz tap deploy/myapp
```

For: debugging.

## Linkerd Top

Top-style request stats:
```bash
linkerd viz top deploy/myapp
```

For: real-time.

## Service Profiles

Custom routes + retries:
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: myapp.prod.svc.cluster.local
  namespace: prod
spec:
  routes:
  - name: GET /
    condition:
      method: GET
      pathRegex: /
    isRetryable: true
  retryBudget:
    retryRatio: 0.2
    minRetriesPerSecond: 10
    ttl: 10s
```

## Traffic Splits (SMI)

```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: myapp-rollout
spec:
  service: myapp
  backends:
  - service: myapp-v1
    weight: 90
  - service: myapp-v2
    weight: 10
```

For: canary.

(SMI = Service Mesh Interface; standard CRDs.)

## Gateway API (Current Direction)

Recent Linkerd has shifted L7 routing toward the Kubernetes **Gateway API** `HTTPRoute`; `ServiceProfile`/SMI `TrafficSplit` shown above are the older/historical model.

`HTTPRoute` is the standard, mesh-agnostic way Linkerd now expresses path/header routing, traffic splits, retries, and timeouts. The GAMMA initiative extended Gateway API to cover east-west (mesh) traffic, not just north-south ingress, so the same CRD describes both.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: myapp-split
  namespace: prod
spec:
  parentRefs:
  - name: myapp            # the target Service (mesh/east-west)
    kind: Service
    group: core
  rules:
  - backendRefs:
    - name: myapp-v1
      port: 8080
      weight: 90
    - name: myapp-v2
      port: 8080
      weight: 10
```

The same shift applies to every major mesh — see the Istio Gateway API note in C02. Prefer `HTTPRoute` for new work; treat `ServiceProfile`/`TrafficSplit` as legacy/maintenance.

## Linkerd vs Istio

| | Linkerd | Istio |
|---|---|---|
| Data plane | linkerd2-proxy (Rust) | Envoy (C++) |
| Footprint | Small | Larger |
| Features | Focused | Comprehensive |
| Setup | Simple | Complex |
| Learning curve | Low | Steep |
| L7 routing | Gateway API `HTTPRoute` (ServiceProfile/SMI legacy) | Gateway API `HTTPRoute` / `VirtualService` |
| Multi-cluster | Supported | Supported |

## When Linkerd

- Want mTLS + basic L7 features
- Simpler setup
- Resource-constrained
- Smaller team

## When Istio

- Need many features
- Complex routing
- Ambient mode
- Large org

## Linkerd Edge

Open source flavor.

Buoyant Enterprise: paid.

## Multi-Cluster

```bash
linkerd multicluster install | kubectl apply -f -
linkerd multicluster link --cluster-name west | kubectl apply -f -
```

For: cross-cluster mTLS.

## Resource Usage

Per pod: ~10-20 MB RAM.
Control plane: ~200 MB total.

For 100 pods: 1-2 GB. Tiny vs Istio.

## Sustainability

- CNCF graduated
- Buoyant company (commercial)
- Strong production users
- Steady releases

## Performance

linkerd2-proxy: < 1 ms latency added.

Benchmarks: often outperforms Envoy at low complexity.

## Best Practices

- Annotation-based injection
- Service Profiles for important services
- Monitor with viz
- mTLS strict (default)
- Inject in selective namespaces
- Upgrade quarterly

## Common Mistakes

- Expect Istio-level features (Linkerd is focused)
- No Service Profiles (miss retries)
- Inject all namespaces
- Skip linkerd check

## Quick Refs

```bash
# Install
curl -sL run.linkerd.io/install | sh
linkerd install --crds | kubectl apply -f -
linkerd install | kubectl apply -f -

# Inject
linkerd inject deployment.yaml | kubectl apply -f -

# Check
linkerd check

# Viz
linkerd viz install
linkerd viz dashboard
linkerd viz tap deploy/X
linkerd viz top
linkerd viz stat deploy

# Upgrade
linkerd upgrade
```

## Interview Prep

**Mid**: "Linkerd vs Istio."

**Senior**: "When Linkerd."

**Staff**: "Mesh selection."

## Next Topic

→ [T02 — Simpler Tradeoffs vs Istio](T02-Linkerd-vs-Istio.md)
