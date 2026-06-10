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

## Maglev

L4 LB:
- Consistent hashing
- DSR
- Stateless

## L7

After L4:
- TLS termination
- HTTP routing
- Cache

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

**Staff**: "Global LB."

**Principal**: "Anycast architecture."

## Next Topic

→ [T06 — Design Netflix's Deployment Platform](T06-Design-Spinnaker.md)
