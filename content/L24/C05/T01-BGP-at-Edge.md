# L24/C05/T01 — BGP at the Edge

## Learning Objectives

- Understand BGP
- Use at edge

## BGP

Border Gateway Protocol:
- Inter-AS routing
- Path vector
- Internet's routing system

## AS

Autonomous System:
- Network operator
- Own AS number (ASN)
- Routes own prefixes

Examples:
- AS15169: Google
- AS13335: Cloudflare
- AS16509: Amazon

## eBGP vs iBGP

- eBGP: between ASes
- iBGP: within AS

## Path Selection

BGP picks the best route by walking an ordered tie-break list (after preferring the highest weight, a Cisco-local, pre-step):
1. Highest local preference
2. Shortest AS path
3. Lowest origin code (IGP < EGP < Incomplete)
4. Lowest MED
5. Prefer eBGP-learned over iBGP-learned
6. Lowest IGP metric to the next hop
7. Oldest (most stable) eBGP route
8. Lowest router ID / lowest neighbor address (final deterministic tiebreaker)

For: policy-driven. (Steps 1-2 are where operators usually steer traffic; the lower steps are deterministic tiebreakers. This is the standard simplification — exact ordering/weight is vendor-specific.)

## Prefix Announcement

```
AS X announces 192.0.2.0/24
   ↓
Peers learn route
   ↓
Internet routes traffic for 192.0.2.0/24 to AS X
```

## Anycast

(See T02.)

Same prefix from multiple locations:
- BGP picks nearest

## Edge BGP

CDN / cloud edge:
- Multiple POPs
- Each announces same IPs
- Closest serves users

## Configure (Cisco)

```
router bgp 65000
 neighbor 1.2.3.4 remote-as 65001
 network 192.0.2.0 mask 255.255.255.0
```

## BIRD / FRR

Linux BGP:
```
protocol bgp neighbor1 {
  local as 65000;
  neighbor 1.2.3.4 as 65001;
  ipv4 {
    import all;
    export all;
  };
}
```

## RPKI

Route Origin Authorization:
- Signed records
- "AS X authorized to announce prefix Y"
- Prevent hijack

For: security.

## Communities

Tags on routes:
- Customer routes
- Don't export
- Policy

## Looking Glass

Tools to query BGP state:
```
https://bgp.tools/
```

For: troubleshooting.

## Anycast

(Detail in T02.)

## Filtering

```
prefix-list X permit 192.0.2.0/24
neighbor 1.2.3.4 route-map filter in
```

For: limit accepted routes.

## Real-World

- ISPs run BGP
- Cloud providers
- Large enterprises
- CDNs

## Cloud BGP

- AWS Direct Connect / Cloud WAN
- Azure ExpressRoute
- GCP Cloud Interconnect

For: hybrid.

## Best Practices

- RPKI for security
- Filter announced
- Multiple peers (multi-homing)
- Monitor (looking glass)

## Common Mistakes

- Accept default route blindly
- No RPKI (hijack risk)
- Single peer (SPOF)

## Quick Refs

```
BGP peers
RPKI for ROA
Anycast for distribution
ECMP for paths
```

## Interview Prep

**Senior**: "What role does BGP play?" — It's the internet's inter-AS routing protocol: a path-vector protocol where each Autonomous System advertises the IP prefixes it owns and learns paths to everyone else. It's policy-driven (local preference, AS-path, communities), not shortest-path — operators steer traffic with policy.

**Staff**: "How do you use BGP to run an edge/CDN?" — Anycast: announce the same prefix from every POP, and BGP naturally routes each user to a topologically near site; capacity and failover come from withdrawing a prefix at a draining POP. Combine with ECMP/Maglev behind the edge for per-box load spreading. Multi-home to several transit providers for resilience, and protect against route hijacks with RPKI ROAs and strict prefix filtering.

**Principal**: "What are the failure and security concerns at ISP scale?" — Route leaks and hijacks (a misconfigured or malicious AS announcing prefixes it shouldn't) can blackhole or intercept traffic globally; defenses are RPKI origin validation, prefix/AS-path filtering, and max-prefix limits per peer. Plan for path selection determinism (the full tie-break ladder), churn/convergence under flap (dampening), and graceful POP drain/failover. Monitor with looking glasses and BGP telemetry so you detect anomalies before users do.

## Next Topic

→ [T02 — Anycast in Practice](T02-Anycast.md)
