# L26/C05/T03 — Data Egress

## Learning Objectives

- Reduce egress
- CDN strategy

## Egress

Data out of cloud:
- AWS: $0.05-0.09/GB
- GCP: $0.08-0.12/GB
- Azure: $0.05-0.087/GB

## Where

- Internet (browser users)
- Cross-region
- Cross-cloud

## CDN Discount

CloudFront egress:
- $0.085/GB (first 10 TB)
- Less for committed

AWS waives S3 → CloudFront transfer.

For: use CDN saves bandwidth bill.

## CDN Pricing

| | AWS CF | Cloudflare | Fastly |
|---|---|---|---|
| Egress | $0.085/GB | included with paid plans | $0.12+/GB |
| Commit | reductions | - | per-region |

For Cloudflare: bandwidth essentially free at paid tier.

## Optimize

- Compress (gzip, brotli)
- Cache aggressive
- Modern image formats (WebP, AVIF)
- Minify
- Lazy load

For: less bytes out.

## Compression Savings

gzip on:
- HTML/JS/CSS: 70-90% smaller
- JSON API: 70-80%

For: massive.

## Image Optimization

WebP: 25-35% smaller than JPEG.
AVIF: 30-50% smaller.

Serve appropriate size:
- Don't 1080p on mobile.

For: bandwidth saved.

## Cache TTL

Longer TTL:
- Less origin egress
- More CDN hit

For: aggressive caching.

## Cross-Region

Egress between regions:
- $0.02-0.04/GB
- Add up for replication

## Cross-Cloud

(See L09/C03/T04.)

Expensive; minimize.

## Identify Top

```sql
SELECT line_item_resource_id, SUM(line_item_unblended_cost)
FROM cur
WHERE line_item_usage_type LIKE '%DataTransfer-Out-Bytes%'
GROUP BY line_item_resource_id
ORDER BY 2 DESC
LIMIT 10
```

Top egress sources.

## Best Practices

- CDN in front of public
- Compression
- Image optimization
- Aggressive caching
- Monitor top
- Negotiate commits

## Common Mistakes

- No CDN (direct origin egress)
- No compression
- Large images uncompressed
- Egress alerts off

## Quick Refs

```
Egress costs:
- Internet: $0.05-0.12/GB
- Cross-region: $0.02-0.04/GB
- Cross-cloud: $0.05+/GB

Mitigations:
- CDN
- Compress
- Optimize images
- Cache TTL
- Commits
```

## Interview Prep

**Mid**: "Egress costs."

**Senior**: "Reduce egress."

**Staff**: "Bandwidth strategy."

## Next Topic

→ Move to [L26/C06 — Kubernetes Cost Management](../C06/README.md)
