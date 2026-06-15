# L14/C03 — Linkerd

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Linkerd-Architecture.md) | Architecture (linkerd2-proxy in Rust) | 0.5 hr |
| [T02](T02-Linkerd-vs-Istio.md) | Simpler Tradeoffs vs Istio | 0.5 hr |

## Architecture

```
[Control plane (linkerd-)]
   - identity (cert authority)
   - destination (service discovery)
   - proxy-injector (admission webhook)

   ↓

[linkerd2-proxy] sidecars (Rust)
   - written in Rust (memory safe, low overhead)
   - 1/10th memory of Envoy
```

## Philosophy

- "Service mesh that you can run"
- Focused on basics done well: mTLS, retries, latency
- Smaller surface area than Istio
- Less knobs

## Install
```bash
linkerd install | kubectl apply -f -
kubectl annotate namespace myns linkerd.io/inject=enabled
```

## Key Features

### mTLS by Default
Automatic between meshed pods. Identity via service accounts.

### Automatic Retries
Configured via ServiceProfile:
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: my-app.default.svc.cluster.local
  namespace: default
spec:
  routes:
  - name: GET /api/foo
    condition: { method: GET, pathRegex: "/api/foo" }
    isRetryable: true
    timeout: 500ms
  retryBudget:
    retryRatio: 0.2
    minRetriesPerSecond: 10
    ttl: 10s
```

### Traffic Split (canary)
```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: my-canary
spec:
  service: my-app
  backends:
  - service: my-app-v1
    weight: 90
  - service: my-app-v2
    weight: 10
```

## Linkerd vs Istio

| | Linkerd | Istio |
|---|---|---|
| Sidecar | linkerd2-proxy (Rust) | Envoy (C++) |
| Memory per sidecar | ~10-30 MB | ~50-200 MB |
| CPU overhead | Lower | Higher |
| Features | Focused basics | Comprehensive |
| Complexity | Lower | Higher |
| Multi-cluster | Yes (simpler) | Yes (more powerful) |
| L7 features | Basic | Rich (rewrite, mirror, fault injection) |
| Ambient | No (own model) | Yes (ambient mode) |
| Maturity | CNCF graduated | CNCF graduated |

## When Linkerd

- Want mesh without overhead
- Prefer simplicity
- Don't need every L7 feature
- Smaller team / operating budget

## When Istio

- Need full feature set (canary, mirror, fault injection, AuthorizationPolicy)
- Already invested in Envoy elsewhere
- Multi-team, complex routing

## Why linkerd2-proxy in Rust

- Memory safety (no buffer overflows)
- Low memory footprint
- Predictable latency (no GC)
- Sidecars typically idle most of the time; Rust's tail latency is great

## Interview Themes

- "Compare Linkerd and Istio"
- "Why Rust for linkerd2-proxy?"
- "Canary with Linkerd"
- "Multi-cluster Linkerd — how?"
