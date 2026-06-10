# L24/C07/T02 — L7 Attacks

## Learning Objectives

- Recognize L7 attacks
- Defend application

## L7 (Application)

Slow, complex requests:
- Exhaust app resources
- Not network bandwidth
- Harder to detect

Examples:
- HTTP flood
- Slowloris
- POST flood
- Cache busting

## HTTP Flood

Many GET requests:
- Look legit
- Saturate app
- Hard to distinguish from real users

Defense:
- Rate limit per IP
- Bot detection
- CAPTCHA

## Slowloris

Open many connections:
- Send slow headers
- Never complete
- Exhaust connection pool

Defense:
- Connection timeout
- Concurrent connection limit per IP
- Nginx event-driven (resilient)

## POST Flood

Large POSTs:
- Big bodies
- Server processes
- Memory exhausted

Defense:
- Body size limit
- Rate limit
- POST throttling

## Cache Busting

Random query strings:
```
/api?random=1
/api?random=2
...
```

Cache miss every time; origin hit.

Defense:
- Strip random params
- Hot path caching
- Rate limit per IP

## Bot Identification

- User-Agent
- IP reputation
- Behavior (mouse, scroll)
- TLS fingerprint (JA3)

## Defenses

### WAF
Application firewall:
- AWS WAF
- Cloudflare WAF
- Imperva
- F5

Rules:
- OWASP Core Rule Set
- Custom rules
- Rate limit

### Bot Management
- Cloudflare Bot Management
- DataDome
- HUMAN (PerimeterX)

Classify; challenge bots.

### CAPTCHA
- hCaptcha
- Cloudflare Turnstile
- Google reCAPTCHA

For: human verification.

### Rate Limit

Per IP / per user / per session.

```nginx
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
limit_req zone=mylimit burst=20;
```

### Connection Limit

```nginx
limit_conn_zone $binary_remote_addr zone=perip:10m;
limit_conn perip 10;
```

### Adaptive

Cloudflare Under Attack Mode:
- Challenge all
- Reduce by signals
- Auto

## L7 Detection

- Anomaly in QPS / endpoint
- Suspicious User-Agents
- Same params repeatedly
- Geographic anomaly

## Real Examples

### GitHub 2018
1.35 Tbps; Memcached.

### AWS 2020
2.3 Tbps; CLDAP reflection.

### Cloudflare 2023
71 Mrps L7 (HTTPS).

For: continuous.

## Best Practices

- WAF + Bot mgmt
- Rate limits
- CDN + DDoS protection
- Monitor anomalies
- Practice (game day)

## Common Mistakes

- No WAF
- Trust user-agent
- No rate limit
- Reactive only

## Quick Refs

```
L7 attacks: app-level
Slowloris: slow connections
HTTP flood: many GETs
Cache bust: random params

Defense:
- WAF
- Bot management
- Rate limit
- CDN
```

## Interview Prep

**Mid**: "L7 DDoS."

**Senior**: "Bot mitigation."

**Staff**: "Multi-layer defense."

## Next Topic

→ [T03 — AWS Shield, Cloudflare DDoS Protection](T03-DDoS-Tools.md)
