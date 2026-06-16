# L03/C03/T05 — DNS as a Load Balancer (Route53, GeoDNS)

## Learning Objectives

- Understand DNS-based traffic routing
- Compare routing policies
- Recognize DNS LB limits

## Why Use DNS for LB

- Global reach without anycast infrastructure
- No LB hop in the data path
- Cheap at scale
- Works at L3 (any protocol; not just HTTP)

Limits:
- TTL lies (caching by clients/middleboxes)
- Limited control over individual sessions
- Cannot rebalance live connections

## Routing Policies (Route 53)

### Simple
Single record, no logic. One IP returned (or multi-value but no health check).

### Weighted
Split traffic by weight.
```
example.com → A 1.2.3.4 weight 90
example.com → A 5.6.7.8 weight 10
```
Use: canary deploys.

### Latency-Based
Route 53 measures network latency from many vantage points; returns endpoint with lowest latency to querying resolver.

Use: multi-region apps, optimize user latency.

### Geolocation
Route based on user's country/continent.
- Different content per region (compliance, language)
- Different infrastructure per region

### Geoproximity
Geo + custom bias (e.g., "push more traffic to LA even if Tokyo is closer"). Requires Route 53 Traffic Flow.

### Failover
Active/passive. Primary served while healthy; falls back to secondary.

### Multi-Value Answer
Returns up to 8 random healthy records (better than simple round-robin).

### IP-Based
Route based on client IP CIDR. Used for: large client networks that want specific routing.

## Health Checks

Route 53 (and other DNS LBs) actively probe endpoints:
- HTTP / HTTPS
- TCP
- Calculated (combine other health checks)
- CloudWatch alarm-based

Failed health check → record excluded from responses.

## Example: Active/Passive Failover

```
us-east-1 ALB (PRIMARY) ← health check on /healthz
us-west-2 ALB (SECONDARY)

example.com:
  type=A FAILOVER PRIMARY  → us-east-1 ALB
  type=A FAILOVER SECONDARY → us-west-2 ALB
```

Health check fails → DNS returns SECONDARY.

## Example: Weighted Canary

```
example.com:
  type=A weight=95 → v1 backend
  type=A weight=5  → v2 backend (canary)
```

Slowly increase v2 weight. Statistical sample.

## Common Mistakes

### Sticky Cache
A client cached the OLD response. Continues using old IP for TTL duration (or longer; see T03).

Implication: weighted shifts take time to manifest. Not real-time.

### Per-Session vs Per-Lookup
Two queries from same resolver may get different answers (if Route 53 returns random of weighted set). But cache flattens this.

### No Session State
DNS doesn't know "this user is in flight; route to same place." Use anycast or sticky LB for that.

## Geo-DNS Use Cases

- Compliance (EU data stays in EU)
- Performance (route to nearest region)
- Different infra per region (cellular vs Wi-Fi)
- Localized content (gambling allowed in some countries)

## Alternatives

| | Pros | Cons |
|---|---|---|
| DNS-based (Route 53) | Simple, cheap, global | TTL lies, no real-time |
| Anycast (Cloudflare, AWS GA) | Fast failover, real-time | More expensive |
| Application-level (client-side LB) | Most control | Client logic |

## Provider Examples

- **AWS Route 53**: most comprehensive DNS LB
- **Cloudflare**: load balancing + DDoS + CDN integrated
- **NS1**: focused on advanced DNS LB
- **Akamai DNS**: enterprise
- **GCP Cloud DNS + Cloud Load Balancing**: simpler model

## Sample Route 53 Config (Terraform)

```hcl
resource "aws_route53_record" "api_primary" {
  zone_id = aws_route53_zone.main.id
  name    = "api.example.com"
  type    = "A"
  set_identifier = "primary"
  
  failover_routing_policy {
    type = "PRIMARY"
  }
  
  alias {
    name    = aws_lb.east.dns_name
    zone_id = aws_lb.east.zone_id
    evaluate_target_health = true
  }
  
  health_check_id = aws_route53_health_check.east.id
}

resource "aws_route53_record" "api_secondary" {
  # Similar; with SECONDARY policy + west ALB
}
```

## Monitoring

- Route 53 query metrics
- Resolver behavior (some clients ignore TTL)
- Per-region traffic split (CloudWatch / synthetic checks)

## Best Practices

- **Treat DNS LB as coarse, eventually-consistent routing** — great for region selection and failover, wrong for real-time rebalancing or sticky sessions. Pair it with anycast or an in-path LB when you need fast, session-aware control.
- **Keep TTLs short on failover/weighted records** (30-60s) so shifts manifest reasonably fast, accepting the higher query volume and cost.
- **Always attach health checks** to failover, weighted, and multi-value records so unhealthy endpoints are pulled from responses automatically (`evaluate_target_health = true` on alias records).
- **Use latency- or geo-based routing for global apps**, and geoproximity with bias when you must deliberately steer traffic away from the nearest region (capacity, compliance).
- **Prefer Multi-Value Answer over plain round-robin** when you want client-side spread *with* health checking (returns up to 8 healthy records).
- **Manage records as code** (Terraform/CloudFormation) with `set_identifier`, routing policy, and health-check IDs version-controlled — DNS LB config is easy to drift.

## Quick Refs

Route 53 routing policies:

| Policy | Routes by | Typical use |
|---|---|---|
| Simple | single record | static endpoint |
| Weighted | configured weights | canary / A-B split |
| Latency | lowest measured latency | multi-region perf |
| Geolocation | client country/continent | compliance, localization |
| Geoproximity | distance + bias | deliberate traffic steering |
| Failover | primary/secondary + health | active/passive DR |
| Multi-Value | up to 8 random healthy | health-checked round-robin |
| IP-based | client IP CIDR | large known client networks |

DNS LB strengths: global, cheap, no data-path hop, any protocol (L3). Limits: TTL/caching delays, no live connection rebalance, no session state.

```bash
dig example.com +short                 # see returned record set
dig @8.8.8.8 example.com ; dig @1.1.1.1 example.com   # resolver variance
for i in $(seq 5); do dig +short example.com; done    # observe weighted/multi-value spread
```

## Interview Prep

**Mid**: "How does DNS-based LB work?"

**Senior**: "Limits of DNS for failover?"

**Staff**: "Design global LB combining DNS + anycast."

## Next Chapter

→ [C04 — HTTP, HTTPS, HTTP/2, HTTP/3](../C04/README.md)
