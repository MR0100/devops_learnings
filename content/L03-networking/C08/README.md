# L03/C08 — Edge & CDN Networking

## Chapter Overview

The internet edge — CDNs, anycast, edge computing — is where modern systems optimize for users worldwide. Every senior engineer should be able to design an edge strategy.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-CDN-Topology.md) | CDN Topology (PoPs, Origin) | 1 hr |
| [T02](T02-Anycast-IP.md) | Anycast IP | 0.5 hr |
| [T03](T03-Edge-Computing.md) | Edge Computing | 1 hr |
| [T04](T04-DDoS-Edge.md) | DDoS Protection at the Edge | 1 hr |

## CDN Topology

```
User in Tokyo                  PoP (edge)                  Origin (region)
     │                            │                              │
     │   GET /static/logo.png     │                              │
     │ ─────────────────────────► │                              │
     │   (cache miss)             │   GET /static/logo.png       │
     │                            │ ───────────────────────────► │
     │                            │   <bytes>                    │
     │                            │ ◄─────────────────────────── │
     │                            │   (cache stored)             │
     │   <bytes>                  │                              │
     │ ◄───────────────────────── │                              │
     │                            │                              │
     │   GET /static/logo.png     │                              │
     │ ─────────────────────────► │ (cache HIT, no origin call)  │
     │   <bytes>                  │                              │
     │ ◄───────────────────────── │                              │
```

PoP = Point of Presence (edge location). Major CDNs have 100-300+ PoPs worldwide.

## CDN Layers

- **Edge cache**: closest to user, fastest, smallest
- **Mid-tier (shield/origin shield)**: protects origin from edge stampede
- **Origin**: your servers/cloud

## Cache Key

The key identifying a cached object:
- URL path + query string (usually)
- Host header
- Selected headers via `Vary` (Accept-Encoding always; others sparingly)
- Cookies (usually NOT — they explode the key space)

### Cache-Control Directives (Origin-side)

```
Cache-Control: public, max-age=3600, s-maxage=86400, immutable
                │       │              │              │
                │       │              │              └ Don't revalidate
                │       │              └ Shared cache TTL (CDN)
                │       └ Browser TTL
                └ Cacheable by anyone
```

Useful patterns:
- `max-age=0, s-maxage=86400` — never cache in browser, cache in CDN
- `private, max-age=300` — browser cache only (personalized)
- `no-store` — don't cache anywhere
- `stale-while-revalidate=86400` — serve stale up to 1 day while refreshing

## Anycast Deeper

Same IP advertised from many PoPs via BGP:
```
                  Internet routing tables
                  See: 1.2.3.4 via AS 13335 (Cloudflare)
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
    [PoP Tokyo]    [PoP Frankfurt]    [PoP São Paulo]
   1.2.3.4 here    1.2.3.4 here       1.2.3.4 here
```

Internet's shortest-AS-path picks the "nearest" PoP for each client.

Use cases:
- DNS (root nameservers, 1.1.1.1)
- DDoS absorption (attack spreads across PoPs)
- HTTP edge (Cloudflare, Fastly)
- TCP / Global LB (AWS Global Accelerator)

## Edge Computing

Code runs at PoP, not origin. Reduces latency for compute-light logic.

| Platform | Runtime | Cold Start | Use |
|---|---|---|---|
| Cloudflare Workers | V8 isolates (JS/WASM) | ~5ms | Auth, A/B, redirects, edge KV |
| Fastly Compute | WebAssembly | ~5ms | Same |
| AWS Lambda@Edge | Node/Python | 200ms+ | CloudFront integration |
| AWS CloudFront Functions | JS subset | ~1ms | Lightweight URL rewrites, auth headers |
| Vercel Edge | V8 isolates | ~5ms | Next.js edge routes |

### Typical Edge Use Cases
- Auth at edge (validate JWT before hitting origin)
- A/B test routing
- Geo-based redirects
- Edge KV reads (Cloudflare KV, Durable Objects)
- API rate limiting
- Image resizing
- HTML personalization

## Cache Strategies

### Static Assets
Long TTL (1 year), versioned URLs:
```
/assets/logo.abc123.png    Cache-Control: max-age=31536000, immutable
```
On deploy, new hash = new URL = no invalidation needed.

### HTML
Short or no TTL — risk of serving stale UI is high.

### API Responses
Per-endpoint based on read patterns:
- `/users/me` → `private`, short max-age
- `/products/list` → public, short max-age, vary on Accept-Encoding
- Use `stale-while-revalidate` for resilience

### Invalidation
- Soft purge (mark stale, refetch on next request)
- Hard purge (remove from edge)
- Both slower at PoP scale than cache fills

## DDoS Protection at the Edge

```
Volumetric (Gbps/Tbps) → absorbed by CDN's combined PoP capacity
                          (Cloudflare claims 200+ Tbps)
Protocol (SYN flood, UDP) → scrubbed at edge
L7 (slow HTTP, app-level) → WAF rules, rate limiting, JS challenges
```

Modern providers (Cloudflare, AWS Shield Advanced, Akamai) provide all three layers automatically.

## Performance Numbers

| Scenario | Latency to Origin | Latency via CDN |
|---|---|---|
| User in US-east, origin US-east | 30ms | 5-15ms (PoP near user) |
| User in EU, origin US-east | 110ms | 10-20ms (cache hit) |
| User in Asia, origin US-east | 170ms | 10-20ms |
| Cache miss anywhere | Adds round-trip to origin | 1.5-2× origin RTT |

A CDN converts a 170ms cross-continental request into a 15ms PoP request — provided cache hit ratio is high.

## Choosing a CDN

| | Cloudflare | Fastly | AWS CloudFront | Akamai |
|---|---|---|---|---|
| PoPs | 300+ | 80+ | 450+ | 4000+ |
| Edge compute | Workers (V8) | Compute (WASM) | Lambda@Edge, CF Functions | EdgeWorkers |
| Free tier | Generous | None | Modest | None |
| Best for | All-purpose, ease | Programmable cache | AWS-native | Largest enterprise |

## Interview Themes

- "Design a CDN cache strategy"
- "How does Anycast work?"
- "Compare edge computing platforms"
- "DDoS — Internet edge defense"
- "Why is HTML caching tricky?"
- "Walk me through what happens on cache miss"
