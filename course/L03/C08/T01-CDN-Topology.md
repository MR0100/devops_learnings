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

## Interview Prep

**Mid**: "How does a CDN work?"

**Senior**: "Cache key design — what to include?"

**Staff**: "Optimize cache hit ratio for a media site."

## Next Topic

→ [T02 — Anycast IP](T02-Anycast-IP.md)
