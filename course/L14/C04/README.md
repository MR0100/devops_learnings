# L14/C04 — Consul Connect

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-HashiCorp-Stack.md) | HashiCorp Stack Integration | 0.5 hr |

## What Consul Is

A service discovery and config + service mesh from HashiCorp.

### Core Capabilities
- **Service Discovery**: register services; DNS or HTTP API to find them
- **Health Checking**: actively or passively
- **Key/Value Store**: shared config
- **Connect (Service Mesh)**: Envoy sidecar mesh with mTLS

## Architecture

```
[Consul Server cluster (Raft, 3 or 5)]
            ↑
            │ RPC
            │
[Consul Agent (DaemonSet)] on each node
            ↑
            │ XDS
            ▼
[Envoy sidecars]
```

## When Consul Connect

- Already using HashiCorp stack (Vault, Terraform, Nomad)
- Want service mesh that works on K8s AND VM workloads (hybrid)
- Multi-DC setup
- Need integrated K/V store

## When Not

- K8s-only — use Istio or Linkerd
- Don't want HashiCorp lock-in

## Service Discovery (non-mesh use)

Many companies use Consul ONLY for service discovery (legacy app on VMs):

```
service registers → Consul agent → cluster
   ↓
Consul DNS: my-service.service.consul → IP
```

## Consul Connect on K8s

```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceDefaults
metadata:
  name: web
spec:
  protocol: http

---
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceIntentions
metadata:
  name: web
spec:
  destination:
    name: web
  sources:
  - name: api
    action: allow
```

## Hybrid: VM + K8s

Consul's killer feature is meshing across VMs and K8s in one mesh. Most other meshes are K8s-only.

## Interview Themes

- "When Consul Connect?"
- "Consul vs Istio for hybrid environments"
- "Service discovery — Consul vs K8s Service"
