# L03/C07/T06 — Load Balancing (L4 vs L7)

## Learning Objectives

- Distinguish L4 (transport) from L7 (application) load balancing
- Choose connection-level vs request-level distribution
- Configure health checks, connection draining, and sticky sessions
- Pick the right balancing algorithm for a workload

## What a Load Balancer Does

A load balancer (LB) sits in front of a pool of backends and spreads incoming
traffic across them. It provides three things at once:

1. **Scale** — distribute load so no single backend is overwhelmed
2. **Availability** — route around failed backends (via health checks)
3. **Abstraction** — clients see one stable VIP/DNS name, not N backends

The single most important design question is *which OSI layer it operates at*,
because that determines what it can see and what it can do.

## L4 vs L7

| | L4 (Transport) | L7 (Application) |
|---|---|---|
| Operates on | TCP/UDP connections | HTTP(S)/gRPC requests |
| Sees | IPs, ports, TCP flags | Method, path, headers, cookies, host |
| Decision unit | Per **connection** | Per **request** |
| TLS | Passthrough (or simple termination) | Terminates, inspects, can re-encrypt |
| Routing | 5-tuple hash / round-robin | Path/host/header-based |
| Overhead | Very low (often kernel/DSR) | Higher (parses payload) |
| AWS example | NLB | ALB |
| OSS example | IPVS, HAProxy (tcp mode), MetalLB | Envoy, NGINX, HAProxy (http mode), Traefik |

**L4** forwards packets/connections without understanding the payload. It's fast,
protocol-agnostic (anything over TCP/UDP), and preserves the connection end to
end. It cannot route by URL because it never reads the HTTP request.

**L7** terminates the connection, parses the application protocol, and makes
per-request decisions: send `/api/*` to one pool, `/images/*` to another, do
header-based canary routing, rewrite paths, inject headers, enforce WAF rules.
The cost is that it must decrypt TLS and parse every request.

```
Client ──TCP──► [L4 LB] ──TCP──► Backend        (one connection, one backend)
                  hash(5-tuple) → backend, sticky for life of connection

Client ──TLS──► [L7 LB] ──HTTP──► Backend A      (request 1: /api  → pool A)
                          └─HTTP──► Backend B      (request 2: /img  → pool B)
                  new routing decision PER request on the same connection
```

## Connection-Level vs Request-Level Distribution

This is the practical consequence of L4 vs L7, and a classic source of "uneven
load" incidents.

- **L4 = connection-level.** A backend is chosen once, when the connection opens,
  and every byte on that connection goes to the same backend until it closes.
- **L7 = request-level.** With HTTP keep-alive or HTTP/2 multiplexing, many
  requests share one client connection; an L7 LB can spread those individual
  requests across backends.

Why it matters:

- **Long-lived connections skew L4 balancing.** gRPC and HTTP/2 open one
  long-lived TCP connection and multiplex many requests over it. An L4 LB hashes
  that single connection to one backend, so all the requests land on one pod —
  the new pods you scaled up get nothing. Fix: use an **L7** LB (Envoy, ALB) that
  balances per request, or a client-side/mesh LB that is HTTP/2-aware.
- **Short HTTP/1.1 requests balance fine at L4** because each new connection
  re-hashes.

## Health Checks

The LB must know which backends are alive. Two kinds:

- **Active health checks** — the LB proactively probes each backend on an
  interval (`GET /healthz`, or a TCP connect for L4). Backends failing N
  consecutive probes are marked unhealthy and pulled from rotation; they return
  after M consecutive successes.
- **Passive health checks (outlier detection)** — the LB watches real traffic and
  ejects a backend that returns too many 5xx / connection errors (Envoy's outlier
  detection). Catches failures an active probe might miss.

Key parameters: interval, timeout, healthy/unhealthy thresholds, and the check
path. Two failure modes to design around:

- **Shallow checks lie.** A check that only confirms the port is open will keep
  routing to a process that is up but can't reach its database. Prefer a
  `/healthz` that exercises critical dependencies — but beware making it *too*
  deep (a slow dependency can mark your whole fleet unhealthy at once).
- **Separate liveness from readiness.** "Should I be restarted?" (liveness) is a
  different question from "should I receive traffic right now?" (readiness). LBs
  route on readiness.

## Connection Draining (Graceful Shutdown)

When a backend is removed — deploy, scale-in, or failed health check — you don't
want to sever its in-flight requests. **Connection draining** (AWS:
*deregistration delay*; Envoy/K8s: *graceful shutdown / preStop*) stops sending
the backend **new** connections while letting existing requests finish, up to a
timeout, then forcibly closes.

```
t0  Backend marked draining → no NEW requests routed to it
t0..tN  In-flight requests allowed to complete
tN  (drain timeout, e.g. 30s) remaining connections force-closed
```

Typical timeout: 30–300s. Set it longer than your slowest normal request, but
not so long that a rolling deploy stalls. In Kubernetes this pairs with a
`preStop` hook + `terminationGracePeriodSeconds` so the pod leaves the Service
endpoints before it stops accepting work.

## Sticky Sessions (Session Affinity)

Stickiness pins a given client to the same backend across requests. Mechanisms:

- **Cookie-based (L7)** — LB injects a cookie (e.g. ALB `AWSALB`, or an
  application cookie) naming the backend. Survives client IP changes; the cleanest
  option.
- **Source-IP hash (L4)** — hash the client IP to a backend. Breaks behind NAT/CGNAT
  (many users share one IP → one backend) and on IP change.

Use stickiness only when you must — it's usually a smell that the app keeps
**local session state**. Costs: uneven load, broken balancing when a hot client
dominates, and lost sessions when that backend dies. The better fix is
**stateless backends** with shared session state (Redis, signed JWT/cookie), so
any backend can serve any request.

## Balancing Algorithms

| Algorithm | How it picks | Good for |
|---|---|---|
| Round robin | Next backend in order | Uniform backends, uniform requests |
| Weighted round robin | Round robin biased by weight | Mixed instance sizes; canary % |
| Least connections | Fewest active connections | Long-lived/variable-duration requests |
| Least request (EWMA) | Lowest in-flight + latency estimate | Latency-sensitive L7 (Envoy default-ish) |
| Least response time | Lowest connections + latency | Heterogeneous backend speed |
| IP hash / consistent hash | hash(client or key) → backend | Stickiness, cache affinity |
| Power of two choices (P2C) | Pick 2 at random, take the lesser-loaded | Scales without global state |
| Random | Uniform random | Many backends; cheap, surprisingly good |

Rules of thumb:

- Equal-cost, short requests → **round robin** is fine and cheapest.
- Variable request cost or long-lived connections → **least connections / least
  request** avoids piling work on a busy backend.
- Need cache hit affinity (e.g. shard a key to a node) → **consistent hashing**,
  which minimizes reshuffling when the backend set changes.
- Huge fleets where global state is expensive → **P2C / random** approximate
  least-loaded without a central counter.

## Where LBs Live in a Stack

```
                Internet
                   │
            [ Global / DNS or Anycast LB ]   (GeoDNS, Global Accelerator)
                   │
            [ L4 LB: NLB / IPVS ]            (TCP/UDP, fast, TLS passthrough)
                   │
            [ L7 LB: ALB / Envoy / Ingress ] (HTTP routing, TLS term, WAF)
                   │
            [ Service mesh sidecar ]          (per-request, mTLS, retries)
                   │
                Backends
```

Real systems layer these: an L4 LB at the edge for raw throughput and DDoS
absorption, an L7 LB/ingress behind it for routing, and optionally a mesh for
service-to-service. DNS/Anycast does coarse *global* steering; the L4/L7 LBs do
fine-grained *local* distribution.

## Quick Refs

```bash
# AWS ELBv2 (ALB/NLB) — inspect target health & draining
aws elbv2 describe-target-health --target-group-arn <arn>
aws elbv2 describe-target-group-attributes --target-group-arn <arn> \
  | grep -i deregistration_delay        # connection draining timeout (s)

# NGINX (L7) upstream with health + algorithm
#   upstream app {
#     least_conn;                        # algorithm
#     server 10.0.1.10:8080 max_fails=3 fail_timeout=10s;
#     server 10.0.1.11:8080;
#   }

# HAProxy: L4 (mode tcp) vs L7 (mode http)
#   backend web
#     balance leastconn                  # or roundrobin / source
#     cookie SRV insert indirect nocache # cookie-based stickiness (L7)
#     option httpchk GET /healthz        # active L7 health check
#     server s1 10.0.1.10:8080 check inter 2s fall 3 rise 2

# Linux L4 LB (IPVS) — what kube-proxy uses in ipvs mode
ipvsadm -L -n                            # list virtual servers + real servers
ipvsadm -L -n --stats                    # per-backend connection stats

# Kubernetes graceful drain (pair with preStop + grace period)
kubectl get endpointslices -l kubernetes.io/service-name=<svc>
#   spec.terminationGracePeriodSeconds: 30
#   lifecycle.preStop.exec: ["sh","-c","sleep 15"]   # leave endpoints first
```

| Symptom | Likely cause |
|---|---|
| gRPC/HTTP2 load piles on one pod | L4 LB balancing per-connection; use L7 |
| New pods get no traffic after scale-up | Long-lived connections + L4 hashing |
| 502s during deploy | No/short connection draining (deregistration delay) |
| One user overloads one backend | Source-IP stickiness behind NAT |
| Healthy-looking backend serving errors | Shallow health check (port-only, not `/healthz`) |

## Common Mistakes

- **Using an L4 LB for gRPC/HTTP2 and expecting per-request balancing.** It
  balances per connection; one long connection = one backend.
- **Health check that only tests the port.** Process is up, dependency is down,
  LB keeps routing. Use a real `/healthz`.
- **No connection draining.** Deploys and scale-ins kill in-flight requests →
  user-visible 5xx and broken uploads.
- **Stickiness as a crutch for stateful backends.** Pin works until the backend
  dies; then sessions vanish. Externalize state instead.
- **Health check path that hits a shared dependency.** A slow database can flap
  every backend unhealthy simultaneously — a self-inflicted outage.
- **Same algorithm everywhere.** Round robin on long-lived connections produces
  hot backends; reach for least-connections/least-request there.

## Best Practices

- **Pick the layer for the protocol.** L4 for raw TCP/UDP throughput, TLS
  passthrough, and DDoS absorption; L7 for HTTP routing, TLS termination, and any
  multiplexed protocol (gRPC/HTTP2) that needs per-request balancing.
- **Always health-check at the application layer** (`/healthz` that exercises real
  dependencies sparingly), not just the port — but never make the check hammer a
  shared backend, or one slow dependency flaps the whole fleet unhealthy.
- **Configure connection draining** (deregistration delay / `preStop` + grace
  period) so deploys and scale-ins finish in-flight requests instead of 5xx'ing.
- **Match the algorithm to the traffic.** Least-connections/least-request for
  long-lived or uneven work; round robin only for uniform, short requests;
  consistent hashing when cache affinity matters.
- **Keep backends stateless** and externalize session state so you never depend on
  stickiness for correctness — stickiness should be an optimization, not a crutch.
- **Layer global and local LBs**: Anycast/GeoDNS for coarse region steering, L4 at
  the edge, L7 for routing, mesh for service-to-service — size each region N+1 to
  absorb failover.

## Interview Prep

**Mid**: "What's the difference between an L4 and an L7 load balancer?"
- L4 routes per TCP/UDP **connection** using the 5-tuple; it can't see HTTP. L7
  terminates TLS, parses each **request**, and routes by host/path/header. ALB is
  L7, NLB is L4.

**Senior**: "We scaled our gRPC service from 3 to 10 pods but the 3 original pods
stay hot and the new ones idle. Why?"
- gRPC runs over a single long-lived HTTP/2 connection. An L4 LB (or
  `ClusterIP`/kube-proxy) hashes each connection to one backend, so existing
  clients keep hitting their original pods regardless of new capacity. Fix:
  balance per request — an L7/HTTP2-aware proxy (Envoy, ALB), a service mesh, or
  client-side LB with periodic connection re-resolution / `GOAWAY` cycling.

**Staff**: "Design load balancing for a global, multi-region API with both REST
and gRPC traffic, zero-downtime deploys, and resilience to a regional failure."
- Layer it: Anycast/GeoDNS or Global Accelerator for region selection; per-region
  L4 LB at the edge for throughput and DDoS absorption; L7 ingress (Envoy/ALB) for
  TLS termination and per-request routing — critical so gRPC/HTTP2 balances across
  pods. Use least-request with outlier detection; readiness-gated endpoints plus
  connection draining (preStop + grace period) for zero-downtime rollouts;
  stateless backends with shared session store so no stickiness needed. For
  regional failure: health-checked global routing withdraws the dead region; size
  each region to absorb failover load (N+1 across regions).

## Next Chapter

→ [C08 — Edge & CDN Networking](../C08/README.md)
