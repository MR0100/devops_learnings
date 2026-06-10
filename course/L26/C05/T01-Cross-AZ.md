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

K8s topologyAware:
```yaml
service.kubernetes.io/topology-mode: Auto
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
# K8s topology
spec:
  internalTrafficPolicy: Cluster   # or Local
service.kubernetes.io/topology-mode: Auto
```

```bash
# CUR query
WHERE line_item_usage_type LIKE '%InterAZ%'
```

## Interview Prep

**Mid**: "Cross-AZ cost."

**Senior**: "Mitigate."

**Staff**: "Network cost strategy."

## Next Topic

→ [T02 — NAT Gateway Costs](T02-NAT-Costs.md)
