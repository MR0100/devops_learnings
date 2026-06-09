# L24 — Production Networking

## Overview

The networking layer that sits above L02 (Linux networking) and L03 (network protocols): production-grade load balancing, API gateways, service discovery, BGP, and DDoS defense.

**7 chapters, 22 topics.**

## Chapter Map

### [C01](C01/) — Load Balancing Algorithms
- T01 Round Robin, Least Connections, Weighted, Consistent Hashing
- T02 Health Checks
- T03 Sticky Sessions

### [C02](C02/) — Reverse Proxies
- T01 Nginx (Configs, Modules)
- T02 HAProxy
- T03 Envoy
- T04 Traefik

### [C03](C03/) — API Gateway
- T01 Kong, Tyk, AWS API Gateway
- T02 Auth, Rate Limiting, Quotas
- T03 Gateway API (Kubernetes)

### [C04](C04/) — Service Discovery
- T01 DNS-Based, Client-Side, Server-Side
- T02 Consul, Eureka

### [C05](C05/) — BGP, Anycast, ECMP
- T01 BGP at the Edge
- T02 Anycast in Practice (Cloudflare, AWS Global Accelerator)
- T03 ECMP & Maglev (Google's L4 LB)

### [C06](C06/) — TLS Termination Patterns
- T01 Edge Termination
- T02 Re-Encryption to Backend
- T03 SNI Routing

### [C07](C07/) — DDoS Protection
- T01 Volumetric Attacks
- T02 L7 Attacks
- T03 AWS Shield, Cloudflare DDoS Protection

## Load Balancing Algorithms

| Algorithm | When |
|---|---|
| Round robin | Equal-cost identical backends |
| Least connections | Long-lived connections, variable work |
| Weighted | Heterogeneous backends |
| Consistent hashing | Caches (preserve cache locality) |
| Maglev hashing | At scale (Google) |
| EWMA | Latency-aware |
| Random | Surprisingly good baseline |

## Reverse Proxy Comparison

| | Nginx | HAProxy | Envoy | Traefik |
|---|---|---|---|---|
| Strength | Web serving + cache | TCP/HTTP, very fast | xDS dynamic config, service mesh | K8s native |
| Language | C | C | C++ | Go |
| Config reload | Hot reload (graceful) | Hot reload | xDS / push | Dynamic |
| Use | Web frontend | High-traffic LB | Mesh, modern microservices | K8s ingress |

## API Gateway vs Reverse Proxy

| | Reverse Proxy | API Gateway |
|---|---|---|
| Layer | L4 + basic L7 | L7-focused |
| Auth | Pass-through | Built-in |
| Rate limit | Available | First-class |
| Schema | No | OpenAPI integration |
| Plugins | Modules | Rich ecosystem |
| Use | LB, edge | API platforms |

## Service Discovery Models

```
Client-side:                Server-side:
Client knows registry       Client → LB → registry
queries → backend           backend
(e.g., Consul Connect,      (e.g., AWS ALB, K8s Service)
Netflix Ribbon)
```

K8s Services are server-side service discovery (kube-proxy + ClusterIP).

## Anycast

Same IP advertised from multiple locations via BGP. Internet routes to nearest. Cloudflare's 1.1.1.1 is anycast.

Used for:
- DNS root servers
- CDN edges
- DDoS absorption
- Global Accelerator

## DDoS Protection Layers

```
Volumetric (Gbps) →  Scrubbing center / cloud (Shield, Cloudflare)
Protocol (SYN flood) → SYN cookies, scrubbing
L7 (slow HTTP, app) → WAF, rate limiting, captchas
```

## Recommended Reading

- *Load Balancing in the Cloud* — by Microsoft (free)
- Cloudflare blog (Anycast, DDoS posts)
- Envoy docs

## Interview Themes

- "Compare load balancing algorithms"
- "How does Anycast work?"
- "Design DDoS protection for an API"
- "Service discovery in K8s"
- "Nginx vs Envoy"

## Next

→ [L25 — Chaos Engineering](../L25/README.md)
