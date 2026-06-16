# L26/C05/T01 — Cross-AZ Traffic

## Learning Objectives

- Identify cross-AZ cost
- Reduce

## Cross-AZ Cost

AWS:
- $0.01-0.02/GB inter-AZ
- Both directions

For high traffic: significant.

## Example

10 TB/day cross-AZ:
- $100-200/day
- $3000-6000/month

## Causes

### LB → Backends
LB in AZ-A → backends in AZ-B = cross-AZ.

Mitigation: cross-zone LB OFF for NLB; backend in same AZ.

### Replication
Cross-AZ replication = cost.

For: HA; accept.

### Service to Service
A in AZ-1 calls B in AZ-2.

K8s zone-aware routing. The older annotation is **deprecated**:
```yaml
# DEPRECATED — Topology Aware Hints / Routing annotation
service.kubernetes.io/topology-mode: Auto
```

The current approach is the `spec.trafficDistribution` field on the Service
(GA in Kubernetes 1.31), which keeps traffic in-zone when endpoints are
available there and spills over otherwise:
```yaml
apiVersion: v1
kind: Service
spec:
  trafficDistribution: PreferClose   # prefer same-zone endpoints
```

Prefer same AZ.

## Topology-Aware Routing

K8s:
- Routes to same AZ first
- Cross-AZ as fallback

For: cost + latency.

## Cross-Zone LB

ALB/NLB:
- ALB cross-zone always on (no extra cost)
- NLB cross-zone optional (extra cost)

For NLB: disable cross-zone if backends in all AZs (avoid charge).

## Service Mesh

Istio locality:
```yaml
trafficPolicy:
  loadBalancer:
    localityLbSetting:
      enabled: true
```

Prefer local AZ.

## VPC Endpoints

Avoid traffic via NAT:
- S3 endpoint: free
- Other services: hourly + GB

For: avoid NAT cost.

## Identify

CloudWatch metrics:
- `NetworkOut` per instance
- Cost by AZ in CUR

```sql
SELECT line_item_usage_type, SUM(line_item_unblended_cost)
FROM cur
WHERE line_item_usage_type LIKE '%DataTransfer%Out-Bytes%'
GROUP BY line_item_usage_type
```

## Mitigations

- Topology-aware (K8s)
- Same-AZ preference (mesh)
- Cross-zone LB off (NLB)
- Co-locate hot services

## Trade-Off

- Same AZ: cheap; less HA
- Cross AZ: HA; expensive

For: HA important; design carefully.

## Real Examples

### Many SaaS
Cross-AZ accidentally high; can be 30%+ of cloud bill.

### Optimizations
Save 50-80% with topology-aware.

## Best Practices

- Topology-aware routing
- VPC endpoints
- Co-locate services
- Monitor per-AZ traffic
- Cross-zone LB only when needed

## Common Mistakes

- All cross-AZ (no topology)
- NAT for AWS services (S3, etc.)
- Don't measure

## Quick Refs

```yaml
# K8s zone-aware routing
spec:
  internalTrafficPolicy: Cluster   # or Local
  trafficDistribution: PreferClose # current (GA 1.31); replaces the
                                   # deprecated topology-mode: Auto annotation
```

```bash
# CUR query
WHERE line_item_usage_type LIKE '%InterAZ%'
```

## Interview Prep

**Junior**: "What is cross-AZ traffic cost?" — AWS charges roughly $0.01–0.02/GB for traffic between Availability Zones, in *both* directions. For chatty microservices spread across AZs this adds up — easily thousands of dollars a month and sometimes 30%+ of the bill.

**Mid**: "How do you reduce cross-AZ traffic?" — Keep traffic in-zone: zone-aware routing in Kubernetes (`trafficDistribution: PreferClose`, replacing the deprecated `topology-mode: Auto` annotation), Istio locality load balancing, co-locating chatty services, and disabling NLB cross-zone load balancing when backends already exist in every AZ. Use VPC endpoints to avoid routing AWS-service traffic through NAT.

**Senior**: "What's the trade-off in cutting cross-AZ traffic?" — Same-AZ preference is cheaper and lower-latency but reduces resilience, because if that AZ degrades you lose the in-zone path. The right design keeps multi-AZ redundancy for availability while preferring same-AZ for the hot path, so you get most of the cost saving without a single-AZ failure mode — and you measure per-AZ transfer in the CUR to confirm.

**Staff**: "Design a network-cost strategy for a microservices platform." — Make cross-AZ and egress visible first (CUR queries on DataTransfer line items), then attack the biggest flows: zone-aware routing/locality LB to keep hot paths in-zone, VPC endpoints to bypass NAT for AWS services, centralized vs per-AZ NAT trade-offs, and co-locating chatty dependencies. Treat it as continuous: a chatty new service can silently re-inflate cross-AZ cost, so monitor per-AZ transfer and alert on anomalies rather than auditing once.

## Next Topic

→ [T02 — NAT Gateway Costs](T02-NAT-Costs.md)
