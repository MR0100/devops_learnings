# L24/C07 — DDoS Protection

## Topics

- **T01 Volumetric Attacks** — Bandwidth saturation
- **T02 L7 Attacks** — Application-level
- **T03 AWS Shield, Cloudflare DDoS Protection** — Mitigations

## Attack Types

### L3/L4 Volumetric
- UDP flood, ICMP flood, SYN flood, amplification (DNS, NTP, memcached)
- Saturate network bandwidth or state tables
- Measured in Gbps to Tbps
- Examples: 2.4 Tbps Azure (2021), 3.47 Tbps Cloudflare (2022)

### L7 Application
- HTTP flood (many GETs)
- Slowloris (slow HTTP)
- Targeted expensive endpoints (login, search, complex query)
- Lower volume (millions of req/s); harder to distinguish from real traffic

### Reflection / Amplification
Attacker spoofs source IP as victim; sends small queries to amplifiers; amplifiers send large responses to victim.

- DNS: 50× amplification
- NTP: 500×
- memcached (UDP): 50,000× (record-breaking attacks)

Solution: providers shut down open amplifiers; rate-limit responses.

## Defenses

### Anycast Absorption
- Attack spreads across many PoPs
- Each PoP absorbs small share
- Cloudflare claims 200+ Tbps total capacity

### Scrubbing Centers
- Suspicious traffic routed to scrubbing facility
- Filters; sends clean traffic to origin
- Used by Akamai, Radware, vendors-of-last-resort

### Rate Limiting (per IP, per route, per user)
- Reject excess
- Distinguish attack from popularity

### CAPTCHAs / JS Challenges
- Bot detection
- Increase cost to attacker
- Hassle for users (use sparingly)

### Connection Limits
- TCP SYN cookies
- Half-open connection limits
- Conntrack tuning

### WAF Rules
- Pattern-match common L7 attacks
- Bad-bot signatures
- IP reputation lists

## Cloud Provider Solutions

### AWS
- **Shield Standard** (free, automatic) — L3/L4
- **Shield Advanced** ($3000/mo + per-resource) — 24/7 DRT, L7 visibility, cost protection, advanced reporting
- **WAF** — L7 rules
- **CloudFront** — anycast + caching dampens attacks
- **Global Accelerator** — anycast for non-HTTP

### Cloudflare
- All tiers include DDoS protection (free + paid)
- Massive network capacity
- Magic Transit (L3 protection for entire networks)
- Spectrum (TCP/UDP protection)

### GCP
- **Cloud Armor** (WAF + DDoS)
- **Cloud Armor Adaptive Protection** (ML-based)

### Azure
- **DDoS Protection Standard**
- **Front Door** (CDN with WAF)
- **Application Gateway WAF**

## Architecture for DDoS Resilience

```
[Client]
   ↓
[CDN / Anycast Edge] ← absorbs volume; caches; bot detection
   ↓ healthy clean traffic only
[WAF] ← L7 rules
   ↓
[Load Balancer] ← health-check + auto-scaling
   ↓
[Origin] ← protected by all layers above
```

### Origin Hiding
- Origin IP never published
- Only CDN knows origin
- WAF rule: drop traffic that bypasses CDN

### Bot Detection
- JS challenge (browser must execute)
- Behavioral analysis (mouse movement, etc.)
- Reputation (known bad IPs)

## Run-Book for Active Attack

1. **Detect**: anomalous traffic; alert fires
2. **Assess**: type (L3/L4 vs L7)? Source IPs? Pattern?
3. **Engage provider DRT** if Shield Advanced / Cloudflare Pro
4. **Apply rules**: rate limit, WAF rule, geo block specific countries if source-clear
5. **Communicate**: status page; "we're aware"
6. **Monitor**: ensure protections holding
7. **Post-incident**: tune rules; improve runbook

## Cost Considerations

### Pay-as-you-go egress
A massive DDoS can spike egress costs.
- Shield Advanced has cost protection
- Cloudflare absorbs at edge (no origin egress)

### Pre-provisioning
- AWS Shield Advanced: $3000/mo minimum
- Worth it if business risk warrants

### Auto-scaling
- Scaling up DURING attack helps absorb load
- But can cost a fortune
- Combine with rate limiting

## Real Attack Examples

### Memcached Amplification (Feb 2018)
- Attackers spoofed source IP; queried open memcached servers (UDP); responses 50,000× larger
- 1.7 Tbps attack against GitHub (largest at the time)
- Mitigation: tighter memcached defaults (later versions disable UDP)

### Mirai (2016)
- IoT botnet
- Attacked Dyn (DNS provider) → much of US Internet appeared down
- Mitigation: many things, including IoT vendor security

### HTTP/2 Rapid Reset (2023)
- L7 attack abusing HTTP/2 stream cancellation
- Cloudflare, AWS, Google saw 100M+ req/s attacks
- Mitigation: rate-limit stream creation per connection

## What Doesn't Work

- **iptables on origin** — packet floods saturate NIC before iptables runs
- **Geo-blocking entire continents** — many real users harmed
- **Manual whack-a-mole** — attackers adapt faster than humans
- **Single-region defense** — attackers go where you can't (Internet ingress points)

## Best Practices

- Always be behind a CDN
- Cache static content at edge (less origin load)
- WAF rules for top OWASP risks
- Bot detection
- Rate limiting per route
- Monitoring (sudden traffic spikes)
- Runbook + game day quarterly

## Interview Themes

- "DDoS defense layers"
- "L3/L4 vs L7 attacks"
- "Anycast absorbs DDoS — how?"
- "Walk through response to active attack"
- "Origin hiding — design"
