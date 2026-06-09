# L07/C07/T03 — DNS, CDN

## Learning Objectives

- Use cloud DNS
- Configure CDN

## DNS in Cloud

### Route53 (AWS)
- Hosted Zones (one per domain)
- Records: A, AAAA, CNAME, MX, TXT, ALIAS
- ALIAS: AWS-specific; points to AWS resource (ALB, CloudFront, S3 website) — no extra DNS hop

### Routing Policies
- Simple: one or many answers; random
- Weighted: 70%/30% split (canary)
- Latency: route to lowest-latency region
- Failover: primary + secondary with health checks
- Geo / Geoproximity: by user location
- Multi-Value: multiple healthy IPs

### Health Checks
HTTP / TCP probes; remove unhealthy from DNS rotation.

### Private Hosted Zones
DNS resolution within VPCs. Internal-only names.

## TTL Strategy

- Long TTL (1h+): fewer queries; slow change propagation
- Short TTL (60s): fast change; more queries

For failover: short TTL needed (~60s).

## DNS as Glue

```
user → DNS → IP → connect
```

DNS is global routing layer.

## Apex Records

Apex (zone root, e.g., `example.com`): can't be CNAME (DNS spec). Use ALIAS / ANAME.

## DNSSEC

Sign records; client verifies. Prevents cache poisoning. Few use it; complex.

## CDN

Content Delivery Network: cache at edge POPs close to users.

Benefits:
- Lower latency
- Offload origin
- DDoS protection
- TLS termination
- Geographic optimization
- Cache invalidation
- HTTP/2/3, edge compute

## CloudFront (AWS)

- 600+ POPs globally
- Caching with TTLs per resource
- Origins: S3, ALB, custom HTTP
- Cache key configurable
- Edge functions: CloudFront Functions (small), Lambda@Edge (full)

### Distribution
Configure:
- Origins (where uncached content fetched)
- Behaviors (path patterns + caching rules)
- TLS cert (ACM in us-east-1)
- Geo restriction
- Custom domain (CNAME)

### Cache Behaviors
- Path `/static/*`: cache 1 day; ignore query string
- Path `/api/*`: don't cache; forward all headers

### Invalidation
Push new content:
```bash
aws cloudfront create-invalidation --distribution-id E123 --paths '/static/*'
```

Slow (5-10 min); use sparingly.

Alternative: version asset URLs (`/static/v123/app.js`); never invalidate.

## Cloud CDN (GCP)

- Integrated with HTTPS Load Balancer
- Caches at Google's edge
- Negative caching, request collapsing

## Azure CDN / Front Door

- Front Door: global L7 + CDN
- CDN: per-region offerings

## Cloudflare

Third-party; very popular:
- Free tier (substantial)
- DDoS protection
- Workers (edge compute, V8 isolates; fast cold start)
- R2 (S3-compatible storage; no egress!)
- DNS

For new web apps: often Cloudflare on top of any cloud.

## Cache Headers

Origin sends:
```
Cache-Control: public, max-age=3600
Expires: ...
ETag: ...
Last-Modified: ...
```

CDN honors:
- Cache for max-age
- Validate via ETag / If-Modified-Since

Origin must send right headers; otherwise CDN ineffective.

## Cache-Control Examples

- Static asset with hash in name: `public, max-age=31536000, immutable`
- HTML: `no-cache` (revalidate every time; can cache if 304)
- API: `private, no-store`
- User-specific: `private, no-cache`

## Edge Compute

Run code at edge:
- CloudFront Functions: small JS; URL manipulation; auth
- Lambda@Edge: full Lambda at edge POPs
- Cloudflare Workers: V8 isolates; rich API
- Fastly Compute@Edge: Rust/WASM

Use:
- A/B testing
- Auth
- URL routing
- Header manipulation
- Geo redirection
- Personalization

## Cost

CDN: $0.085/GB (CloudFront US/EU); cheaper at volume.
Requests: $0.012/10000 HTTPS.

Often cheaper than direct origin egress.

Cloudflare: free tier large; paid plans.

## When NOT CDN

- Internal app (no public users)
- Always-personalized (no shareable cache)
- Tiny site (overhead > benefit)

Most public web should be CDN.

## Origin Shield

Inner cache tier in front of origin. Reduces origin requests (multiple edges → one shield → origin).

For high-cardinality content: helps.

## Streaming / Video

CDN for live + VOD streaming:
- HLS / DASH segments cached at edge
- Manifest dynamic (short TTL)
- Tokenized URLs for access control

## TLS

CDN terminates TLS; uses your cert (or theirs). Backend HTTPS optional but recommended.

For S3 origins: CloudFront uses its TLS; users see your domain.

## Common Mistakes

- Origin headers say `no-cache` (defeats CDN)
- Different cache key per user (every request unique; never caches)
- Cache HTML forever (stale content)
- No invalidation strategy
- TTL=0 (defeats CDN)
- CDN without backend rate limit (CDN cache miss = origin gets hit)

## Multi-CDN

Use 2+ CDNs; route by perf / failover. For massive sites:
- Akamai, Cloudflare, Fastly, CloudFront mixed
- Tools: NSone, Cedexis

## DNS for SaaS

Run web app on your domain via CNAME to provider:
```
www.mysite.com → mysite.example.heroku.com
```

Issues: apex (use ALIAS), TLS (provider must support custom).

## Geo DNS

Route by user location:
```
US user → US-EAST IP
EU user → EU-WEST IP
```

For latency or compliance. Route53 supports.

## Health-Checked DNS

```
Primary: 10.0.0.5 (health-checked)
Secondary: 10.0.1.5 (failover)
```

DNS returns primary if healthy, else secondary. ~60s failover.

## Latency Routing

```
Endpoint A (us-east-1)
Endpoint B (eu-west-1)
Endpoint C (ap-south-1)
```

Route53 returns nearest. Real RTT measurement; updates as network changes.

## Common Mistakes

- Long TTL on records you want to change quickly
- No health check (DNS returns dead IP)
- DNS without redundancy (NS records concentrated)

## Interview Prep

**Junior**: "What does CNAME do?"

**Mid**: "Failover DNS."

**Senior**: "CDN cache strategy."

**Staff**: "Global low-latency app design."

## Next Topic

→ [T04 — Cross-Region Networking](T04-Cross-Region.md)
