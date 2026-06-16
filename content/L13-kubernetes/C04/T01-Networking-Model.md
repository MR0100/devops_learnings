# L13/C04/T01 — Pod-to-Pod, Pod-to-Service, External-to-Service

## Learning Objectives

- Understand K8s network model
- Trace traffic paths

## K8s Network Model

Rules:
1. Every pod gets unique cluster-wide IP
2. Pods can communicate with all other pods without NAT
3. Nodes can communicate with all pods (without NAT)
4. Pod sees same IP as others see for it

CNI plugin implements.

## Pod-to-Pod (Same Node)

Pod A (10.244.1.5) → Pod B (10.244.1.6):
- veth pair connects pod to host bridge / interface
- Traffic stays on node (Linux bridge or similar)

Fast; no NAT.

## Pod-to-Pod (Different Node)

Pod A on Node 1 → Pod B on Node 2:
- CNI handles cross-node:
  - Overlay (VXLAN, IPIP): encapsulate
  - Routing: nodes route pod CIDRs
  - Underlay (AWS VPC CNI): pods use VPC IPs

Path depends on CNI.

## Service

Stable IP + DNS abstracting pods:
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
```

ClusterIP (e.g., 10.96.5.10): virtual; managed by kube-proxy.

## Service Backed by Pods

Endpoints / EndpointSlice tracks pod IPs:
```bash
kubectl get endpoints web
# IPs: 10.244.1.5 10.244.2.7 10.244.3.9
```

When pod ready/unready: endpoints updated.

## Pod-to-Service

Pod → ClusterIP:80 → (DNAT to pod IP) → pod:8080.

DNAT done by:
- kube-proxy iptables rules
- Or IPVS
- Or Cilium eBPF

## DNS

CoreDNS resolves service names:
- `web` (same namespace)
- `web.production.svc.cluster.local`
- `<pod-ip>.pod.cluster.local` (rare)

Pod's /etc/resolv.conf:
```
nameserver 10.96.0.10    # CoreDNS Service IP
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

## External-to-Service

For exposing outside cluster:

### NodePort
Service.spec.type=NodePort:
- Allocate port 30000-32767 on every node
- Traffic to <NodeIP>:NodePort → Service

Old; simple but not for production typically.

### LoadBalancer
Service.spec.type=LoadBalancer:
- Cloud provider provisions LB
- LB → NodePort → Service → Pods

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
```

For HTTPS: TLS at LB; backend HTTP.

### Ingress
HTTP/HTTPS routing:
- One LB; many services
- Path / host-based
- TLS termination

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port: {number: 80}
```

Requires Ingress Controller (Nginx, ALB, Traefik).

### Gateway API
Newer; replacement for Ingress (covered T06).

## kube-proxy

Per-node agent maintaining service rules:

### iptables mode
For each Service: iptables rule that DNATs ClusterIP to a backend pod (random).

Pros: stable
Cons: O(n) rules; slow at huge scale (10000+ services)

### IPVS mode
Kernel-level LB; better at scale.

Algorithms: round-robin, weighted round-robin, least-conn, etc.

### Cilium eBPF
Replaces kube-proxy; eBPF programs directly in kernel:
- Faster
- Programmable
- No iptables / IPVS

## Endpoints vs EndpointSlice

EndpointSlice: scalable replacement for Endpoints.
- Each slice up to 100 endpoints
- Better for huge services (10000+ endpoints)

Default in modern K8s.

## Service IP Range

Cluster has Service CIDR (e.g., 10.96.0.0/12).

Pod CIDR (e.g., 10.244.0.0/16) different.

Each pod IP unique; service IP virtual.

## ExternalIP

```yaml
spec:
  type: ClusterIP
  externalIPs:
  - 1.2.3.4
```

Service reachable on external IP. Routing managed by you.

## Headless Service

```yaml
spec:
  clusterIP: None
  selector:
    app: db
```

No ClusterIP. DNS returns all pod IPs:
- `db.namespace.svc.cluster.local` → A records for each pod

For: stateful sets, peer discovery.

## ExternalName

```yaml
spec:
  type: ExternalName
  externalName: db.example.com
```

DNS CNAME to external. No selector/endpoints.

For: external services accessible by internal name.

## Multi-Cluster

Cross-cluster service discovery:
- Service mesh (Istio multi-cluster, Cilium ClusterMesh)
- ExternalDNS + DNS
- API Gateway federation

## Load Balancing Algorithms

Default (kube-proxy iptables): random (with probability weights).

IPVS: round-robin, least-conn, etc.

Service Mesh: more options (consistent hash, etc.).

## Session Affinity

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
```

Same client IP → same pod. For stateful (avoid).

## Headless + StatefulSet

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
spec:
  clusterIP: None
  selector: {app: db}
```

StatefulSet pods:
- db-0.db-headless...
- db-1.db-headless...

For peer discovery.

## Traffic Policy

```yaml
spec:
  externalTrafficPolicy: Local
```

Local: only route to pods on same node as receiving LB endpoint. Preserves source IP. May have uneven distribution.

Cluster: route to any pod. Hides source IP.

## Internal Traffic Policy

```yaml
internalTrafficPolicy: Local
```

Pod → Service: route only to pods on same node.

For: latency reduction, locality.

## Pod IP Allocation

Per CNI:
- Calico: BGP / VXLAN; pod CIDR per node
- Cilium: similar; eBPF
- AWS VPC CNI: VPC IPs (one ENI per X pods)
- Flannel: VXLAN overlay

Choice affects:
- Performance
- Cost
- Visibility
- Features

## Service Discovery

Apps find services via:
- DNS (most common)
- Environment variables (auto-set on pod start)
- API queries (rare)

DNS preferred; flexible.

## Common Issues

### Service Not Working
```bash
kubectl get svc
kubectl get endpoints   # any backends?
kubectl describe svc web

# Pod selector match?
kubectl get pods --selector=app=web
```

### DNS Failing
```bash
kubectl exec my-pod -- nslookup web
# Or
kubectl exec my-pod -- getent hosts web
```

If fails: CoreDNS issue.

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system <coredns-pod>
```

### Pod-to-Pod Failing
```bash
# From pod A:
kubectl exec pod-a -- ping <pod-b-ip>
kubectl exec pod-a -- curl <pod-b-ip>:port
```

If fails: CNI issue, NetworkPolicy block, SG (AWS VPC CNI).

## Best Practices

- Use Service names (DNS) over IPs
- Headless Service for stateful
- Topology-aware routing for latency
- Ingress / Gateway over per-service LB (cost)
- NetworkPolicy for security

## Common Mistakes

- Selector typo (no endpoints)
- Wrong targetPort (service can't reach pod)
- Service IP hardcoded
- No Service for stateful (direct pod IP unreliable)

## Quick Refs

```yaml
# Service
apiVersion: v1
kind: Service
spec:
  selector:
    app: web
  ports:
  - port: 80          # ClusterIP port
    targetPort: 8080  # pod port
    protocol: TCP

# Types
type: ClusterIP        # default
type: NodePort
type: LoadBalancer
type: ExternalName
```

```bash
# Inspect
kubectl get svc
kubectl get endpoints
kubectl describe svc web
kubectl get endpointslices -l kubernetes.io/service-name=web
```

## Interview Prep

**Junior**: "How do pods communicate."

**Mid**: "Service vs Pod IP."

**Senior**: "kube-proxy modes."

**Staff**: "Networking at 10000-service scale."

## Next Topic

→ [T02 — CNI Plugins](T02-CNI.md)
