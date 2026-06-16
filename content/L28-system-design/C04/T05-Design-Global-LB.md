# L28/C04/T05 — Design a Global Load Balancer

## Learning Objectives

- Design global LB
- Anycast architecture

## Requirements

### Functional
- Route to nearest region
- Failover on region down
- TLS termination
- DDoS protection
- L7 routing

### Non-Functional
- < 50 ms TTFB globally
- 99.999% availability
- Petabytes/day throughput

## Estimation (derived)

Derive PoP count from the latency budget, not from a round number. TTFB < 50 ms with cross-continent RTT at ~150 ms means **you cannot serve a far user from a central origin** — the speed of light forbids it. So PoPs must be near users:
```
target_rtt        = < 50 ms  →  user-to-PoP must be ~< 25 ms one way
~25 ms one-way    ≈ within ~2,500 km of the user
→ need PoPs on every populated continent, dozens to hundreds globally
```
Now bandwidth, derived from throughput:
```
throughput        = 1 PB/day
bytes/sec         = 1e15 / 86,400 ≈ 11.6 GB/s ≈ 93 Gbps aggregate
pops              = 200
per_pop_bandwidth = 93 Gbps / 200 ≈ 0.5 Gbps avg, multiples at peak
```
And the availability target sets the failover requirement:
```
99.999% = ~5 min downtime/year  →  failover must be automatic and sub-second
```
That 5-minutes-a-year budget is why failover is **BGP/anycast (sub-second)**, not DNS (TTL-bound, tens of seconds) — derived from the SLA, not preference.

## Components

### Anycast IPs
Same IP from many POPs.

### Edge POPs
- L4 / L7 LB
- TLS termination
- Cache
- Edge compute

### Origin Routing
- Geo / latency-based
- Health-aware

### Health Checks
- Multiple sources
- Origin liveness
- Auto-failover

### Edge Compute
- Custom logic
- A/B
- Auth

### DDoS
- Absorb at edge
- Scrubbing
- Rate limiting

## Architecture

```
User → DNS → Anycast IP → Nearest POP
                       ↓
                    ECMP to LB nodes (Maglev-like)
                       ↓
                    L4 then L7
                       ↓
                    Edge cache (CDN)
                       ↓
                    Origin (regional)
```

## BGP

Each POP announces:
- Same prefix
- Internet routes to nearest

## Deep Dive: Why Anycast + Maglev

**Anycast** announces the *same* IP prefix from every PoP via BGP; the internet's routing naturally delivers each user to the topologically nearest PoP. That gives two things for free: low latency (nearest PoP) and fast failover (withdraw the prefix and traffic re-routes in seconds, no DNS TTL wait). The catch — a routing change can move a flow to a different PoP mid-connection — is why the L4 tier must be **connection-stable**.

**Maglev** (Google's L4 LB) solves exactly that:
- **Consistent hashing** maps a 5-tuple flow to the same backend even as the backend set changes, so a re-routed packet still lands on its connection's server.
- **Direct Server Return (DSR)**: responses bypass the LB and go straight to the client, so the LB only sees ingress — critical when egress is the petabyte-scale direction.
- **Stateless**: any Maglev node can handle any packet (state is in the hash, not the node), so they scale with ECMP and survive node loss without dropping connections.

## Deep Dive: L7 at the Edge

After L4 picks a backend, the L7 tier does the expensive, stateful work close to the user:
- **TLS termination** at the edge (session setup is RTT-bound, so terminating near the user saves round trips); keep-alive to origin over the backbone.
- **HTTP routing / WAF / auth**: reject bad traffic at the edge before it crosses the backbone — cheapest place to drop it.
- **Cache**: serve static and cacheable dynamic content from the PoP; an **origin shield** (a mid-tier cache) collapses many PoP misses into one origin request so a cold cache doesn't stampede the origin.

The layering matters: L4 is fast/stateless/connection-stable, L7 is smart/stateful/cache-aware. Putting L7 logic in L4 would kill throughput; putting L4 stability in L7 would break connections on re-route.

## Failover

POP failure:
- BGP withdraws
- Other POPs serve
- Sub-second

Region failure:
- Origin health
- DNS or app-level retry

## Scale

For petabytes/day:
- 200+ POPs
- Massive compute
- Custom hardware sometimes

## Real Examples

### Cloudflare
Massive anycast.

### AWS CloudFront + Global Accelerator
Similar.

### Google Front End (GFE)
Global LB for all Google services.

### Akamai
Largest CDN.

## Trade-Offs

- Build vs buy (Cloudflare etc.)
- Anycast complexity
- Edge compute limits

## Best Practices

- Anycast for low latency
- BGP for failover
- L4 + L7 layered
- Edge cache
- DDoS at edge

## Common Mistakes

- DNS-only (slow failover)
- Single POP (no anycast)
- No DDoS
- No edge cache

## Quick Refs

```
Components:
- Anycast IP
- BGP announcements
- POPs (L4 + L7)
- TLS termination
- Edge cache (CDN)
- Edge compute
- DDoS

Pattern: User → DNS → IP → POP → Origin
```

## Interview Prep

**Senior**: "Why anycast instead of DNS-based geo-routing?" — DNS failover is bounded by TTL and resolver caching, so it's tens of seconds at best — too slow for a 99.999% (5 min/year) target. Anycast announces one IP from every PoP via BGP, so routing delivers users to the nearest PoP and failover is just withdrawing a prefix — sub-second, no TTL wait. The trade is that flows can re-route mid-connection, which the L4 tier has to absorb.

**Staff**: "Design a global load balancer for sub-50ms TTFB worldwide." — The latency budget forces the architecture: cross-continent RTT is ~150 ms, so I can't serve far users from a central origin — I need PoPs within ~2,500 km of users, hundreds globally, each announcing an anycast IP. Maglev-style L4 (consistent hashing + DSR + stateless) keeps connections stable through re-routes, L7 terminates TLS and runs WAF/cache at the edge, and an origin shield protects the origin. Failover is BGP withdrawal, derived from the five-nines budget.

**Principal**: "A whole PoP just failed and you're absorbing a DDoS at the same time — what happens?" — The PoP withdraws its BGP prefix and neighboring PoPs absorb its traffic within seconds; because L4 is stateless with consistent hashing, in-flight connections re-establish on surviving nodes rather than black-holing. The DDoS is scrubbed at the edge — anycast itself dilutes a volumetric attack across all PoPs, the L7/WAF tier drops malicious requests before they cross the backbone, and rate limiting caps abusive sources. The design principle is that both failures are handled by the *same* property — distributed, stateless edge with automatic re-routing — rather than a special-case runbook.

## Next Topic

→ [T06 — Design Netflix's Deployment Platform](T06-Design-Spinnaker.md)
