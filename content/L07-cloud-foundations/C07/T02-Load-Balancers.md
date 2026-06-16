# L07/C07/T02 — Load Balancers (L4, L7)

## Learning Objectives

- Pick L4 vs L7
- Configure correctly

## Layers

- L4 (TCP/UDP): routes packets; no app awareness
- L7 (HTTP, gRPC): inspects requests; routes by path/header

## AWS Options

| | ALB | NLB | GWLB | CLB |
|---|---|---|---|---|
| Layer | L7 | L4 | L3 | L4/L7 (legacy) |
| Use | HTTP/HTTPS/gRPC | TCP/UDP/TLS | Insert appliances | Old |
| Performance | high | extreme | line-rate | medium |
| WebSocket | yes | yes | n/a | yes |
| Sticky | yes | yes (TCP) | n/a | yes |
| Pricing | hourly + LCUs | hourly + NLCUs | hourly + GBs | hourly + GBs |

Default modern: ALB (HTTP) or NLB (TCP/raw).

## ALB

L7 load balancing:
- Path routing: `/api → backend1`, `/static → backend2`
- Host routing: `api.example.com → svc1`, `app.example.com → svc2`
- Method, header, query, source IP routing
- HTTP/2 + gRPC + WebSocket
- TLS termination
- WAF integration
- OIDC auth (offload)

Target types: Instance, IP, Lambda.

## NLB

L4 (TCP/UDP/TLS) load balancing:
- Static IP per AZ (or EIP)
- Extreme perf (millions QPS)
- Source IP preserved
- TLS termination optional

Used for:
- Non-HTTP (gaming, IoT)
- Need static IPs
- Ultra-low latency
- Extremely high throughput

## Target Groups

Define backend pool:
- Targets: instances, IPs, ALBs
- Health check: HTTP path, TCP, gRPC
- Algorithm: round-robin, least-outstanding, weighted

## Listeners

What to do with arriving traffic:
- ALB: listener on 80/443; rules route
- NLB: listener forwards to target group

## SSL/TLS

LB terminates TLS:
- ACM-managed certs (free for AWS-issued)
- SNI support (multiple certs per ALB)
- Cipher suites configurable (security policy)

Cert renewal: automatic for ACM.

Backend: HTTP (re-encrypt optional).

## Health Checks

Frequent probes; remove unhealthy targets.
- Interval (default 30s)
- Timeout (5s)
- Healthy threshold (5 consecutive)
- Unhealthy threshold (2 consecutive)

Path: `/healthz` returning 200.

## Sticky Sessions

ALB cookie: route requests from same client to same target.

Useful if app stores state in memory (anti-pattern; prefer stateless).

## Cross-Zone

Each AZ has LB nodes. With cross-zone enabled: distribute across all AZs evenly. Off: each LB node only routes to its AZ targets.

ALB: on by default.
NLB: off by default; enable for even distribution.

## Connection Draining (Deregistration Delay)

When target removed (deploy/scale-in): finish in-flight requests; close after delay.

Set to >= max request duration (e.g., 30-60s).

## Pricing

ALB: $0.0225/hour + LCUs (load balancer capacity units; ~$0.008 each).
NLB: $0.0225/hour + NLCUs.
LCU = max(new conns/s, active conns, processed bytes, rule evals).

For 1M req/day: ~$25/mo.
For 1B req/day: significant.

## Other Cloud LBs

### Azure
- Application Gateway (L7)
- Load Balancer (L4)
- Front Door (global L7)
- Traffic Manager (DNS-based)

### GCP
- Cloud Load Balancing (global)
  - External HTTP(S) LB (global anycast L7)
  - Internal LB
  - Network LB (L4)
  - TCP/SSL Proxy

GCP global LBs unique: one anycast IP serving globally; routes to nearest region.

## L7 LB Features

### Path-Based Routing
```
/api/* → api-targets
/static/* → static-targets
default → app-targets
```

### Host Routing
```
api.example.com → api-tg
admin.example.com → admin-tg
```

### Header-Based
```
Header X-Env: canary → canary-tg
else → main-tg
```

For blue/green, canary.

### Weighted
70% to v1, 30% to v2. Gradual rollout.

## L4 vs L7 Decision

L4 when:
- Non-HTTP
- Need ultra-low latency
- Need source IP
- Simple
- Static IP

L7 when:
- HTTP/HTTPS
- Need path/header routing
- TLS termination wanted
- WebSocket
- Want WAF / auth offload

Often both: NLB → ALB → app (NLB for ingress; ALB for HTTP routing).

## Internal vs Internet-Facing

- Internet-facing: public IPs; in public subnets
- Internal: private IPs; in private subnets

For microservices: internal ALBs.

## Health Check Path

```
/healthz → 200 OK if I can serve
```

Should:
- Be cheap (no DB call typically)
- Check dependencies if needed (DB connection)
- Differentiate liveness (running) vs readiness (can serve)

K8s readiness vs liveness probes are analogous.

## Connection Limits

ALB: 25k+ concurrent (default)
NLB: millions

If client side connection pool too large: SG and OS limits matter.

## Common Mistakes

- ALB without HTTPS
- LB without health check
- Cross-zone off (uneven load)
- Single-AZ (LB AZ failure = down)
- No connection draining (drops in-flight)
- Health check path returns 200 for OOM-trashing app

## Cost Optimization

- Right-size: ALB vs CloudFront
- Consolidate (one ALB; multiple paths)
- Skip LB for internal point-to-point if not needed

## Global Load Balancing

Across regions:
- Route53 latency / weighted / failover
- CloudFront (CDN with origin failover)
- AWS Global Accelerator (anycast IPs to regional LBs)
- GCP global LB (one anycast IP globally)

## Best Practices

- Terminate TLS at the LB with ACM-managed certs (auto-renew, SNI for multiple domains); re-encrypt to backends when traffic is sensitive.
- Deploy across multiple AZs and enable cross-zone balancing (default on ALB, off on NLB) for even load.
- Give every target group a meaningful health check that distinguishes liveness from readiness — don't return 200 from an app that can't actually serve.
- Set deregistration delay (connection draining) ≥ max request duration so deploys/scale-in don't drop in-flight requests.
- Keep apps stateless and avoid sticky sessions; use header/weighted routing for canary and blue/green rollouts instead.
- Put internal services behind internal LBs (private subnets) and only expose internet-facing LBs in public subnets.

## Quick Refs

L4 vs L7 picker:

| Choose L4 (NLB) | Choose L7 (ALB) |
|---|---|
| Non-HTTP (gaming, IoT, TCP/UDP) | HTTP/HTTPS/gRPC |
| Ultra-low latency, millions QPS | Path/host/header routing |
| Static IP, source IP preserved | TLS termination, WAF, auth offload |

AWS LB types: ALB (L7) · NLB (L4, static IP) · GWLB (L3 appliance insertion) · CLB (legacy). Common pattern: NLB ingress → ALB → app.

Global load balancing options: Route 53 (latency/weighted/failover DNS), CloudFront (CDN + origin failover), AWS Global Accelerator (anycast → regional LBs), GCP global LB (single anycast IP).

Pricing feel: ALB/NLB ~$0.0225/hr + capacity units (LCU/NLCU = max of new conns/s, active conns, bytes, rule evals). ~$25/mo at 1M req/day.

## Interview Prep

**Junior**: "L4 vs L7."

**Mid**: "ALB vs NLB."

**Senior**: "LB cross-zone tradeoff."

**Staff**: "Global LB strategy for multi-region app."

## Next Topic

→ [T03 — DNS, CDN](T03-DNS-CDN.md)
