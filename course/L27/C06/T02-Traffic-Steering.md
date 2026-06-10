# L27/C06/T02 — Traffic Steering

## Learning Objectives

- Steer traffic
- Granular control

## Traffic Steering

Direct traffic via:
- DNS
- Anycast
- LB weights
- App-level

For: dynamic routing.

## DNS-Based

Route 53:
- Latency
- Weighted
- Geolocation
- Failover

## Cloudflare LB

```
Pools:
  US: ALB-us-east-1
  EU: ALB-eu-west-1

Steering: geo / latency / random / proximity
```

## AWS Global Accelerator

Anycast IPs:
- 2 static IPs
- Route to nearest healthy
- Sub-second failover

For: fast.

## Use Cases

### Drain
Shift weight away.

### A/B
20% to new version (region or pool).

### Geo
EU users → EU.

### Latency
User → fastest region.

### Failover
Health → primary; fail → secondary.

## Granularity

- Per user (sticky)
- Per session
- Per request

For: stateful vs random.

## Drain Pattern

```
T-0: 100% A
T-10: 80% A, 20% B
T-20: 50% A, 50% B
T-30: 20% A, 80% B
T-40: 0% A, 100% B
```

Gradual.

## Anycast Failover

Faster than DNS:
- BGP withdraws
- Other POP serves

But: less control.

## L4 vs L7 Steering

- L4: by IP / port
- L7: by HTTP path / header / cookie

For: more flexibility L7.

## App-Level

App reads region info; routes:
```python
if user.region == 'EU':
    return call_eu_backend()
else:
    return call_us_backend()
```

For: very granular.

## Best Practices

- Plan for failover
- Gradual shifts
- Health-aware
- Anycast for low RTO
- DNS for general

## Common Mistakes

- DNS only (TTL issues)
- All-or-nothing
- No health integration
- No comms

## Quick Refs

```
DNS: Route 53 routing policies
Anycast: Global Accelerator / Cloudflare
LB: weighted pools
App: client-side routing
```

## Interview Prep

**Senior**: "Traffic steering."

**Staff**: "Multi-region routing."

**Principal**: "Global control plane."

## Next Topic

→ Move to [L28 — System Design for DevOps & Platform Engineers](../../L28/README.md)
