# L23/C05 — CDN Strategy

## Topics

- **T01 CloudFront, Cloudflare, Fastly, Akamai** — Provider comparison
- **T02 Edge Computing** — CF Workers, Lambda@Edge
- **T03 Cache Keys & Vary Headers** — What gets cached
- **T04 Image Optimization at Edge** — Smart resizing

## CDN Provider Comparison

| | CloudFront | Cloudflare | Fastly | Akamai |
|---|---|---|---|---|
| PoPs | 450+ | 300+ | 80+ | 4000+ |
| Edge compute | Lambda@Edge, CF Functions | Workers (V8) | Compute (WASM) | EdgeWorkers |
| Free tier | Generous | Generous | None | None |
| Best for | AWS-native | All-purpose, dev-friendly | Programmable cache, large files | Enterprise / massive scale |
| Origin shielding | Yes | Yes (Tiered Cache) | Yes (Origin Shield) | Yes (NetStorage) |

## CloudFront

Tight AWS integration. ALB/S3/Lambda@Edge origins.

```yaml
# Distribution config
Origins:
  - S3 (static)
  - ALB (dynamic)
Behaviors:
  - /static/* → S3 origin, cache 1 year
  - /api/* → ALB, no cache
  - default → ALB, cache 1 hour
Functions:
  - Viewer-Request: auth header check (CF Functions)
  - Origin-Request: URL rewrite (Lambda@Edge)
```

Cache invalidation: $0.005 per path beyond 1000/month free.

## Cloudflare

The most widely-used CDN. Strong free tier. Massive R&D.

### Workers
JavaScript V8 isolates at edge. Sub-millisecond cold start. KV storage, Durable Objects.

```javascript
export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/api/version') {
      return new Response('v1.0', { headers: { 'cache-control': 'max-age=60' } });
    }
    return fetch(request);
  }
};
```

### Cloudflare R2
S3-compatible storage with NO egress fees.

### DDoS Protection
Free tier includes massive DDoS absorption (200+ Tbps capacity).

## Fastly

Engineered for programmable cache. Used by Reddit, GitHub, New York Times.

### Compute@Edge (WebAssembly)
Run any language compiled to WASM at edge.

### Instant Purge
Sub-second cache purge globally (rare among CDNs).

### Use
Large file delivery; programmable cache logic; reliable purge.

## Akamai

Legacy giant; biggest network. Premium price; enterprise sales-driven. Increasingly losing ground to Cloudflare/CloudFront in modern stacks.

## Cache Keys

Determines whether a request is a hit or miss.

```
Default key = URL path + query string + Host
```

### Tunable
- Include/exclude query params
- Include/exclude headers (Vary)
- Include/exclude cookies
- Custom keys (per CDN)

### Vary Header
Tells CDN "cache separately based on these headers":
```
Vary: Accept-Encoding
Vary: User-Agent       # bad — explodes cache (millions of UAs)
```

Use Vary sparingly. Each distinct value = separate cache entry.

## Cache-Control

```
Cache-Control: public, max-age=3600, s-maxage=86400, immutable
                │       │              │              │
                │       │              │              └ never revalidate
                │       │              └ CDN TTL
                │       └ browser TTL
                └ cacheable
```

### Stale-While-Revalidate
```
Cache-Control: max-age=60, stale-while-revalidate=600
```
Serve cached for 60s. After expiry, serve stale up to 10 min while refreshing async.

## What to Cache

| Path | TTL | Why |
|---|---|---|
| `/static/foo.abc123.js` | 1 year | Versioned URL; safe to cache forever |
| `/images/*` | 30 days | Rarely changes |
| `/api/products` (catalog) | 5 min | Mostly stable |
| `/api/users/me` | private, 60s | Per-user; short |
| `/login` POST | no-store | Don't cache |
| HTML pages | varies | 1 min to immutable based on dynamism |

## Edge Computing

### Use Cases
- Auth at edge (JWT validation before origin)
- A/B testing (route to variants)
- Geo-routing (different origin per country)
- URL rewriting / redirects
- Cookie manipulation
- HTML injection (analytics tag)
- Light API at edge (sub-10ms latency worldwide)

### Cold Start
- CF Workers: ~5ms
- Lambda@Edge: 200ms+
- CloudFront Functions: ~1ms (limited capability)

## Image Optimization at Edge

Resize / format-convert / compress on demand:
- Cloudflare Image Resizing
- Fastly Image Optimizer
- AWS CloudFront with Lambda@Edge

```
Original: /images/hero.jpg (5 MB)
Mobile request: /images/hero.jpg?w=400&format=webp
Cache returns: 50 KB WebP
```

Save bandwidth + improve performance.

## Origin Shield / Tiered Cache

A "shield" layer between edge and origin:
- Edge → Shield → Origin
- Reduces origin load (fewer cache misses reach it)
- Better cache hit ratio overall

## Logs & Analytics

CDN logs to S3/GCS/etc.:
- CloudFront → S3 access logs (delayed) or Real-time Logs (Kinesis)
- Cloudflare → Logpush
- Fastly → real-time tail

Analyze for: top URLs, geographic distribution, error rates, cache hit ratio.

## Cost

Major components:
- Egress (bytes served): ~$0.05-0.085/GB
- Requests: per million
- Edge compute: per invocation
- Shield/Origin Shield: extra layer cost

Optimization:
- High cache hit ratio = low egress from origin
- Compress at edge (Brotli, gzip)
- Image optimization at edge
- Tier old objects out of CDN

## Interview Themes

- "Design CDN strategy for X"
- "Cache key + Vary headers"
- "Cloudflare Workers vs Lambda@Edge"
- "Cache-Control directives"
- "Origin shield — why?"
