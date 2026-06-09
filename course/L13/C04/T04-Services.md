# L13/C04/T04 — Services (ClusterIP, NodePort, LoadBalancer, Headless)

## Learning Objectives

- Use service types correctly
- Pick for each scenario

## Service

Stable abstraction over set of pods:
- Selector matches pods → endpoints
- Virtual IP (ClusterIP)
- DNS

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
```

## Types

- ClusterIP (default)
- NodePort
- LoadBalancer
- ExternalName

Plus: Headless (clusterIP: None).

## ClusterIP

Internal only:
- Service IP from Service CIDR
- Reachable only inside cluster
- For pod-to-pod communication

```yaml
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
```

Pod accesses `web` (DNS) → ClusterIP → DNAT to pod.

## NodePort

Expose on every node's IP at static port (30000-32767):

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080
```

`<NodeIP>:30080` → Service → pod.

Use:
- Direct access (no LB)
- Testing
- Behind external LB

## LoadBalancer

Cloud provider provisions LB:
```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
```

AWS: NLB or ALB (with controller).
GCP: Cloud LB.
Azure: Azure LB.

LB gets external IP/hostname; routes to NodePort → Service → pod.

For prod public services.

## Annotations (LoadBalancer)

```yaml
metadata:
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
```

Configure LB behavior.

## ExternalName

DNS CNAME to external:
```yaml
spec:
  type: ExternalName
  externalName: db.example.com
```

`db.namespace.svc.cluster.local` → CNAME → `db.example.com`.

No selector, endpoints, ClusterIP.

For: external services with internal name.

## Headless Service

```yaml
spec:
  clusterIP: None
  selector:
    app: db
```

No ClusterIP. DNS returns all pod IPs:
```
db.namespace.svc.cluster.local → A records for each pod
```

For: StatefulSet, peer discovery, client-side load balancing.

## Endpoints

For each Service: Endpoints (or EndpointSlice) tracks pod IPs:
```bash
kubectl get endpoints web
```

Updated when pods become Ready / unready.

EndpointSlice (newer): scalable for huge services.

## Ports

```yaml
ports:
- name: http
  port: 80          # Service port
  targetPort: 8080  # Pod port (or name)
  protocol: TCP

- name: metrics
  port: 9090
  targetPort: 9090
```

Multiple ports on one Service.

## Named Target Ports

Pod:
```yaml
ports:
- name: http
  containerPort: 8080
```

Service:
```yaml
targetPort: http
```

Avoid hardcoded port numbers.

## Selectors

```yaml
selector:
  app: web
  tier: frontend
```

Matches pods with ALL labels.

Pods may have more labels (extra OK).

## Service Without Selector

Don't auto-create Endpoints. You create manually:
```yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: db   # must match Service name
subsets:
- addresses:
  - ip: 1.2.3.4
  ports:
  - port: 5432
```

For: external services accessed via internal name (alternative to ExternalName).

## DNS

```
<service-name>.<namespace>.svc.cluster.local
```

Pod's resolv.conf:
```
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

Short names work in same namespace.

## Cross-Namespace

```
web.production.svc.cluster.local
```

From pod in `default`: explicit namespace.

## CoreDNS

K8s DNS:
- Resolves Service names
- Forwards external (to upstream)
- Pluggable (cache, prometheus, etc.)

Configured via Corefile (ConfigMap kube-system/coredns).

## Service Topology

```yaml
trafficDistribution: PreferClose   # 1.31+
```

Prefer pods on same zone (latency, cost).

## EndpointSlice

Newer Endpoints replacement:
- Up to 100 endpoints per slice
- Many slices per Service (scale to 10000+ endpoints)
- Default in modern K8s

## Load Balancing

Default: random (with probability) via iptables.

For specific algorithms (consistent hash, least-conn):
- IPVS mode
- Cilium
- Service mesh

## Session Affinity

```yaml
sessionAffinity: ClientIP
sessionAffinityConfig:
  clientIP:
    timeoutSeconds: 3600
```

Sticky based on client IP.

For stateful client → same pod.

Avoid: stateless preferred.

## Multiple Services Same Pod

A pod can be selected by multiple Services. Different ports / paths.

## Port Forwarding

Local access to Service:
```bash
kubectl port-forward svc/web 8080:80
# http://localhost:8080
```

For debugging.

## Internal Load Balancer

AWS:
```yaml
annotations:
  service.beta.kubernetes.io/aws-load-balancer-internal: "true"
```

Internal LB (private subnet); not Internet-facing.

For: internal microservices wanting LB.

## CRD-Based: AWS Load Balancer Controller

For ALB / advanced NLB:
```yaml
annotations:
  kubernetes.io/ingress.class: alb
```

Used with Ingress (covered T05).

## Service Mesh

Istio / Linkerd / Cilium replace Service routing with mesh:
- mTLS
- Retries
- Traffic policies
- Observability

Pods route via sidecar (or eBPF) instead of kube-proxy.

K8s Service still exists; mesh layers on.

## Common Patterns

### Tiered
- Frontend (LoadBalancer): public
- API (ClusterIP): internal
- DB (Headless): direct pod access

### Multi-Port
- HTTP (80)
- gRPC (50051)
- Metrics (9090)

One Service.

### External Service
- ExternalName for external DB
- App uses `db.namespace.svc.cluster.local`
- DNS resolves to actual.

## Common Mistakes

- Wrong selector (no endpoints)
- Wrong targetPort
- ClusterIP for external (won't work)
- LoadBalancer per service (cost!) — use Ingress
- Hardcoded ClusterIP

## Best Practices

- Named ports (avoid magic numbers)
- Ingress over per-Service LB
- Internal LB for internal services
- Topology-aware for latency
- Service mesh for many services

## Multi-Cluster

For services across clusters:
- Each cluster has Service
- DNS / mesh combines:
  - Istio multi-cluster
  - Cilium ClusterMesh
  - ExternalDNS

## Inspection

```bash
kubectl get svc
kubectl describe svc web
kubectl get endpoints web
kubectl get endpointslices -l kubernetes.io/service-name=web

# Resolve
kubectl exec my-pod -- nslookup web

# Curl
kubectl exec my-pod -- curl http://web/
```

## Service Mesh Auto-Discovery

Istio Service Entry registers external as if in-mesh:
```yaml
apiVersion: networking.istio.io/v1
kind: ServiceEntry
spec:
  hosts:
  - api.partner.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
```

For: mesh sees external as managed.

## Quick Refs

```yaml
# ClusterIP (default)
spec:
  selector: {app: web}
  ports:
  - port: 80
    targetPort: 8080

# Headless
spec:
  clusterIP: None
  selector: {app: db}
  ports: [...]

# NodePort
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080

# LoadBalancer
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
```

## Interview Prep

**Junior**: "ClusterIP vs NodePort."

**Mid**: "Headless service use."

**Senior**: "Service for stateful workload."

**Staff**: "100 services architecture."

## Next Topic

→ [T05 — Ingress Controllers](T05-Ingress.md)
