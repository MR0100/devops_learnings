# L23/C05/T01 — CDN: CloudFront, Cloudflare, Fastly, Akamai

## Learning Objectives

- Choose CDN
- Configure basics

## CDN

Content Delivery Network:
- Edge caching globally
- Reduce origin load
- Reduce latency

## Why

- Static content: cache once; serve many
- API: cache eligible responses
- DDoS absorb
- TLS termination at edge

## Major CDNs

### Cloudflare
- Anycast network
- 300+ edge locations
- Free tier
- Workers (edge compute)

### CloudFront (AWS)
- AWS-integrated
- Lambda@Edge
- 400+ POPs
- Pay-per-use

### Fastly
- Real-time purge (instant)
- VCL config
- Compute@Edge (Wasm)

### Akamai
- Largest network
- Enterprise
- Expensive
- Highly featured

### Bunny.net
- Cheaper alternative
- Growing

### KeyCDN
- Budget

## Comparison

| | Cloudflare | CloudFront | Fastly | Akamai |
|---|---|---|---|---|
| POPs | 300+ | 400+ | 90+ | 4000+ |
| Free tier | yes | limited | no | no |
| Edge compute | Workers | Lambda@Edge | Compute@Edge | EdgeWorkers |
| Real-time purge | yes | minutes | yes | yes |
| Price | $ | $ | $$ | $$$ |
| DDoS | strong | Shield | strong | strong |

## Choose

### Cloudflare
Most use cases. Free tier great.

### CloudFront
AWS-heavy. Integrated.

### Fastly
Need instant purge. Edge compute.

### Akamai
Massive enterprise.

## Configure

### Cloudflare
DNS → Cloudflare → orange cloud.
Auto-proxies.

### CloudFront
Distribution → origin → settings.

```bash
aws cloudfront create-distribution --distribution-config ...
```

### Fastly
Service → origin → VCL.

## Cache Rules

```
Cache-Control: public, max-age=3600
Cache-Control: private, no-cache
Cache-Control: public, max-age=60, stale-while-revalidate=300
```

CDN respects (configurable).

## Cache Key

Default: URL.

Customize:
- Vary by header
- Vary by cookie
- Strip query strings

## Cache Hit

```
HTTP request → POP (edge) → cache hit? → serve
                              ↓ miss
                              → origin → cache → serve
```

## Hit Rate

Target: 80%+.

Low hit rate:
- Diverse URLs
- Personalized
- Short TTL

## Purge

```bash
# CloudFront
aws cloudfront create-invalidation --distribution-id X --paths "/path/*"

# Cloudflare
curl -X POST .../purge_cache -d '{"files":["url"]}'
```

For: explicit refresh.

## Costs

- CloudFront: $0.085/GB (first 10 TB)
- Cloudflare: free; paid for advanced
- Fastly: $0.12/GB+
- Bunny.net: $0.005/GB+

For high bandwidth: cost varies dramatically.

## Edge Compute

(See T02.)

For: dynamic processing at edge.

## Best Practices

- Cache static aggressive
- Stale-while-revalidate for resilience
- Cache key minimal
- Monitor hit rate
- Purge sparingly

## Common Mistakes

- Personalized URLs (low hit)
- Cache-Control private wrongly
- Vary by cookie (cache fragmentation)
- No purge plan

## Quick Refs

```
Headers:
  Cache-Control: max-age=N
  ETag, Last-Modified
  Vary: Accept-Encoding

Purge:
  CloudFront create-invalidation
  Cloudflare purge_cache
  Fastly purge URL
```

## Interview Prep

**Mid**: "CDN basics."

**Senior**: "CDN choice."

**Staff**: "Edge architecture."

## Next Topic

→ [T02 — Edge Computing](T02-Edge-Computing.md)
