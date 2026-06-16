# L08/C09/T02 — Route 53 (Routing Policies)

## Learning Objectives

- Configure DNS
- Use routing policies

## Route 53

Authoritative DNS + domain registrar + health checks.

100% SLA (one of few AWS services).

## Hosted Zones

- Public: Internet-resolvable
- Private: VPC-only

```bash
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)
```

Returns NS records; configure at registrar.

## Records

- A: IPv4
- AAAA: IPv6
- CNAME: alias to name (not at apex)
- ALIAS: AWS-specific; CNAME-like; works at apex
- MX: mail
- TXT: arbitrary text (verification, SPF)
- SRV: service
- NS: name servers
- SOA: zone authority
- CAA: cert authority authorization

## ALIAS Records

For AWS targets:
- ALB, NLB
- CloudFront
- S3 website
- Other Route 53 records

Free; no extra DNS hop.

```yaml
my.example.com → ALIAS → my-alb-123456.us-east-1.elb.amazonaws.com
```

CNAME apex isn't allowed by DNS spec; ALIAS works.

## Routing Policies

| | Use |
|---|---|
| Simple | One answer (or multiple round-robin) |
| Weighted | Split traffic % |
| Latency | Lowest-latency region |
| Geolocation | By user country |
| Geoproximity | By distance with bias |
| Failover | Active/passive HA |
| Multi-Value | Multiple healthy IPs |
| IP-Based | By client IP |

## Simple

Default. Returns IPs in record. Round-robin (clients pick).

For: one endpoint.

## Weighted

Split traffic:
```
Record 1: 70% → v1
Record 2: 30% → v2
```

For: canary, A/B test.

## Latency-Based

Routes to lowest-latency region:
```
us-east-1 endpoint
eu-west-1 endpoint
ap-south-1 endpoint
```

Route 53 picks closest to user (real measured latency).

For: global low-latency apps.

## Geolocation

By continent / country / state:
```
US → US endpoint
EU → EU endpoint
default → US endpoint
```

For: compliance, content licensing, language.

## Geoproximity

Like Latency but with bias (you set):
- Bias 50 → resources serve 50% larger area than default
- Use Route 53 Traffic Flow (visual editor)

## Failover

Primary + secondary:
- Health check on primary
- If unhealthy: serve secondary

```yaml
Primary: 10.0.0.5 (with health check)
Secondary: 10.0.1.5
```

For: active-passive HA, DR.

## Multi-Value

Up to 8 healthy IPs returned. Client picks.

Like Simple but with health checks (drop unhealthy).

For: simple HA across instances.

## IP-Based

Route by client IP CIDR:
- Corp network → internal endpoint
- General Internet → public endpoint

## Health Checks

```bash
aws route53 create-health-check --caller-reference ... --health-check-config '{
  "Type": "HTTP",
  "ResourcePath": "/health",
  "FullyQualifiedDomainName": "api.example.com",
  "Port": 80,
  "RequestInterval": 30,
  "FailureThreshold": 3
}'
```

Types:
- HTTP / HTTPS
- TCP
- Calculated (combine others)
- CloudWatch alarm

Used with failover, multi-value, etc.

## TTL

How long DNS resolvers cache:
- Long (1h+): fewer queries; slow change propagation
- Short (60s): fast change; more queries

For failover: ~60s.

For static records: longer.

## Private Hosted Zones

DNS resolution within VPC:
```bash
aws route53 create-hosted-zone --name internal.example.com --vpc VPCRegion=us-east-1,VPCId=vpc-xxx --hosted-zone-config PrivateZone=true
```

Records resolved only within associated VPCs.

For: internal service discovery.

## Resolver

Hybrid DNS:
- Outbound endpoints: VPCs resolve on-prem DNS
- Inbound endpoints: on-prem resolves VPC DNS

For: hybrid cloud DNS.

## DNS Firewall

Block malicious domains:
```bash
aws route53resolver create-firewall-domain-list --name baddomains
aws route53resolver create-firewall-rule-group --name myrules
```

For: prevent C2 / phishing / malware DNS.

## Traffic Flow

Visual editor for complex routing:
- Combine policies
- Geo → Weighted → Latency, etc.
- Version control

Cost: $50/policy/mo.

## DNSSEC

Sign records; clients verify. Prevents cache poisoning.

Enable per hosted zone. Complex; mostly compliance/govt.

## Pricing

- Hosted Zone: $0.50/mo
- Queries: $0.40 per million
- Health Check (basic): $0.50/mo
- Domain registration: per TLD ($12+/yr)

Cheap for most. Heavy DNS: bulk pricing helps.

## Domain Registration

Buy / transfer domain at Route 53:
```bash
aws route53domains register-domain --domain-name myapp.com --duration-in-years 1 --admin-contact ...
```

Auto-renew enabled by default.

## DNS-Based Failover Examples

### Active-Passive
Primary: us-east-1 LB (health checked)
Secondary: us-west-2 LB

Primary down → DNS returns secondary.

### Multi-Region Latency
Three regions; users routed to nearest.
Health-checked; unhealthy region not returned.

## Common Mistakes

- Long TTL on records you want to change quickly
- No health check (return dead IPs)
- CNAME at apex (use ALIAS)
- Same TTL for everything

## Best Practices

- ALIAS for AWS targets
- Short TTL for failover-relevant records
- Health checks on all critical
- Private zone for internal
- DNSSEC for compliance
- Resolver for hybrid

## Monitoring

CloudWatch:
- HealthCheckStatus per check
- ConnectionTime, TimeToFirstByte (HTTPS)
- DNS queries per zone

Alert on:
- Health check fails sustained
- Anomalous query patterns

## SLA

100% for Route 53. Practically never down.

But propagation delays (TTL) still apply.

## Migration

For zone migration:
1. Create zone in Route 53
2. Add records
3. Test (resolve specific NS)
4. Lower TTL on existing
5. Wait
6. Update registrar NS
7. Decommission old

## DNS Records Export

```bash
aws route53 list-resource-record-sets --hosted-zone-id Z123
```

Export; backup.

## Common Anti-Patterns

- All records TTL 1 day; can't quickly failover
- Hardcoded IPs (no DNS abstraction)
- Wildcard for everything
- No backup of records

## Latency Performance

Route 53 anycast: ~5-50 ms resolution globally.

Resolvers cache; reduce queries.

## Quick Refs

```bash
# Zone
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)

# Record
aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://change.json

# Health check
aws route53 create-health-check --caller-reference ... --health-check-config ...

# Get
aws route53 list-resource-record-sets --hosted-zone-id Z123
```

## Interview Prep

**Junior**: "DNS A vs CNAME."

**Mid**: "Route 53 failover."

**Senior**: "Latency-based routing tradeoffs."

**Staff**: "Global DNS architecture."

## Next Topic

→ [T03 — Global Accelerator](T03-Global-Accelerator.md)
