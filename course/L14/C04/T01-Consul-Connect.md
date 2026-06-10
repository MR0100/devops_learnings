# L14/C04/T01 — Consul Connect: HashiCorp Stack Integration

## Learning Objectives

- Use Consul Connect
- Integrate with HashiCorp tools

## Consul Connect

Service mesh by HashiCorp:
- Works with VMs (not just K8s)
- mTLS via Envoy sidecar
- Service discovery via Consul
- Intentions for authz
- Integrates with Vault, Nomad, Terraform

## Why Consul

- Multi-platform (K8s + VMs + bare metal)
- Already use HashiCorp stack
- Consul as KV / DNS / service registry

## Components

- Consul Server (control plane)
- Consul Client (per-node agent)
- Envoy sidecar (proxy)
- Connect CA (issues mTLS certs)

## Architecture

```
Consul Server cluster (3-5 nodes; Raft)
   ↕ agent gossip
Consul Client (per node, every type)
   ↕ supervises
Envoy sidecar (per service)
```

## Install K8s

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install consul hashicorp/consul \
  --create-namespace \
  --namespace consul \
  --values values.yaml
```

```yaml
# values.yaml
global:
  name: consul
  datacenter: dc1
server:
  replicas: 3
connectInject:
  enabled: true
  default: true
controller:
  enabled: true
```

For K8s native.

## Inject

Like Istio / Linkerd; auto-inject sidecar.

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    consul.hashicorp.com/connect-inject: "true"
spec:
  containers:
  - name: app
    ...
```

## Intentions

Service-to-service authorization:
```bash
consul intention create frontend backend
consul intention create -deny frontend admin-service
```

Or CRD:
```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceIntentions
metadata:
  name: backend
spec:
  destination:
    name: backend
  sources:
  - name: frontend
    action: allow
  - name: hostile
    action: deny
```

## mTLS

Default-on for Connect-enabled services. Automatic.

CA: Consul-managed or Vault.

## Service Discovery

Apps look up via DNS:
```bash
dig backend.service.consul
```

Or Catalog API.

For: cross-mesh, cross-platform.

## VM Support

```bash
# Install on VM
sudo apt install consul

# Join cluster
consul agent -join CONSUL_SERVER

# Register service
consul services register myservice.json
```

For: hybrid; VMs + K8s same mesh.

## Multi-Datacenter

Consul DC peering or WAN federation:
```bash
consul join -wan SERVER_DC2
```

Cross-DC service discovery + Connect.

For: multi-region.

## Comparison

| | Consul | Istio | Linkerd |
|---|---|---|---|
| K8s | yes | yes | yes |
| VM | yes | (manual) | no |
| Service discovery | Catalog (native) | K8s | K8s |
| Auth | Intentions | AuthorizationPolicy | ServerAuthorization |
| Proxy | Envoy | Envoy | linkerd2-proxy |
| Multi-DC | Yes | Multi-cluster | Multi-cluster |

## Use Cases

### Hybrid (VM + K8s)
Consul's strength.

### HashiCorp Stack
Already use Vault / Terraform / Nomad: Consul fits.

### Service Discovery
Replace ZooKeeper / etcd / DNS hacks.

### Vault Integration
Consul Connect → Vault CA → certs.

## Nomad + Consul

Nomad jobs use Consul:
- Service discovery
- Connect sidecars
- Vault secrets

For: alternative to K8s.

## Vault Integration

```hcl
connect {
  ca_provider = "vault"
  ca_config {
    address = "https://vault.example.com:8200"
    token = "..."
    root_pki_path = "connect-root"
    intermediate_pki_path = "connect-intermediate"
  }
}
```

For: enterprise PKI.

## CRDs

Beyond ServiceIntentions:
- ProxyDefaults
- ServiceDefaults
- ServiceRouter
- ServiceSplitter
- ServiceResolver

For: routing, splitting, etc.

## Traffic Splitting

```yaml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceSplitter
metadata:
  name: api
spec:
  splits:
  - weight: 90
    service: api
    serviceSubset: v1
  - weight: 10
    service: api
    serviceSubset: v2
```

## Observability

Consul UI:
- Service health
- Intentions
- Topology

Metrics: Prometheus.

For traces: Jaeger / Zipkin (Envoy).

## ACLs

```bash
consul acl token create -policy-name read-only
```

For: API access control. Distinct from intentions.

## Health Checks

```hcl
service {
  name = "myapp"
  port = 8080
  check {
    http     = "http://localhost:8080/health"
    interval = "10s"
  }
}
```

Failures → service removed from discovery.

## Production

- 3+ Consul servers
- Multi-AZ
- Backup snapshots
- Vault for ACL bootstrap
- Audit logs

## Comparison to Service Mesh Only

Consul: also service registry, KV store, DNS.

For just mesh: Istio/Linkerd simpler in K8s-only.
For broader: Consul.

## Decline

Consul Connect: mature but smaller market vs Istio.

In K8s-only: Istio/Linkerd often picked.

In hybrid: Consul natural.

## Best Practices

- Vault CA for prod
- Intentions per service
- Health checks tight
- HA Consul cluster
- ACLs strict
- Backup snapshots

## Common Mistakes

- Allow-all intentions
- No ACLs (insecure API)
- Single Consul server
- No backup

## Quick Refs

```bash
# Consul
consul members
consul services
consul catalog services
consul intention list / create

# K8s
kubectl apply -f intention.yaml
kubectl get serviceintentions
```

## Interview Prep

**Mid**: "Consul Connect."

**Senior**: "Hybrid mesh."

**Staff**: "HashiCorp stack integration."

## Next Topic

→ Move to [L14/C05 — Envoy Standalone](../C05/README.md)
