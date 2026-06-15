# L24/C07/T01 — Volumetric Attacks

## Learning Objectives

- Recognize DDoS types
- Defend bandwidth

## DDoS

Distributed Denial of Service:
- Many sources
- Overwhelm target
- Bandwidth or CPU

## Volumetric

Saturate bandwidth:
- 100 Gbps+ floods
- Network unable to forward

Examples:
- UDP flood
- ICMP flood
- DNS amplification
- NTP amplification

## Amplification

Send small request → server returns huge:
```
1-byte DNS query → 60-byte response
Amplification: 60×
```

Spoof source = victim IP.

Mitigation: rate limit on reflectors.

## Memcached Amplification

2018: 1.7 Tbps attack:
- Spoof source
- Memcached returns large data
- Massive amplification

For: patched; closed by default.

## SYN Flood

TCP handshake abuse:
- Send SYNs
- Half-open connections
- Server resources exhausted

Mitigation:
- SYN cookies
- Increase backlog

## UDP Flood

Pure bandwidth waste.

Mitigation:
- Drop at network edge
- Cloud-scale absorption

## Defense

### Cloud Scrubbing
- AWS Shield
- Cloudflare
- Akamai Prolexic

Re-route traffic; scrub; forward clean.

### BGP Diversion

Announce wider range; scrub center receives.

### Anycast

Disperse:
- Attack at 1 POP = absorbed locally

### Over-Provision

Headroom for spikes.

## Detection

Sudden bandwidth spike:
- 10× normal
- Auto-trigger mitigation

## Cost

Bandwidth attacks: expensive for victim.

DDoS-as-a-Service: cheap.

Imbalance favors attacker.

## CDN Mitigation

Cloudflare etc:
- All traffic via CDN
- DDoS absorbed at edge
- Origin protected

## Best Practices

- CDN in front
- DDoS protection (Shield, etc.)
- Monitor bandwidth
- Practice response
- Have runbook

## Common Mistakes

- Origin exposed
- No DDoS plan
- Insufficient capacity
- No monitoring

## Quick Refs

```
Volumetric: bandwidth
Amplification: small → huge
SYN flood: TCP handshake
UDP flood: pure bytes

Defense:
- CDN absorbs
- Anycast disperses
- Cloud scrubbing
- BGP diversion
```

## Interview Prep

**Mid**: "Volumetric DDoS."

**Senior**: "Amplification."

**Staff**: "DDoS architecture."

## Next Topic

→ [T02 — L7 Attacks](T02-L7-Attacks.md)
