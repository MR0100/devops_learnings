# L03/C03/T03 — DNS Caching, TTLs, and Why TTLs Lie

## Learning Objectives

- Understand DNS caching layers
- Plan TTL strategy for changes
- Recognize when TTLs are violated

## Caching Layers

```
Browser (cache)
  ↓ miss
OS stub resolver (cache: systemd-resolved, glibc nscd)
  ↓ miss
Recursive resolver (cache: 8.8.8.8 et al.)
  ↓ miss
TLD / Authoritative servers
```

Each layer caches; reduces upstream load.

## TTL (Time to Live)

Each DNS record has TTL in seconds. "Cache for N seconds."

```
example.com. 3600 IN A 93.184.216.34
              ↑
              cache for 1 hour
```

## Why TTLs Lie

Many actors don't respect TTL:

### Browsers
- Cache for session lifetime (sometimes ignoring TTL)
- Chrome `chrome://net-internals/#dns` to flush

### OS Caches
- systemd-resolved caches honor TTL but with min/max enforced
- glibc nscd has its own (often longer) settings
- Many apps cache via own libraries

### JVM
**Caches forever by default**. Notorious.
```
networkaddress.cache.ttl=60                  # override in security.properties
networkaddress.cache.negative.ttl=10
```

### Recursive Resolvers
- May floor TTL to prevent excessive queries
- Some clamp to max (e.g., 5 min)

### Apps with Connection Pools
- DNS resolved once at connection establishment
- Pool keeps connections alive for hours
- Doesn't re-resolve

### NAT / CGNAT
- May cache or rewrite responses

## The "TTL = Failover Time" Myth

A 60-second TTL doesn't mean failover in 60 seconds:
- Old clients keep using cached entries
- JVMs cache forever
- Browsers cache per session
- Connection pools persist

Reality: budget 1-5 minutes minimum for DNS-based failover.

## Pre-Migration TTL Strategy

For planned DNS changes:

```
Day -7: lower TTL from 1h to 60s
        (this takes up to 1 hour for caches to expire)
Day -6 onwards: caches now use 60s TTL
Day 0: make the change
Day +1: raise TTL back to 1h (after change verified)
```

Wait at least 1 old-TTL period before relying on new short TTL.

## TTL Tradeoffs

| Short TTL | Long TTL |
|---|---|
| Fast updates | Slow updates |
| More DNS queries | Less load |
| Higher DNS bill (per-query pricing) | Lower bill |
| Better failover | Worse failover |

Typical:
- Static IP for an apex: 1h-24h
- ALB endpoints: 60s (alias records often have AWS-managed shorter TTL)
- Failover targets: 30-60s
- Internal infra: 5-15 min

## Negative Caching (NXDOMAIN TTL)

Negative responses are cached too, controlled by SOA's `minimum TTL` field. If you fix a record but resolvers cached NXDOMAIN, it takes that long to clear.

## TTL Inheritance in Zones

If individual record has no TTL, falls back to:
1. `$TTL` directive at top
2. SOA's minimum

## Browser Cache Tour

```
Chrome:   chrome://net-internals/#dns
Firefox:  about:networking#dns
Edge:     edge://net-internals/#dns
```

Each shows entries and lets you flush.

## OS Cache Flush

```bash
# Linux (systemd-resolved)
sudo systemd-resolve --flush-caches
resolvectl statistics

# macOS
sudo killall -HUP mDNSResponder
sudo dscacheutil -flushcache

# Windows
ipconfig /flushdns
```

## Operational Practice

### Before Changes
- Check current TTL: `dig +nocmd example.com A +noall +answer`
- Lower TTL well in advance

### After Changes
- Verify: `dig @8.8.8.8 example.com; dig @1.1.1.1 example.com`
- Various resolvers may cache differently

### Monitor
- DNS query rate (sudden drop = something cached and isn't refreshing)
- Resolution latency
- NXDOMAIN rate

## Cloud-Native Implications

### K8s CoreDNS
- Pod queries CoreDNS
- CoreDNS caches with own TTL
- Multiple resolvers (CoreDNS, NodeLocal DNS) layer

### Service Mesh
- Envoy resolves on connection
- DNS refresh interval configurable

### Mobile / Edge
- Carrier networks may cache aggressively
- Hard to ensure clean cutover

## Common Mistakes

- **Believing "60s TTL = 60s failover"**: JVMs cache forever, browsers cache per session, connection pools never re-resolve, and some resolvers floor/clamp TTLs. Budget minutes, not seconds, for DNS-based failover.
- **Lowering TTL the day of the change**: the *old* TTL must expire first. Drop TTL at least one full old-TTL period in advance, or stale caches ignore your new short value.
- **Forgetting negative caching**: NXDOMAIN responses are cached per the SOA `minimum` field. Fixing a missing record doesn't help users who already cached "doesn't exist" until that timer expires.
- **Ignoring the JVM**: `networkaddress.cache.ttl` defaults to caching forever (or `-1`) under a SecurityManager. A Java fleet can keep hitting a decommissioned IP indefinitely.
- **Assuming connection pools re-resolve**: DNS is resolved once at connection setup; long-lived pools (DB, HTTP keep-alive, Envoy) pin to the old IP until connections are recycled.
- **Verifying against only one resolver**: caches diverge — confirm a change has propagated across `8.8.8.8`, `1.1.1.1`, and the authoritative server, not just your laptop.

## Best Practices

- **Pre-stage migrations**: lower TTL (e.g., 1h→60s) a week ahead, wait one old-TTL period, make the change, verify, then raise TTL back once stable.
- **Match TTL to volatility**: stable apex 1h-24h; ALB/failover targets 30-60s; internal infra 5-15 min. Short TTLs cost query volume (and money on per-query pricing).
- **Force re-resolution where it matters**: cap JVM cache TTL, recycle connection pools on cutover, and set explicit DNS refresh intervals in Envoy/service mesh.
- **Tune the SOA `minimum` (negative TTL) low** for zones that change often, so NXDOMAIN fixes propagate quickly.
- **Validate propagation across multiple public resolvers and the authoritative server** before declaring a change complete.

## Quick Refs

Caching layers (each can hold a record): browser → OS stub (systemd-resolved/nscd) → recursive resolver → authoritative. Negative (NXDOMAIN) TTL comes from the SOA `minimum` field.

Typical TTLs: apex/static 1h-24h · ALB/alias 60s · failover 30-60s · internal 5-15 min.

```bash
# Read the current TTL straight from the authoritative server
dig +nocmd @ns1.example.com example.com A +noall +answer

# Verify propagation across resolvers
dig @8.8.8.8 example.com +short ; dig @1.1.1.1 example.com +short

# Flush local caches
sudo systemd-resolve --flush-caches              # Linux (systemd-resolved)
sudo killall -HUP mDNSResponder                  # macOS
ipconfig /flushdns                               # Windows
# Browser: chrome://net-internals/#dns  |  about:networking#dns

# JVM: cap DNS cache (security.properties)
# networkaddress.cache.ttl=60
# networkaddress.cache.negative.ttl=10
```

## Interview Prep

**Mid**: "How long until a DNS change takes effect?"

**Senior**: "Why might a DNS change not take effect for some users even after TTL expires?"

**Staff**: "Plan a DNS failover for a critical service. Walk through TTL strategy."

## Next Topic

→ [T04 — DNSSEC](T04-DNSSEC.md)
