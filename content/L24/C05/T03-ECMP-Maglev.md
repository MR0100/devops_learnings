# L24/C05/T03 — ECMP & Maglev (Google's L4 LB)

## Learning Objectives

- Understand ECMP
- Know Maglev

## ECMP

Equal Cost Multi-Path:
- Multiple routes to destination
- Same cost
- Hash to pick

For: distribute traffic.

## Example

```
Source → Router → 
  ├─ Path 1 (via R2)
  ├─ Path 2 (via R3)
  └─ Path 3 (via R4)
```

Router hashes 5-tuple:
- (src IP, dst IP, src port, dst port, protocol)
- Pick path

Consistent: same flow → same path.

## Use Cases

### Backbone
Multiple paths between data centers.

### Server LB
Multiple servers behind anycast IP:
- ECMP distributes
- Each server gets ~1/N

### Top-of-Rack
ECMP to spine switches.

## Stateless

Routers don't track flows:
- Just hash + pick
- Scales massively

## L4 LB Without ECMP

Traditional:
- LB tracks state
- Sticks per flow
- Scaling needs sync

For: limited.

## Maglev (Google)

Google's L4 LB:
- ECMP from network
- Hash-based backend selection
- Consistent hashing

```
Packet → ECMP → Maglev instance → Hash backend → Forward
```

## Consistent Hashing Lookup Table

```
Backend ring: 65537 slots
Each backend: weight × slots
Hash flow → slot → backend
```

Backend added/removed: minimal rehash.

## Why

Each Maglev:
- Same lookup table
- Same flow → same backend
- No state sync needed

## Benefits

- Scales linearly
- HA (any instance can serve)
- No central state

## Implementation

DSR (Direct Server Return):
- Maglev receives packet
- Forwards to backend
- Backend responds direct to client

For: high throughput.

## Failover

Backend dies:
- Lookup table updated
- New flows to others
- Existing flows: usually rerouted to alive

## ECMP in K8s

```bash
# Cilium / Calico support ECMP
```

For: BGP-based K8s LB.

## ECMP + Anycast + LB

```
Internet (anycast)
   ↓
Router (ECMP)
   ↓
Many LBs (Maglev-like)
   ↓ DSR
Many backends
   ↓ direct response
Internet
```

For: massive scale + low latency.

## Real Examples

### Google
Maglev for all traffic.

### Facebook (Meta)
Katran (similar; eBPF).

### Cloudflare
Similar architecture.

## XDP / eBPF

Modern L4 LB:
- XDP (kernel)
- Faster than Maglev (no userspace)
- Katran open-source

## Best Practices

- ECMP for multi-path
- Consistent hashing for stickiness
- DSR for high throughput
- eBPF for newest

## Common Mistakes

- ECMP without symmetric routing (asymmetric drops)
- LB stateful at scale (sync hell)
- No flow stickiness

## Quick Refs

```
ECMP: equal-cost paths; flow-hash
Maglev: Google's L4 LB
Katran: Meta's eBPF LB
DSR: direct return
Anycast + ECMP + L4 LB = scale
```

## Interview Prep

**Senior**: "ECMP."

**Staff**: "Maglev architecture."

**Principal**: "L4 LB at scale."

## Next Topic

→ Move to [L24/C06 — TLS Termination Patterns](../C06/README.md)
