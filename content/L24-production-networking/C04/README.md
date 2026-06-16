# L24/C04 — Service Discovery

## Topics

- **T01 DNS-Based, Client-Side, Server-Side** — Approaches
- **T02 Consul, Eureka** — Tools

## Why Service Discovery

Services move. IPs change. Manual lists break.

> Service discovery: how does service A find service B's current network address?

## Approaches

### Server-Side (via LB)
```
Client → LB (always at fixed addr) → backend (any IP)
```
- LB knows backends; routes traffic
- Client unaware of individual backends
- Examples: K8s Service, AWS ALB, GCP HTTP LB

### Client-Side
```
Client → service registry → list of backends
Client → backend (chosen) directly
```
- Client picks which backend
- More efficient (no LB hop)
- More complex (client-side LB logic)
- Examples: Netflix Eureka + Ribbon, Consul + native clients

### DNS-Based
```
Client → DNS lookup → resolves to backend IP
```
- Simplest
- TTLs cause issues (stale data)
- Often combined with above
- Examples: K8s headless service, Consul DNS interface

## K8s Service Discovery

K8s Services give server-side discovery:
- ClusterIP: virtual IP, kube-proxy routes
- Headless Service: DNS returns pod IPs directly
- LoadBalancer: provisioned cloud LB
- ExternalName: CNAME

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

Pods can connect via `my-service.namespace.svc.cluster.local`.

### Headless Service (Direct Pod Access)
```yaml
spec:
  clusterIP: None
  selector:
    app: my-app
```

DNS returns all pod IPs. Client picks. Used by StatefulSets (Cassandra, etc.).

## Consul

HashiCorp service discovery + KV + Connect (mesh).

### Service Registration
```
service "my-app" {
  port = 8080
  check {
    http = "http://localhost:8080/healthz"
    interval = "10s"
  }
}
```

### Discovery via DNS
```bash
dig my-app.service.consul        # returns healthy instances
```

### Discovery via HTTP
```bash
curl http://consul:8500/v1/health/service/my-app
```

### Multi-DC
- Each DC has its own Consul cluster
- Federated for cross-DC queries
- Used by HashiCorp Nomad, k8s integration

## Eureka

Netflix's discovery (older; less used today).
- Client-side discovery
- Self-preservation mode (don't evict during network partition)
- Java/Spring ecosystem mostly

## Zookeeper / etcd

Generic distributed coordination; used by older systems for discovery:
- Service registers ephemeral node
- Node disappears when service dies
- Watchers notified

Kubernetes uses etcd internally; Apache Curator on ZooKeeper is older pattern.

## Service Mesh as Discovery

Service mesh (Istio, Linkerd, Consul Connect) provides discovery + LB + mTLS + observability.

For new K8s deployments: built-in K8s Service is usually enough. Add mesh when you need L7 features.

## DNS TTL Issues

DNS-based discovery struggles with churn:
- Long TTL → stale entries; can't fail over fast
- Short TTL → DNS load
- Client caches → ignores TTL

Modern systems push updates (xDS, gRPC LB) rather than rely on DNS.

## Service Discovery Patterns

### Self-Registration
- Service registers itself in registry on startup
- Deregisters on shutdown
- Risk: forgot to deregister; stale entries

### Sidecar Registrar
- Sidecar handles registration
- Decoupled from app

### Platform Native
- K8s API server tracks pods + endpoints
- Cloud APIs track instances
- Most modern approach

## Health Checks Tie In

Discovery + health check = "discover only healthy".

K8s readinessProbe controls inclusion in Service endpoints.
Consul health checks control DNS responses.
LBs do active health checks.

## Multi-Cluster Discovery

For multi-K8s-cluster discovery:
- **K8s Multi-Cluster Services (MCS)** — KEP-style spec
- **Cilium ClusterMesh** — flat connectivity + shared services
- **Submariner** — service connectivity across clusters
- **Istio multi-cluster** — mesh across clusters

## Service Catalog

Beyond raw discovery: documented services.
- **Backstage** (Spotify) — service catalog UI
- **OpsLevel, Cortex, Effx** — commercial catalogs

Adds: ownership, runbooks, deps, SLOs per service.

## Interview Themes

- "Service discovery approaches"
- "K8s Service — how discovery works"
- "Why is DNS imperfect for discovery?"
- "Consul vs K8s native"
- "Multi-cluster service discovery"
