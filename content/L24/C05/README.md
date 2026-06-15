# L24/C05 — BGP, Anycast, ECMP

## Topics

- **T01 BGP at the Edge** — Internet routing
- **T02 Anycast in Practice** — Cloudflare, Global Accelerator
- **T03 ECMP & Maglev** — Equal-cost paths, Google's LB

## BGP (Border Gateway Protocol)

The Internet's routing protocol. Connects Autonomous Systems (ASes).

### AS
- An "Autonomous System" = network under one admin (ISP, cloud provider, large corp)
- AS number (ASN), e.g., AS13335 (Cloudflare), AS16509 (Amazon)
- ~100K ASes worldwide

### iBGP vs eBGP
- **iBGP**: between routers in same AS
- **eBGP**: between ASes (Internet routes)

### How It Works
1. AS announces "I have IP prefixes X.X.X.0/24"
2. Neighbors learn; forward to their neighbors
3. Path attributes (AS_PATH, local_preference, MED) shape decisions
4. Shortest AS_PATH usually wins

```
AS1 ────── AS5 ────── AS9
AS1 ─ AS2 ─ AS5            ← AS1's view of paths to AS5
```

Both work; AS1 picks based on policy + AS_PATH length.

### Famous BGP Outages
- **Facebook (2021)**: BGP config error withdrew their entire prefix; site disappeared
- **Cloudflare (2019)**: leaked prefix from a customer
- **YouTube (2008)**: Pakistan hijacked YouTube prefix; brief global outage

BGP has minimal security; trust-based. Improvements: RPKI (validate origin).

## Anycast

Same IP advertised from many locations.

```
Internet routes packets to nearest (lowest AS_PATH) location.

Cloudflare 1.1.1.1 is announced from 300+ PoPs.
Internet routing automatically directs each client to nearest PoP.
```

### Use Cases
- DNS (root nameservers, 8.8.8.8, 1.1.1.1)
- CDN edges
- DDoS absorption (attack distributes across PoPs)
- HTTP edge (Cloudflare, Fastly)
- AWS Global Accelerator

### Stateful Connections + Anycast
TCP keeps connection to one anycast endpoint. Routing changes mid-flow → connection breaks.

In practice: route stability is good enough for most TCP. UDP (DNS, QUIC) handles re-routing seamlessly.

## AWS Global Accelerator

Anycast IPs + AWS backbone.

```
Client → Anycast IP (Cloudflare-like edge)
       → AWS backbone (low jitter)
       → Endpoint Group(s) in regions
       → ALB / NLB / EC2 / EIP
```

### Use
- Lower-latency global services (skip random Internet routing)
- Fast multi-region failover (two anycast IPs; auto-shift on health)
- Bypass slow ISP paths

## ECMP (Equal-Cost Multi-Path)

When multiple paths have equal cost, spread traffic.

### Routing-Level ECMP
- Multiple routes to same destination
- Router hashes 5-tuple → picks path
- Used for: balanced bandwidth across links

### Server-Level ECMP
- Multiple LB instances; each advertises same anycast IP
- Routers spread across them
- Used by: Google Maglev, Facebook Katran, AWS NLB (under the hood)

### Maglev (Google)

Google's L4 LB. Uses consistent hashing + ECMP:
- Each LB instance announces anycast IP via BGP
- Routers ECMP across LB instances
- Each LB has identical consistent-hashing table
- All hash a request to the same backend
- Backend changes (failure) only re-route minimal traffic

Result: stateless, fast, fault-tolerant L4 LB at planet scale.

Open-source equivalent: **Katran** (Facebook, BPF-based).

## XDP / eBPF for High-Performance LB

eBPF allows kernel-level packet processing without leaving kernel:
- Cilium uses XDP for L4 LB
- Katran uses XDP
- Performance: tens of millions of packets per second

## BGP at the Cloud Edge

Major cloud providers run their own BGP:
- AWS announces VPC CIDRs via BGP (DX, VPN)
- Cloudflare, Akamai, etc. peer with ISPs globally
- Anycast is BGP-based

### Cross-AS Peering
- **Public peering** (Internet Exchanges like LINX, AMS-IX)
- **Private peering** (direct fiber, e.g., AWS to your network via DX)

## RPKI (Route Origin Validation)

Cryptographic verification of "this AS is allowed to announce this prefix."
- Reduces hijacks
- Slowly being deployed
- AWS, Cloudflare, Comcast adopted

## Interview Themes

- "What is BGP and what failures does it cause?"
- "Anycast — how it works"
- "Maglev / Katran — LB architecture"
- "ECMP — when used?"
- "Global Accelerator vs CloudFront"
