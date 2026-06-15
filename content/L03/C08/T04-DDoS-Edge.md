# L03/C08/T04 — DDoS Protection at the Edge

## Learning Objectives

- Understand DDoS protection layers
- Apply edge-based defenses
- Recognize WAF capabilities

## DDoS Attack Categories

### Volumetric (Gbps to Tbps)
Saturate bandwidth.
- UDP flood, ICMP flood
- Amplification (DNS, NTP, memcached)
- Mitigation: anycast absorption, scrubbing

### Protocol (PPS)
Exhaust state tables.
- SYN flood
- Mitigation: SYN cookies, scrubbing

### L7 (low rate, app-specific)
HTTP floods on expensive endpoints.
- POST /login (CPU expensive)
- Slowloris (hold connections open)
- Mitigation: WAF, rate limiting, behavioral

## Edge Defenses

### Anycast Absorption
Spreads attack across hundreds of PoPs. Each absorbs small share.

Cloudflare claims 200+ Tbps total capacity. Attacks rarely overwhelm.

### TCP SYN Cookies
Don't allocate state until handshake completes. Defeats SYN floods.

Enabled by default on most modern Linux:
```bash
sysctl net.ipv4.tcp_syncookies
```

### Rate Limiting
- Per IP
- Per route
- Per token / user

Reject excess; legit traffic proceeds.

### WAF
L7 rule engine. Blocks:
- Known bad IPs
- Common attack patterns (SQLi, XSS)
- Bots (signatures + behavior)
- Geolocation rules

### Bot Detection
- JS challenge (browser executes; bots fail)
- Cryptographic challenge
- CAPTCHA
- Reputation databases

### Geo Blocking
Block traffic from specific countries / ASes.
- Be careful: blocks real users too
- Use sparingly for emergencies

## Provider Solutions

### Cloudflare
- Free tier includes DDoS protection
- Custom rules in Pro/Business/Enterprise
- Magic Transit for non-HTTP (L3/L4 protection)

### AWS
- **Shield Standard** (free, automatic): L3/L4
- **Shield Advanced** ($3000/mo + per-resource): L7, 24/7 DRT, cost protection, advanced reporting
- **WAF**: L7 rules; per-rule + per-request pricing
- **AWS Network Firewall**: VPC-level

### GCP
- Cloud Armor: WAF + DDoS
- Adaptive Protection (ML-based anomaly detection)

### Azure
- DDoS Protection Standard
- Front Door WAF
- Application Gateway WAF

## Defense in Depth

```
Internet (random users)
   ↓
Anycast Edge (absorbs volumetric DDoS)
   ↓
WAF (filters L7 attacks)
   ↓
Rate Limiting (caps requests per IP/user)
   ↓
Cache (reduces origin load)
   ↓
Origin (protected by above layers)
```

## Origin Hiding

Critical: don't publish your origin IP.
- Only CDN knows
- Configure firewall: only accept from CDN IPs
- Cloudflare publishes its IP ranges
- AWS CloudFront publishes too

Without hiding: attacker DDoS origin directly (bypass CDN).

## Sample Cloudflare Rate Limit Rule

```
Rule: rate_limit_login
  When: URI path = /login AND method = POST
  Threshold: 5 requests per IP per 1 minute
  Action: Challenge (JS)
  Duration: 1 hour
```

## Sample AWS WAF Rule

```json
{
  "Name": "RateLimitIP",
  "Statement": {
    "RateBasedStatement": {
      "Limit": 2000,
      "AggregateKeyType": "IP"
    }
  },
  "Action": { "Block": {} }
}
```

## DDoS Response Runbook

1. **Detect**: anomaly alerts, traffic spike, customer reports
2. **Confirm**: not a celebrity tweet / legitimate spike
3. **Triage**: type (L3/L4 vs L7)? source IPs? pattern?
4. **Engage**: provider DRT if Shield Advanced / Cloudflare Pro
5. **Apply rules**: rate limit, WAF, geo-block specific countries
6. **Communicate**: status page; on-call
7. **Monitor**: protections holding?
8. **Post-incident**: tune rules; runbook update

## Famous DDoS Attacks

- **GitHub 2018**: 1.35 Tbps via memcached amplification
- **Cloudflare 2022**: 26M req/s HTTPS flood
- **Microsoft Azure 2023**: 2.4 Tbps
- **Google 2023**: HTTP/2 rapid reset attack

Defenses keep evolving.

## Cost Protection

If unmitigated DDoS spikes your egress bill:
- AWS Shield Advanced: cost protection
- Cloudflare: absorbed at edge; no extra origin bill
- Self-managed: surprise $$$

## Bot Management

Different from DDoS:
- DDoS: overwhelm
- Bots: scrape, abuse, credential stuff

Tools:
- Cloudflare Bot Management
- AWS Bot Control
- Akamai Bot Manager
- Datadome / Imperva

## Things That Don't Work

- **iptables on origin**: NIC saturated before iptables runs
- **Geo-block whole continent**: harms real users
- **Manual whack-a-mole**: attackers adapt faster
- **Single-region defense**: attackers go where you can't

## Pre-Emptive Prep

- WAF rules for top OWASP risks
- Rate limit on expensive endpoints
- Cache aggressively
- Monitor traffic baselines
- Run game days
- Have a runbook + DRT contact ready

## Common Mistakes

- **Leaving the origin IP discoverable** — old DNS records, mail headers, SSL cert transparency logs, or a direct `origin.example.com` let an attacker bypass the CDN entirely. Lock the origin firewall to CDN IP ranges.
- **Defending volumetric attacks at the origin** — by the time traffic reaches your `iptables`, the NIC/link is already saturated. Volumetric mitigation must happen upstream at the anycast edge.
- **Blocking a whole country/continent in a panic** — geo-blocks take out real users and rarely match the attack's true source; use as a narrow, temporary measure only.
- **Confusing a traffic spike with an attack** — a viral post or a marketing email looks like an L7 flood. Confirm before triggering aggressive challenges that hurt real users.
- **Static thresholds with no baseline** — rate limits set without knowing normal traffic either never fire or block legitimate bursts; baseline first.
- **No tested runbook** — improvising mid-incident wastes the minutes that matter; the DRT contact and rule templates must exist beforehand.

## Best Practices

- **Hide the origin and pin ingress** — only accept connections from your CDN's published IP ranges (and rotate if exposed); never let clients reach the origin directly.
- **Defense in depth at the edge**: anycast absorption → WAF (OWASP + custom) → rate limiting (per IP/route/token) → aggressive caching → origin.
- **Rate-limit expensive endpoints specifically** (`POST /login`, search, report generation) rather than applying one blunt global limit.
- **Cache aggressively** so most requests never reach origin — caching is itself a DDoS mitigation that shrinks the attackable surface.
- **Buy cost protection** for volumetric risk (Shield Advanced, Cloudflare's absorb-at-edge model) so an attack doesn't become a surprise egress bill.
- **Rehearse**: maintain a runbook, keep the provider DRT contact handy, and run game days so the team executes from muscle memory.

## Quick Refs

Attack type → primary defense:

| Type | Example | Mitigation |
|---|---|---|
| Volumetric (Gbps–Tbps) | UDP/DNS/NTP amplification | anycast absorption, scrubbing |
| Protocol (high PPS) | SYN flood | SYN cookies, scrubbing |
| L7 (low rate) | HTTP flood, Slowloris | WAF, rate limit, JS challenge |

```bash
# SYN-cookie protection (should be 1)
sysctl net.ipv4.tcp_syncookies

# Live socket-state distribution during an attack
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn   # spike in SYN-RECV = SYN flood

# Top source IPs hitting a path (from access logs)
awk '$7=="/login"{print $1}' access.log | sort | uniq -c | sort -rn | head

# Confirm origin firewall only allows CDN ranges (Cloudflare list)
curl -s https://www.cloudflare.com/ips-v4
```

WAF/rate-limit pattern: limit `/login POST` to ~5/min/IP with a JS challenge; AWS WAF `RateBasedStatement` aggregates per IP (e.g., `Limit: 2000` → Block). Layer order to remember: **anycast → WAF → rate limit → cache → origin.**

## Interview Prep

**Mid**: "How does CDN absorb DDoS?"

**Senior**: "Origin hiding — why and how?"

**Staff**: "Active attack response runbook."

## Next Lecture

→ [L04 — Shell, Bash & Scripting for Automation](../../L04/README.md)
