# L14/C01/T01 — What Problems Does a Mesh Solve

## Learning Objectives

- Identify mesh use cases
- Decide if needed

## Without Mesh

Apps responsible for:
- TLS (or no TLS)
- Retries (custom logic)
- Timeouts
- Circuit breaking
- Service discovery (via DNS)
- Traffic splitting (LB rules)
- Observability (each app instruments)
- AuthN/Z (per service)

Inconsistent; tedious.

## With Mesh

Infra layer handles:
- mTLS automatic
- Retries via policy
- Timeouts uniform
- Circuit breaking declarative
- Discovery via mesh
- Traffic splitting via CRD
- Metrics/traces from sidecar
- Policy via CRD

App code: focus on business logic.

## Problems

### 1. mTLS
Without mesh: each service does TLS.
- Cert management per app
- Some skip (insecure)
- Hard to rotate

With mesh: sidecar handles.
- Auto-rotated certs
- Default-on
- Zero app changes

### 2. Retries & Timeouts
Without mesh: hardcoded in client libs.

With mesh:
```yaml
- retries:
    attempts: 3
    perTryTimeout: 2s
    retryOn: 5xx,reset,connect-failure
```

Across all clients consistently.

### 3. Circuit Breaking
Without mesh: per-client lib.

With mesh:
```yaml
- connectionPool:
    tcp:
      maxConnections: 100
    http:
      http2MaxRequests: 1000
  outlierDetection:
    consecutive5xxErrors: 5
    interval: 30s
    baseEjectionTime: 30s
```

### 4. Traffic Splitting
Without mesh: deploy + LB config.

With mesh:
```yaml
http:
- route:
  - destination:
      host: app
      subset: v1
    weight: 90
  - destination:
      host: app
      subset: v2
    weight: 10
```

For: canary, A/B.

### 5. Observability
Without mesh: each service instruments.

With mesh: sidecar emits:
- Requests count
- Latency p50/p99
- Error rate
- Per-service metrics

Uniform Grafana dashboards.

### 6. AuthN/Z
Without mesh: app validates JWTs.

With mesh:
```yaml
- mtls:
    mode: STRICT
- when:
  - key: source.principal
    values: ["cluster.local/ns/prod/sa/frontend"]
```

Service identity enforced.

### 7. L7 Routing
Header-based, path-based routing without app changes:
```yaml
- match:
  - headers:
      x-user-type:
        exact: premium
  route:
  - destination:
      host: app-premium
```

### 8. Multi-Cluster
With mesh: services discoverable across clusters.

```yaml
# Istio multi-cluster: pods in cluster A reach services in cluster B transparently
```

## What Mesh Doesn't Solve

- App bugs
- Bad APIs
- Slow services (mesh adds latency)
- Data layer (DB, cache)

Mesh: L4-L7 network.

## When You Don't Need One

### Small Service Count (<10)
Tradeoff not worth.

### Single Stack
All Go services? They can share libraries; less benefit.

### Simple Topology
- Frontend → backend → DB
- Limited inter-service
- No need

### Already Solving It
- Already have mTLS via lib
- Already have observability
- Migration cost > benefit

## When You Need One

### Many Services (50+)
Consistent policy hard otherwise.

### Polyglot
Java + Go + Python + Node: mesh unifies.

### Security
mTLS mandatory; zero-trust.

### Traffic Management
Canaries common; need easy split.

### Observability Required
Uniform metrics from infra layer.

## Cost

### Compute
- Sidecar per pod: 50-200 MB RAM, 0.1-0.5 vCPU
- Control plane (istiod): 1-2 GB RAM, 1-2 vCPU
- For 100 pods: ~10-20 GB extra RAM

### Operational
- Steep learning
- Cert mgmt
- Upgrades
- Debugging (extra hop)

### Latency
- Sidecar adds ~1-5 ms
- mTLS handshake
- Usually fine; pre-prod test

## Examples

### LinkedIn
Service mesh (custom + Envoy-based).

### Lyft
Envoy author. Heavy use.

### Many enterprises
Istio for east-west traffic.

### Reluctant adopters
Wait for ambient mesh (lower overhead).

## Without K8s

Mesh outside K8s: rare.
Consul Connect supports VMs.

For most: K8s + mesh.

## Alternatives

### API Gateway Only
For north-south (in/out): gateway handles.
East-west (service-to-service): apps.

### Service Lib (Hystrix-style)
Library in apps; per-language.

### Cilium / eBPF Mesh
Less overhead; L4 strong; L7 emerging.

## Trends

- Istio ambient (sidecarless): lower overhead
- Cilium service mesh: eBPF
- Linkerd: simpler, less overhead
- Service mesh interface (SMI): standard CRDs

## Best Practices

- Justify mesh before adopting
- Start with mTLS only
- Add features incrementally
- Monitor sidecar resources
- Train team thoroughly
- Test latency impact

## Common Mistakes

- Adopt for buzzword
- Underestimate complexity
- All features at once
- No baseline metrics (can't measure improvement)
- Skip training

## Decision Framework

```
Few services + simple? → No mesh
Polyglot + mTLS need? → Mesh
Strong K8s team? → Istio / Linkerd
New / hesitant? → Linkerd (simpler)
Cilium CNI? → Cilium mesh
```

## Quick Refs

```
Problems: mTLS, retries, observability, policy
Cost: CPU + RAM + complexity
Decision: many services + polyglot + security needs
```

## Interview Prep

**Junior**: "What's a service mesh."

**Mid**: "Problems mesh solves."

**Senior**: "When mesh worth it."

**Staff**: "Mesh strategy at scale."

## Next Topic

→ [T02 — Data Plane vs Control Plane](T02-Data-Control-Plane.md)
