# L24/C04/T01 — DNS-Based, Client-Side, Server-Side

## Learning Objectives

- Compare discovery models
- Pick approach

## Service Discovery

How services find each other:
- IPs change (scaling, restart)
- Need lookup

## Models

### DNS-Based
A/SRV records.
- TTL caching
- Client query

### Client-Side
Client knows backend list.
- Smart client
- Connect directly

### Server-Side
LB in middle.
- LB routes
- Dumb client

## DNS

K8s Service:
```
my-service.default.svc.cluster.local → ClusterIP
```

Client resolves; connects.

Pros: simple.
Cons: TTL stale; no fine-grained control.

## Client-Side LB

Client gets list:
```python
backends = registry.lookup('my-service')
choose(backends)
connect()
```

Pros:
- No middleman
- Smart load balancing
- Lower latency

Cons:
- Client complexity
- Per-language libs

## Server-Side LB

```
Client → LB (ALB / Envoy) → Backend
```

Pros:
- Centralized
- Language-agnostic
- Observability

Cons:
- Extra hop
- LB scaling

## Service Mesh

Hybrid:
- Sidecar = local LB
- Control plane = registry

Best of both:
- No central LB
- Smart routing
- Language-agnostic

## Examples

### K8s ClusterIP
DNS + iptables. Server-side LB (kube-proxy).

### gRPC
Client-side LB supported.

### Service Mesh
Sidecar = local LB.

### Cloud LB
Server-side (ALB, NLB).

## Registry

### Native K8s
etcd via API server.

### Consul
Standalone; multi-platform.

### Eureka
Netflix; less common now.

### Zookeeper
Old; Curator clients.

## DNS Caveats

- TTL: stale data
- A record: limited (~30 IPs)
- No load balancing intelligence

For: simple cases.

## Headless Service (K8s)

```yaml
apiVersion: v1
kind: Service
spec:
  clusterIP: None
  selector: ...
```

DNS returns pod IPs directly.

For: client-side LB.

## gRPC Resolution

```python
channel = grpc.insecure_channel('dns:///my-service:50051')
```

gRPC: client-side LB with discovery.

## Consul

```bash
consul agent
consul services register service.json
```

DNS interface:
```
dig my-service.service.consul
```

Or HTTP API.

## Eureka

```python
client = EurekaClient(eureka_url, app_name='my-app')
client.register()
```

Spring Cloud uses heavily.

## Best Practices

- K8s: native discovery (Service)
- Multi-platform: Consul
- Service mesh: built-in
- Avoid manual IPs

## Common Mistakes

- Manual IPs in config
- Long TTL (stale)
- No fallback
- Hardcoded ports

## Quick Refs

```
K8s: Service / Headless Service
Consul: agent + services
Eureka: REST registry

DNS:        broad; cache issues
Client:     smart; complex
Server:     simple; extra hop
Mesh:       hybrid (sidecar)
```

## Interview Prep

**Mid**: "Service discovery."

**Senior**: "Client vs server LB."

**Staff**: "Discovery at scale."

## Next Topic

→ [T02 — Consul, Eureka](T02-Consul-Eureka.md)
