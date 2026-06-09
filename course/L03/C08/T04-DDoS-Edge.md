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

## Interview Prep

**Mid**: "How does CDN absorb DDoS?"

**Senior**: "Origin hiding — why and how?"

**Staff**: "Active attack response runbook."

## Next Lecture

→ [L04 — Shell, Bash & Scripting for Automation](../../L04/README.md)
