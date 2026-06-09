# L08/C09/T01 — CloudFront (Distributions, Behaviors, Functions, Lambda@Edge)

## Learning Objectives

- Configure CloudFront effectively
- Use edge compute

## CloudFront

AWS CDN. 600+ edge locations globally.

For:
- Static asset delivery
- Dynamic content caching
- Video streaming
- WAF / DDoS protection
- Edge compute

## Distribution

Top-level config:
- Origins
- Behaviors (path → cache rules)
- TLS cert
- Custom domain
- Geo restriction
- WAF Web ACL

## Origins

Where uncached content fetched:
- S3 (static)
- ALB (dynamic apps)
- API Gateway
- EC2 (direct)
- Custom HTTP

Multiple origins per distribution.

## Behaviors

Path patterns → caching rules:
```
/static/*    → cache 1 day; query string ignored
/api/*       → no cache; forward all headers
default      → cache 1 hour
```

## Cache Key

What CloudFront uses to identify cacheable variations:
- URL
- Selected headers (Accept-Language, etc.)
- Selected query strings
- Cookies (rare)

Limit cache key dimensions: more variations = lower hit rate.

## TTL

Set Cache-Control on origin:
```
Cache-Control: max-age=3600
```

CloudFront honors. Or override per behavior.

For immutable assets (hashed filenames):
```
Cache-Control: public, max-age=31536000, immutable
```

## Invalidation

Push new content:
```bash
aws cloudfront create-invalidation --distribution-id ... --paths '/static/*'
```

Slow (5-10 min); $0.005 per path after first 1000/mo.

Alternative: version asset URLs (`/static/v123/app.js`); never invalidate.

## Edge Functions

### CloudFront Functions
- JavaScript (V8 isolates)
- Lightweight (~1 ms)
- Free for many invocations
- Used at viewer-request / viewer-response

```javascript
function handler(event) {
    var request = event.request;
    var headers = request.headers;
    
    // Redirect
    if (request.uri === '/old') {
        return {
            statusCode: 301,
            statusDescription: 'Moved',
            headers: {location: {value: '/new'}}
        };
    }
    
    return request;
}
```

For: header manipulation, redirects, A/B routing, URL rewrites.

### Lambda@Edge
- Lambda runtime at edge
- Heavier (~5 ms)
- Standard Lambda
- Used at viewer/origin request/response

For: auth, personalization, edge logic.

## Use Cases

### Static Site
S3 + CloudFront:
- Origin: S3 bucket (private; OAC)
- Cache HTML for 5 min
- Cache assets long (hashed names)

### Single-Page App
- HTML cached short
- Assets cached long
- Custom error page → /index.html (SPA routing)

### API Caching
- API Gateway origin
- Cache GET responses
- TTL based on Cache-Control

### Video
- Origin: S3 (HLS segments)
- Long cache for segments
- Short cache for manifest

## TLS

ACM cert for custom domain. Must be in us-east-1 (CloudFront global).

```bash
aws acm request-certificate --domain-name example.com --validation-method DNS --region us-east-1
```

Then CloudFront alternate domain name + cert ARN.

## OAC (Origin Access Control)

For S3 origins: bucket private; only CloudFront can read:
```bash
aws cloudfront create-origin-access-control --origin-access-control-config Name=myOAC,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3
```

Plus S3 bucket policy allows OAC. Block all public access.

## Origin Shield

Mid-tier cache. Reduces origin requests:
```
Edge POPs → Origin Shield (one location) → S3 / ALB
```

For high-cardinality content / high-traffic.

Cost: extra. Worth at scale.

## Pricing

Egress:
- Data transfer out: $0.085/GB (US/EU first 10 TB)
- $0.040/GB (50+ TB)
- Asia: higher

HTTPS requests:
- $0.012/10000

Invalidation:
- First 1000/mo free
- $0.005 each after

CloudFront Functions: $0.10/M invocations.

Lambda@Edge: $0.60/M + Lambda compute.

## Compared to S3 Egress

S3 egress: $0.09/GB.
CloudFront: $0.085/GB (and cheaper at volume).

For high download: CloudFront cheaper.

## DDoS / WAF

CloudFront integrates:
- AWS Shield Standard (free; basic DDoS)
- AWS WAF (custom rules)
- AWS Shield Advanced ($$$; comprehensive)

## Geo Restriction

Allow/Deny specific countries:
```bash
aws cloudfront update-distribution ... --restrictions 'GeoRestriction={RestrictionType=blacklist,Locations=[CN,IR]}'
```

For: compliance, content licensing.

## Field-Level Encryption

Encrypt specific request fields (e.g., credit card) end-to-end through CloudFront to origin. Only origin's keys decrypt.

For: PCI compliance, sensitive data.

## Real-Time Logs

CloudFront access logs to Kinesis Data Streams; near real-time analytics.

vs Standard logs (delayed minutes to hours; S3-based).

## Origin Failover

Define origin groups; failover on errors:
```
Primary: ALB in us-east-1
Failover: ALB in us-west-2
```

CloudFront tries primary; on failure (5xx), tries failover.

## Signed URLs / Cookies

For private content:
- Signed URL per object
- Signed cookie for many objects

Pre-shared with authorized client.

For: paid video, private downloads.

## Cache Behaviors Order

CloudFront evaluates behaviors in order; first match wins.

```
1. /api/*       → no cache
2. /admin/*     → no cache; restrict
3. /static/*    → long cache
4. default      → 1 hour
```

Specific first; default last.

## Common Mistakes

- Cache HTML forever (stale content)
- No CloudFront for high download
- Behavior order wrong
- All requests forward all headers (defeats cache)
- No origin shield at scale
- Missing invalidation strategy

## Best Practices

- Hashed asset filenames (no invalidation needed)
- Long cache for assets; short for HTML
- OAC for S3
- HTTPS only
- WAF Web ACL
- Real-time logs for production
- Monitor cache hit ratio

## Cache Hit Ratio

Target: >80%. Higher = less origin load + cost.

CloudWatch metric: `CacheHitRate`.

If low:
- Audit Cache-Control headers
- Reduce cache key dimensions
- Check ignoring query strings appropriately
- Consider Origin Shield

## Edge Location

CloudFront picks nearest to user.

Latency:
- US user: ~10-20 ms to CloudFront
- Origin in different region: extra hop

For best: origin close to most users.

## Multi-Origin

```
/api/* → ALB-region-1
/static/* → S3
/legacy/* → ALB-region-2
```

CloudFront routes per path.

## Logging

Standard logs: S3 (delayed).
Real-time: Kinesis (live).

Fields: request, response, cache hit/miss, edge POP, etc.

Useful for analysis (Athena over S3 logs).

## Continuous Deployment

CloudFront supports staging distribution:
- Test changes without affecting production
- Promote on validation

## VPC Origins (Newer)

Connect CloudFront directly to private ALB / EC2 (no public IP). Improves security.

## Monitoring

CloudWatch:
- Requests
- BytesDownloaded
- 4XXErrors / 5XXErrors
- TotalErrorRate
- CacheHitRate

Real-time dashboard for high-traffic.

## Cost Optimization

- Cache more (higher hit rate)
- Origin Shield at scale
- Price Class (only North America + Europe = cheaper if users there)
- Compress (gzip, brotli at edge)
- Reduce object size

## Compression

CloudFront auto-compresses if origin returns supported types and `Content-Encoding` configured.

Saves 60-80% bytes.

## Quick Refs

```bash
# Distribution
aws cloudfront create-distribution --distribution-config file://dist.json

# Invalidation
aws cloudfront create-invalidation --distribution-id ... --paths '/*'

# Update
aws cloudfront get-distribution-config --id ...
aws cloudfront update-distribution --id ... --distribution-config ... --if-match ETAG
```

## Interview Prep

**Mid**: "When use CloudFront."

**Senior**: "Cache strategy for SPA."

**Staff**: "CDN architecture for global app."

## Next Topic

→ [T02 — Route 53 (Routing Policies)](T02-Route53.md)
