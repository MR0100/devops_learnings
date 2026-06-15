# L24/C05/T02 — Anycast in Practice (Cloudflare, AWS Global Accelerator)

## Learning Objectives

- Understand anycast
- Use in practice

## Anycast

Same IP announced from multiple locations.
Routers pick nearest.

For: low latency + DDoS resilience.

## How

```
IP 1.1.1.1 announced from:
- NYC POP
- LON POP
- TYO POP

User in NYC: routed to NYC POP
User in TYO: routed to TYO POP
```

## Vs Unicast

- Unicast: one IP, one location
- Anycast: one IP, many locations

## Use Cases

### CDN
Edge POPs anycast same IPs:
- Cloudflare: 1.1.1.1 (DNS)
- Quad9: 9.9.9.9

### DNS
Root servers (m, k, others).
13 logical roots × hundreds of physical.

### AWS Global Accelerator
2 anycast IPs per accelerator.
Route to nearest region.

### Cloudflare Workers
All sites accessible at any POP.

## Benefits

- Low latency (nearest)
- DDoS dispersion
- HA (POP failure → reroute)

## Limitations

- Stateful protocols tricky
  - TCP: works (route stable per flow)
  - But: BGP changes can reroute mid-connection
- Per-region state hard

## TCP Anycast

Works most of time:
- Flow stays at one POP
- BGP changes: connection breaks (rare)

For: most HTTP OK.

## AWS Global Accelerator

```bash
aws globalaccelerator create-accelerator --name my-app
```

Provides 2 static IPs:
- Anycast globally
- Route to nearest ALB

For: lower TTFB.

## Cloudflare Anycast

All Cloudflare IPs anycast:
- Free tier included
- Massive POP count

For: free anycast.

## DDoS

Anycast disperses:
- 100 Gbps attack
- Distributed across 100 POPs
- 1 Gbps per POP

For: absorb easily.

## BGP Routing

Each POP announces:
- Same prefix
- BGP path: shortest
- User → nearest

For: automatic.

## Testing

```bash
# Trace from different regions
traceroute 1.1.1.1
```

From US: hits US POP.
From EU: hits EU POP.

## ECMP

(See T03.)

Multiple paths via BGP; load balanced.

## Real Examples

### Cloudflare
1.1.1.1 DNS, all sites.

### Google
Public DNS 8.8.8.8.

### AWS
S3 multi-region access points.

### Fastly
Edge.

## Best Practices

- Use anycast where possible
- TCP usually fine
- Plan for state (use Cloudflare Durable Objects, etc.)
- Monitor per-POP health

## Common Mistakes

- Stateful UDP without thought
- Region-specific state
- Single POP failure cascades

## Quick Refs

```
Anycast: same IP, many locations
BGP: routing protocol
Use: CDN, DNS, global LB
```

## Interview Prep

**Senior**: "What's anycast."

**Staff**: "Anycast architecture."

**Principal**: "Global infrastructure."

## Next Topic

→ [T03 — ECMP & Maglev](T03-ECMP-Maglev.md)
