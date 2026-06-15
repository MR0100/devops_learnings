# L23/C05/T03 — Cache Keys & Vary Headers

## Learning Objectives

- Control cache keys
- Use Vary

## Cache Key

What identifies a cached entry:
- Default: URL
- Plus: configured headers / cookies / query

## Why Care

Wrong key:
- Cache fragmentation (low hit)
- Wrong content served
- Cache misses for similar requests

## Default

Most CDNs:
```
key = method + URL
```

For `GET /api/users/1`:
- Cached once
- Served for matching requests

## Vary Header

Server tells cache to vary by:
```
Vary: Accept-Encoding
Vary: User-Agent
Vary: Authorization
```

For: serve different per header.

## Common Vary

### Accept-Encoding
gzip vs br. Same URL different encoding.

### Accept-Language
Different language versions.

### User-Agent
Mobile vs desktop. Risky (high cardinality).

## Risks

User-Agent variance:
- Thousands of agents
- Cache fragments

For: avoid where possible.

## Better: Cache Key Normalization

Normalize at edge:
```javascript
// CF Worker
const ua = req.headers.get('User-Agent');
const device = isMobile(ua) ? 'mobile' : 'desktop';
const cacheKey = `${url}?device=${device}`;
```

For: limit cardinality.

## Cloudflare Cache Rules

```javascript
// Or via dashboard
Custom Cache Key:
  - URL
  - Header: X-Tenant
```

For: tenant-specific.

## CloudFront

```json
{
  "QueryString": "true",
  "Cookies": {"Forward": "whitelist", "WhitelistedNames": ["session_id"]},
  "Headers": {"Quantity": 1, "Items": ["Authorization"]}
}
```

For: per-user cache (rare).

## Strip Query Params

Marketing params (`utm_source`, etc.):
- Don't vary cache by them
- Strip

CloudFront / Cloudflare: configure.

## Authentication

For per-user content:
- Don't cache OR
- Cache per user (large)

```
Cache-Control: private, no-store
```

Private content: don't cache at CDN.

## Vary: Authorization

Bad: cache per session token.
Fragments cache massively.

Better:
- Don't cache auth content
- Cache public; add auth at app

## Query String

Sort:
```
?a=1&b=2 same as ?b=2&a=1
```

For consistent key.

CDNs usually sort.

## Cookies

Cookies vary cache:
```
Cache-Control: private
```

Or:
- Strip cookies for cacheable
- Add back after

## Examples

### Static
```
GET /static/image.png
```

Single cache; high hit.

### API
```
GET /api/products?lang=en
```

Vary by `lang` query param.

### Personalized
```
GET /api/me
```

No cache (per user).

### Authenticated Public
```
GET /api/articles (public articles)
```

Cache; add user data on client.

## ETag

```
ETag: "abc123"
```

CDN can revalidate:
- If-None-Match → origin
- 304 if same
- Cheap

## Last-Modified

Similar.

## Cache-Control

```
Cache-Control: public, max-age=3600, s-maxage=86400
```

- max-age: browser
- s-maxage: CDN (shared)

For: different TTLs.

## stale-while-revalidate

```
Cache-Control: max-age=60, stale-while-revalidate=600
```

Serve stale up to 10 min while fetching fresh.

For: resilience.

## Best Practices

- Minimize Vary
- Normalize at edge
- Strip irrelevant query
- Don't Vary by User-Agent (too varied)

## Common Mistakes

- Vary: User-Agent (cache fragments)
- Auth content cached publicly (leak)
- Query string included verbatim (low hit)
- No Cache-Control (CDN decides)

## Quick Refs

```
Vary: Accept-Encoding
Cache-Control: public, max-age=3600, s-maxage=86400, stale-while-revalidate=300
ETag: "abc"

CDN config:
- Cache key fields
- Whitelist cookies
- Strip query
```

## Interview Prep

**Mid**: "Cache keys."

**Senior**: "Vary."

**Staff**: "CDN cache design."

## Next Topic

→ [T04 — Image Optimization at Edge](T04-Image-Edge.md)
