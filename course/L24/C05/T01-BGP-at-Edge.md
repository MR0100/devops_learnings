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

BGP picks best route:
1. Highest local preference
2. Shortest AS path
3. Lower MED
4. Older route

For: policy-driven.

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

**Senior**: "BGP role."

**Staff**: "Edge with BGP."

**Principal**: "ISP-level networking."

## Next Topic

→ [T02 — Anycast in Practice](T02-Anycast.md)
