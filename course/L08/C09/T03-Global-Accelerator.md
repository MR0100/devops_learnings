# L08/C09/T03 — Global Accelerator

## Learning Objectives

- Understand Global Accelerator
- Choose vs Route 53 / CloudFront

## What

Global anycast IP addresses; traffic routed to nearest healthy AWS endpoint via AWS backbone.

```
User → anycast IP → nearest AWS edge → AWS backbone → endpoint
```

vs Route 53 (DNS-based; client caches IP; resolution-time decision).
vs CloudFront (caches content; CDN).

## How

You get 2 static anycast IPs:
- Customers connect to one IP
- Traffic enters AWS edge closest to them
- AWS routes over backbone (fast, predictable)
- Reaches healthy endpoint

## Use Cases

- TCP / UDP services (not just HTTP)
- Gaming (low latency)
- IoT (static IPs for firewall allowlist)
- Multi-region failover (DNS too slow)
- API with strict latency

## Endpoints

Behind Global Accelerator:
- ALB
- NLB
- EC2
- Elastic IPs

Cross-region; you specify endpoint groups per region.

## Routing

Weighted across regions:
```
us-east-1: weight 100
eu-west-1: weight 100
```

Each user → nearest healthy.

Or specific endpoints:
```
ALB-1: weight 50
ALB-2: weight 50
```

## Health Checks

Built-in; remove unhealthy.

Faster failover than DNS (no TTL wait):
- DNS failover: TTL + propagation = minutes
- GA failover: seconds

## When GA vs Route 53

| | Route 53 | GA |
|---|---|---|
| Cost | Cheap | $$$ |
| Failover speed | Minutes | Seconds |
| Latency | Variable (DNS) | Predictable (backbone) |
| Static IPs | No | Yes |
| Protocols | HTTP via apps | TCP/UDP all |
| Caching | None | Path through AWS network |

For: tier-0 apps; strict latency; need static IPs; multi-region.

## When CloudFront vs GA

| | CloudFront | GA |
|---|---|---|
| Caching | Yes | No |
| Protocol | HTTP | TCP/UDP |
| Static IPs | No | Yes |
| Use | Cacheable content | Dynamic + non-HTTP |

For HTTP cacheable: CloudFront.
For TCP / UDP / dynamic: GA.

## Pricing

- $0.025 per hour (~$18/mo)
- $0.015/GB processed (US/EU)

Higher in other regions.

For high-volume: real money. But low-latency premium.

## Multi-Region Patterns

```
Customer → GA anycast IP → nearest AWS edge
  ├── us-east-1 ALB
  ├── us-west-2 ALB
  └── eu-west-1 ALB
```

GA routes to nearest healthy.

Failover automatic.

## Standard vs Custom Routing

Standard: connection to anycast IP → nearest endpoint.
Custom: VPC subnet + port mapping; for IoT / gaming with many endpoints.

## Static IPs Use Cases

Firewall allowlist:
- Partner needs to allowlist your IPs
- IPs change per region/region (without GA, multiple to allow)
- GA: 2 static IPs forever

## SLA

99.99% availability.

## Traffic Dial

Manually shift traffic:
```
us-east-1: dial 100% (full)
us-west-2: dial 0% (off)
```

For: gradual region migration; cutover.

## Performance

Latency reduction examples (AWS-published):
- 60% for HTTP from APAC to US backend
- Real numbers: 100-200ms saved possible

Test with vendor tool.

## Health Check

Per endpoint group; configurable:
- Interval
- Threshold
- Path / port

Unhealthy endpoint → traffic shifted to other in group, or other group.

## Common Patterns

### Multi-Region API
- ALB in 3 regions
- GA front
- Static IPs to API customers
- Failover seconds

### Gaming
- UDP servers in many regions
- GA static IP
- Users connect to nearest

### IoT
- Devices have GA IP hardcoded
- Region maintenance: no device change

## Anti-Patterns

- HTTP cacheable content (CloudFront cheaper)
- Single-region (GA overhead for nothing)
- High data + low value (cost)

## Best Practices

- Multi-region required
- TCP/UDP or strict latency
- Static IPs needed
- Health-checked endpoint groups
- Monitor

## Monitoring

CloudWatch:
- ProcessedBytesIn / Out
- NewFlowCount
- HealthyEndpointCount

## Setup

```bash
aws globalaccelerator create-accelerator --name myAccelerator
aws globalaccelerator create-listener --accelerator-arn ... --port-ranges FromPort=443,ToPort=443 --protocol TCP
aws globalaccelerator create-endpoint-group --listener-arn ... --endpoint-group-region us-east-1 --endpoint-configurations EndpointId=arn:aws:elasticloadbalancing:...
```

## Combine with Other

```
User → CloudFront (cache HTTP) → GA (static IP) → ALB → backend
```

Layered: CloudFront caches; GA fast routing.

## VPC Origins

CloudFront connects to VPC endpoints (no public IP needed). Reduces GA need in some cases.

## When NOT GA

- Tight budget; not strict latency
- Single region
- HTTP cacheable
- Route 53 + DNS failover acceptable
- Internal services (no global users)

## Common Mistakes

- GA + CloudFront when CloudFront alone fits
- Single-region with GA
- Forgetting hourly cost (always-on)
- Not testing actual latency improvement

## Quick Refs

```bash
# Create
aws globalaccelerator create-accelerator --name myGA

# Endpoint group
aws globalaccelerator create-endpoint-group --listener-arn ... --endpoint-group-region us-east-1 ...

# Update traffic dial
aws globalaccelerator update-endpoint-group --endpoint-group-arn ... --traffic-dial-percentage 50
```

## Interview Prep

**Mid**: "GA vs Route 53."

**Senior**: "When GA over CloudFront."

**Staff**: "Multi-region tier-0 with GA."

## Next Topic

→ [T04 — WAF & Shield](T04-WAF-Shield.md)
