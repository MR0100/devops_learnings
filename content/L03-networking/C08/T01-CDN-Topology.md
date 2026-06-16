# L03/C08/T01 — CDN Topology (PoPs, Origin)

## Learning Objectives

- Understand CDN architecture
- Recognize PoP role
- Optimize cache hierarchy

## What a CDN Does

Caches content close to users. Reduces:
- Latency (fewer hops)
- Origin load (most requests don't reach origin)
- Bandwidth costs (cached responses)

## Topology

```
User in Tokyo
    ↓ ~5-20ms
PoP (Tokyo edge)
    ↓ on cache miss
Mid-tier / Shield (regional)
    ↓ on miss
Origin (e.g., us-east-1)
```

Three levels typical:
- Edge PoP (closest)
- Shield / Mid-tier (protects origin from miss storms)
- Origin (your servers)

## PoP (Point of Presence)

A datacenter location where CDN has cache servers + routing.
- Major CDNs have 100-500+ PoPs
- Each PoP serves its geographic region
- Anycast routes users to nearest

## Cache Hierarchy Flow

```
1. User → CDN edge (anycast)
2. Edge cache check:
   - Hit: serve from cache
   - Miss: proceed
3. Edge → mid-tier:
   - Hit: serve
   - Miss: proceed
4. Mid-tier → origin
5. Origin returns; cached at mid-tier and edge
6. User receives
```

## Cache Hit Ratio

Goal: 90%+ for static content.

```
hit ratio = hits / (hits + misses)
```

Higher = less origin load + faster user response.

## Cache Key

What identifies a cached object?

Default: URL + Host + Vary headers.

```
https://example.com/img.png
hits → cache key based on URL + Host
serves cached if present
```

Custom rules per CDN:
- Include/exclude query params
- Include/exclude cookies
- Include certain headers
- Per-region keys

## Cache-Control Headers

Origin tells CDN how long to cache:
```
Cache-Control: public, max-age=3600, s-maxage=86400
                         │              │
                         browser TTL    CDN TTL
```

- `max-age`: browser
- `s-maxage`: shared cache (CDN)
- `public`: cacheable anywhere
- `private`: browser only
- `no-cache`: must revalidate (cacheable but check)
- `no-store`: don't cache anywhere
- `immutable`: never check (for versioned URLs like `/style.abc123.css`)

## Stale-While-Revalidate

```
Cache-Control: max-age=60, stale-while-revalidate=3600
```

After 60s: serve stale; refresh async.
Best of both: freshness + availability.

## Cache Invalidation

For breaking changes:
- Purge specific URLs
- Purge by tag (newer CDNs)
- Purge by prefix
- Wildcard purge (entire site)

Costs (CloudFront): $0.005 per path after first 1000/month free.

**Prefer versioned URLs**: change URL → cache miss → new content. No purge needed.

## Edge Computing Tier

Modern CDNs run code at the edge:
- Cloudflare Workers (V8 isolates, ~5ms cold start)
- Fastly Compute (WebAssembly)
- AWS Lambda@Edge (Node/Python; slower)
- CloudFront Functions (V8 subset; ~1ms cold start)

Use cases:
- Auth at edge (no origin round trip)
- A/B testing
- Geo-routing
- URL rewrites
- Personalization
- Image optimization

## Origin Shield

Most CDNs offer "shield" tier:
- One specific PoP per region acts as origin shield
- All edge misses go through shield
- Shield aggregates requests → fewer hits to origin
- Improves overall hit ratio

## Real CDN Stats

Cloudflare (public):
- 300+ PoPs worldwide
- Average user within 50ms of a PoP
- 200+ Tbps total network capacity
- ~30M requests/sec at peak

## CDN Pricing

Major components:
- **Egress**: per-GB to user
- **Requests**: per-million
- **Edge compute**: per-invocation
- **Shield**: per-GB through

Typical:
- Cloudflare free tier handles many small sites
- $0.085/GB ish at AWS CloudFront
- High-traffic sites: $50-90/TB

## Choosing a CDN

| | CloudFront | Cloudflare | Fastly | Akamai |
|---|---|---|---|---|
| PoPs | 450+ | 300+ | 80+ | 4000+ |
| Edge compute | Lambda@Edge, CF Functions | Workers | Compute@Edge | EdgeWorkers |
| Free tier | Limited | Generous | None | Enterprise only |
| AWS integration | Best | Good | Good | Good |
| Programmability | Functions | Excellent | Excellent | Excellent |

Cloudflare often wins for ease + price. CloudFront for AWS-integrated.

## Production Patterns

### Static Assets (highest cache value)
```
/static/*  Cache: 1 year, immutable
URLs versioned per build (logo.abc123.png)
```

### HTML
```
/index.html  Cache: short (5 min) or none
Use stale-while-revalidate for resilience
```

### API
```
/api/products  Cache: 5 min public
/api/users/me  No cache (per-user)
/api/* POST    No cache (writes)
```

## Cache Buster

For when you need fresh:
```
/style.css?v=abc123       # changes hash → new cache entry
```

Or fingerprint in URL itself:
```
/style.abc123.css         # immutable
```

## Common Mistakes

- **Including cookies/auth in the cache key without meaning to** — a `Set-Cookie` or a varying header collapses the hit ratio (every request is "unique") or, worse, caches a per-user response and serves it to everyone.
- **Caching `/index.html` like a static asset** — long-TTL HTML means users see stale pages after a deploy. Cache HTML short (or `no-cache`) and version the assets it references.
- **Purging on every release** instead of versioning URLs — purges cost money, propagate slowly, and cause miss storms. Fingerprinted URLs (`app.abc123.js`) get a free cache miss with no purge.
- **Confusing `max-age` and `s-maxage`** — `max-age` is the browser TTL, `s-maxage` is the CDN/shared-cache TTL; setting only `max-age` makes the CDN inherit the browser value.
- **Caching error responses** — a cached `5xx`/`404` with a long TTL turns a blip into a sustained outage; set short/no TTL for error status codes.
- **No origin shield** — without it, every edge miss hits origin directly; a popular cold object causes a thundering herd.

## Best Practices

- **Version every static asset** (`/style.abc123.css`) and serve it `Cache-Control: public, max-age=31536000, immutable`; never purge, just change the filename.
- Use **`stale-while-revalidate`** on HTML/API so users get an instant (stale) response while the edge refreshes in the background — freshness *and* availability.
- **Normalize the cache key**: strip irrelevant query params and cookies, and use `Vary` deliberately (e.g., `Accept-Encoding`) — every dimension you add multiplies cache entries.
- Enable **origin shield / a mid-tier** so edge misses collapse to one origin fetch per object instead of one per PoP.
- Split policy by content type: **assets = long+immutable, HTML = short+SWR, per-user/API writes = no-store**.
- **Measure cache hit ratio** per route and treat a drop as an incident — it's the leading indicator of origin overload and rising egress bills.

## Quick Refs

`Cache-Control` directives:

| Directive | Meaning |
|---|---|
| `max-age=N` | browser TTL (seconds) |
| `s-maxage=N` | CDN/shared-cache TTL (overrides max-age at CDN) |
| `public` / `private` | cacheable by CDN / browser-only |
| `no-cache` | cache but revalidate before use |
| `no-store` | never cache anywhere |
| `immutable` | never revalidate (versioned URLs) |
| `stale-while-revalidate=N` | serve stale up to N s while refreshing |

```bash
# See cache headers + hit/miss
curl -sI https://example.com/app.abc123.js | grep -iE 'cache-control|age|x-cache|cf-cache-status'

# Force a miss to compare origin vs edge
curl -sI 'https://example.com/page?cb=$RANDOM' | grep -i x-cache

# Cache hit ratio
#   hit_ratio = hits / (hits + misses)   — target 90%+ for static
```

Hit-status headers to know: CloudFront `X-Cache: Hit from cloudfront`, Cloudflare `CF-Cache-Status: HIT/MISS/EXPIRED/REVALIDATED`, Fastly `X-Cache: HIT/MISS`.

## Interview Prep

**Mid**: "How does a CDN work?"

**Senior**: "Cache key design — what to include?"

**Staff**: "Optimize cache hit ratio for a media site."

## Next Topic

→ [T02 — Anycast IP](T02-Anycast-IP.md)
