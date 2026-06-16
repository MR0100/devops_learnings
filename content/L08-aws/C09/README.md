# L08/C09 — Edge Services

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-CloudFront.md) | CloudFront (Distributions, Behaviors, Functions, Lambda@Edge) | 1.5 hr |
| [T02](T02-Route53.md) | Route 53 (Routing Policies) | 1 hr |
| [T03](T03-Global-Accelerator.md) | Global Accelerator | 0.5 hr |
| [T04](T04-WAF-Shield.md) | WAF & Shield | 1 hr |

## CloudFront

AWS CDN — 450+ PoPs globally.

### Distributions
- A distribution = a configuration with one or many origins
- Origin types: S3, ALB, NLB, Custom (any HTTPS endpoint)
- Multiple origins per distribution (route by path)
- Multiple Behaviors per origin (different cache policy per path)

### Cache Behaviors
- Path pattern (`/api/*`, `/static/*`)
- TTL, headers/cookies/query strings to forward
- Compress objects
- Origin protocol
- Viewer protocol (HTTPS only, redirect, allow)

### Cache Policies (Modern)
- AWS-managed policies: `CachingOptimized`, `CachingDisabled`, `CachingOptimizedForUncompressedObjects`
- Custom policies for fine control

### Functions

| | CloudFront Functions | Lambda@Edge |
|---|---|---|
| Runtime | JavaScript subset | Node.js / Python |
| Cold start | ~1ms | 200ms+ |
| Memory | 2MB | 128MB-3008MB |
| Execution | viewer-request, viewer-response | viewer + origin events |
| Use | URL rewrite, auth header check | More complex logic, calls to other AWS |

### Cache Invalidation
- `/path/*` invalidations
- Eventually consistent (~5 min globally)
- First 1000/month free, then $0.005 each
- **Prefer versioned URLs** (no invalidation needed)

### Signed URLs / Signed Cookies
- Restrict access (paid content, time-limited)
- Use CloudFront key groups

## Route 53

### Routing Policies

| Policy | Use |
|---|---|
| Simple | Single record, no logic |
| Weighted | Split traffic (10% / 90% canary) |
| Latency | Route to nearest healthy endpoint by RTT |
| Geolocation | Route by user's geographic region |
| Geoproximity | Bias by geo + custom rules (requires Traffic Flow) |
| Failover | Active-passive with health checks |
| Multi-value answer | Up to 8 healthy records returned |
| IP-based | Route by client IP CIDR |

### Health Checks
- HTTP, HTTPS, TCP
- Calculated: combine other health checks
- CloudWatch alarm: based on metric

### Hosted Zones
- Public: Internet DNS
- Private: VPC-only DNS

### Private DNS for VPCs
- Private hosted zone associated with VPCs
- Often used for internal service.company.com

## Global Accelerator

Anycast IPs + AWS backbone.

```
User
   ↓
Anycast IP (CloudFront-like edge)
   ↓
AWS backbone (low jitter)
   ↓
Endpoint Group(s) in regions
   ↓
ALB / NLB / EC2 / EIP
```

### Why Use
- Faster than public Internet (especially for international)
- Two anycast IPs for client failover
- Quick regional failover

### CloudFront vs Global Accelerator

| | CloudFront | Global Accelerator |
|---|---|---|
| Layer | L7 HTTP(S) | L4 TCP/UDP |
| Caching | Yes | No |
| Use | Web, static, dynamic HTTP | Any TCP/UDP service, gaming, real-time |
| Cost | per req + bytes | hourly + bytes |

## WAF (Web Application Firewall)

Rule-based filtering for HTTP(S).

### Resource Types Protected
- CloudFront
- ALB
- API Gateway
- AppSync
- Cognito User Pool (login)

### Rule Types
- **Managed Rule Groups**: AWS / 3rd-party (OWASP Top 10, bad IPs, bots)
- **Custom Rules**: rate-based, IP set, geo match, regex, SQLi, XSS detection
- **Bot Control**: detect/block bot traffic

### Pricing
- Per WebACL hour + per rule + per request

## Shield

DDoS protection.

### Shield Standard (Free, automatic)
- L3/L4 attacks
- Always-on
- Auto-mitigation

### Shield Advanced ($3000/mo + per-resource)
- L7 visibility
- 24/7 DRT (DDoS Response Team)
- Cost protection (refund for spikes due to DDoS)
- Health-based detection
- Advanced reporting

## Common Patterns

### Static Website
```
Route 53 → CloudFront → S3 (origin)
                     → Lambda@Edge (auth / rewrite if needed)
WAF in front of CloudFront
```

### Multi-region Failover
```
Route 53 failover policy
   primary: ALB in us-east-1
   secondary: ALB in us-west-2
Health check on primary endpoint
```

### Latency-routed Multi-region
```
Route 53 latency policy
   us-east-1 → CloudFront → ALB us-east-1
   eu-west-1 → CloudFront → ALB eu-west-1
   ap-south-1 → CloudFront → ALB ap-south-1
```

## Interview Themes

- "Design a global content delivery setup"
- "CloudFront vs Global Accelerator"
- "Route 53 routing policies — when each?"
- "Walk me through WAF + Shield protection"
- "How does Lambda@Edge differ from CloudFront Functions?"
