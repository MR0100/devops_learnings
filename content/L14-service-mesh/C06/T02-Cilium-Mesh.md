# L14/C06/T02 — Cilium Service Mesh (eBPF)

## Learning Objectives

- Understand Cilium mesh
- Compare to sidecar meshes

## Cilium

CNI for K8s. Built on eBPF:
- L3/L4 networking
- NetworkPolicy
- LoadBalancer (kube-proxy replacement)
- Service Mesh

## Why eBPF

In-kernel data path:
- No sidecar
- Lower latency
- Lower CPU
- Lower memory

## Architecture

```
Pod traffic
   ↓
eBPF program in kernel (Cilium)
   ↓
Encryption (WireGuard) or plaintext
   ↓
Other pod's kernel eBPF
   ↓
Pod
```

## Install

```bash
helm install cilium cilium/cilium \
  --version 1.16 \
  --namespace kube-system \
  --set serviceMesh.enabled=true
```

## L4 mTLS

Via WireGuard (kernel-level):
```bash
cilium config set encryption-type wireguard
```

All pod-to-pod: WG-encrypted.

For: mTLS-like, but at kernel.

## SPIFFE Identities

Cilium issues SPIFFE certs to pods.

For: identity-aware policies.

## CiliumNetworkPolicy

L3-L7:
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-policy
spec:
  endpointSelector:
    matchLabels:
      app: api
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: GET
          path: /api/*
```

L7 HTTP filtering at kernel.

## L7 Features

Limited (vs Istio):
- HTTP method/path filtering
- DNS-based policies
- gRPC method filtering
- Kafka topic filtering

For: many use cases enough.

## Envoy Integration

For richer L7: Envoy as Cilium's L7 proxy.

Auto-managed by Cilium.

For: HTTP routing.

## Hubble

Observability:
- Service map
- Request flow
- L7 decisions

```bash
cilium hubble enable
hubble observe
```

For: visualize.

## Service Mesh Mode

```bash
helm install cilium cilium/cilium --set serviceMesh.enabled=true
```

Enables:
- L7 features
- mTLS (via SPIFFE)
- Ingress controller (Gateway API)

## Gateway API

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  gatewayClassName: cilium
  listeners:
  - name: http
    port: 80
    protocol: HTTP
```

For: ingress without separate controller.

## Comparison

| | Cilium | Istio | Linkerd |
|---|---|---|---|
| Data path | eBPF | Sidecar (Envoy) | Sidecar (linkerd2-proxy) |
| Overhead/pod | ~0 | ~100 MB | ~10-20 MB |
| Pod restart for upgrade | No | Yes | Yes |
| L4 mTLS | WireGuard | TLS 1.3 | TLS 1.3 |
| L7 | Limited + Envoy | Rich | Focused |
| K8s native | Yes (CNI) | Add-on | Add-on |
| VM support | No (K8s-only) | No (mostly) | No |

## Performance

Cilium: near-line-rate throughput.

eBPF: no extra processing overhead vs sidecar copy.

For: high-throughput.

## Cluster Mesh

Cross-cluster:
```bash
cilium clustermesh enable
cilium clustermesh connect --destination-context other-cluster
```

For: services discoverable across clusters.

## Tetragon

Runtime security (separate from mesh):
- Process events
- File access
- Syscalls

For: deep visibility.

## Hubble UI

```bash
cilium hubble ui
```

Service graph + request flow.

For: visualize.

## When Cilium Mesh

### Pros
- Lower overhead
- K8s native
- Strong L4 + NetworkPolicy
- WireGuard mTLS at kernel
- Already use Cilium CNI

### Cons
- Less mature L7 (vs Istio)
- K8s-only (no VM mesh)
- Newer (rapid evolution)

## When Istio Despite Cilium

- Need rich L7
- Multi-cluster maturity
- Existing investment
- Ambient + Cilium possible (some integration)

## When Linkerd Despite Cilium

- Sidecar is fine
- Linkerd ops experience
- Specific Linkerd features

## Migration Path

```
Phase 1: Cilium as CNI
Phase 2: CiliumNetworkPolicy
Phase 3: WireGuard encryption
Phase 4: L7 features (Envoy auto)
Phase 5: Gateway API ingress
```

## Hubble Examples

```bash
# All flows
hubble observe

# Drops
hubble observe --verdict DROPPED

# To specific pod
hubble observe --to-pod ns/pod-name

# HTTP
hubble observe --protocol http
```

For: debug.

## Network Policy Tester

```bash
cilium connectivity test
```

Built-in validation.

## SBOMs / Compliance

Cilium has policies for:
- DNS filtering
- Egress IP control
- Kafka ACLs

For: compliance.

## Best Practices

- Cilium CNI first
- WireGuard for inter-node
- CiliumNetworkPolicy (deny-by-default)
- Hubble enabled
- Test connectivity
- Per-namespace policies

## Common Mistakes

- Allow-all policies
- WireGuard misconfigured
- Mixing Cilium + Istio without understanding
- Wrong kernel version (eBPF requires modern)

## Kernel Requirements

eBPF features: 4.19+ kernel. Modern (5.x+) for full.

For: AKS/EKS/GKE Bottlerocket/AL2023 typically.

## Real Use

- Adobe
- Bell
- Datadog
- Many fintech

Cilium adoption growing.

## Quick Refs

```bash
# Install
helm install cilium cilium/cilium --set serviceMesh.enabled=true

# Status
cilium status
cilium connectivity test

# Hubble
hubble observe / observe --verdict DROPPED

# Policy
kubectl get ciliumnetworkpolicy
```

## Interview Prep

**Mid**: "Cilium vs sidecar mesh."

**Senior**: "eBPF mesh."

**Staff**: "Cilium adoption strategy."

## Next Topic

→ Move to [L15 — CI/CD Deep](../../L15-cicd-fundamentals/README.md)
