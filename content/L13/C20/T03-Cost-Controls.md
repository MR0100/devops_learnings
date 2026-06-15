# L13/C20/T03 — Cost Controls

## Learning Objectives

- Control K8s cost
- Apply optimization techniques

## Cost Drivers

In K8s cluster:
- Nodes (60-80% of cost)
- LBs ($20-50/mo each)
- EBS volumes
- NAT GW (huge sometimes)
- Egress (cross-AZ, cross-region, Internet)
- Logging / monitoring storage
- Add-ons (control plane, support tier)

## Optimization Strategies

### 1. Right-Size Workloads
Match requests to actual usage:
- VPA for recommendations
- Goldilocks dashboard
- Manual review with Prometheus

Over-provisioning by 50% common; cut to 10-20%.

### 2. Reduce Headroom
Maintain 20% headroom; not 50%.

Karpenter consolidates; faster scale-up means less buffer needed.

### 3. Spot Instances
For tolerant workloads:
- 50-90% off
- Karpenter manages
- Mix with on-demand

For 30-50% Spot: typical safe mix.

### 4. Reserved / Savings Plans
For baseline:
- 30-72% off
- 1 or 3 year commit
- Plan baseline; on-demand for surge

### 5. Right-Size Nodes
Don't run 10 small + 10 medium nodes. Consolidate:
- Karpenter picks optimal
- Bin-pack efficiently

### 6. Cluster Consolidation
Multiple small clusters? Combine.
- Save control plane fees
- Better bin-packing

### 7. Reduce LB Costs
Per-Service LB → Ingress (one LB; many Services).

For 50 Services: $1000/mo → $50/mo (one ALB).

### 8. NAT Cost
Often massive. Reduce:
- VPC endpoints for S3, DynamoDB (free)
- Interface endpoints for high-traffic services
- Centralized egress

### 9. Egress
- Cache at edge (CloudFront)
- Compress
- Reduce cross-AZ
- Stay in region

### 10. Log Volume
Cost per GB:
- Datadog: $0.10/GB
- CloudWatch: $0.50/GB

Sample / drop INFO. Keep ERROR.

## Kubecost / OpenCost

K8s cost visibility:
```bash
helm install kubecost kubecost/cost-analyzer
```

Dashboard:
- Cost per namespace
- Cost per workload
- Idle resources
- Recommendations

For: chargeback, visibility.

OpenCost: open-source equivalent.

## Per-Namespace Tracking

Tag pods:
```yaml
metadata:
  labels:
    team: platform
    cost-center: eng
```

Kubecost aggregates by labels.

## Cost Per Workload

```
Workload cost = (CPU_request × CPU_cost) + (Memory_request × Memory_cost) + (Volume × Storage_cost)
```

For: per-app cost attribution.

## Idle Resources

```bash
# Pods using <10% CPU
kubectl top pod -A | awk '$2 ~ /[0-9]+m/ && $2 < 100 {print}'
```

Idle = waste. Investigate.

## Idle Node Consolidation

Karpenter:
```yaml
disruption:
  consolidationPolicy: WhenUnderutilized
  consolidateAfter: 30s
```

Karpenter moves pods to fewer nodes; deletes empty.

## Scale to Zero

For dev / sporadic workloads:
- KEDA: zero pods when idle
- Knative: HTTP-based scale to zero

Saves at idle.

## Off-Hours Shutdown

For dev / staging:
- Scale down at 6 PM
- Scale up at 9 AM
- Save 60% (12 of 24 hr off)

Tools:
- KubeDownScaler
- Custom CronJobs

## Right-Size Process

1. Deploy with conservative defaults
2. Monitor 1 week
3. VPA recommendations
4. Adjust
5. Verify
6. Iterate quarterly

## Avoid Anti-Patterns

- Over-provisioned for "safety"
- All on-demand
- No HPA (always max)
- Single huge cluster per env (vs multi-tier)
- Verbose logging in prod

## Multi-Tier Clusters

Different node groups:
- Critical: on-demand, reserved
- Standard: mix
- Batch: spot

Per-workload affinity.

## EBS Volume Costs

- gp3 instead of gp2 (newer + cheaper)
- Right-size (don't over-allocate)
- Delete orphaned (after PV release)

```bash
# Orphan volumes
kubectl get pv --field-selector status.phase=Released
```

## Image Storage

ECR / GCR / ACR:
- Lifecycle policy (delete old)
- Avoid huge images (multi-stage builds)
- Shared base images

## Monitoring Costs

Prometheus:
- Retention limits
- Cardinality control
- Thanos / Mimir for long-term (S3 cheap)

Grafana Cloud / Datadog: managed but $$$.

## Cluster Add-On Costs

- EKS control plane: $73/mo
- Datadog: $25-100/host/mo
- New Relic, Splunk: similar
- ArgoCD: free
- Karpenter: free

For: budget management.

## Trade-Offs

Cost vs:
- Performance (right-sizing)
- Reliability (HA)
- Speed (provisioned vs autoscale)

Document choices.

## Quarterly Review

- Cost trend (up / down)
- Per-team / app cost
- Optimization opportunities
- Reserved capacity utilization

## Chargeback / Showback

For multi-team:
- Showback: tell teams their cost
- Chargeback: bill them

For: incentive to optimize.

## Cost Budget

Per team:
- Monthly limit
- Alert at 80%
- Block at 100%

For: spending control.

## Anomaly Detection

Cloud:
- AWS Cost Anomaly Detection
- Datadog cost anomaly

Alert on unusual spend.

## Best Practices

- Kubecost / OpenCost installed
- Per-team labels
- VPA recommendations regular
- Karpenter for consolidation
- Spot for tolerant
- Reserved for baseline
- Off-hours shutdown (non-prod)
- Quarterly review
- Document optimization decisions

## Common Mistakes

- No visibility (Kubecost not installed)
- Over-provisioning
- Idle workloads
- All on-demand
- Per-service LB
- Verbose logging
- Forgotten dev environments
- No labels (can't attribute)

## ROI of Optimization

For 10000-pod cluster ($100k/mo):
- Right-sizing: -20% = $20k saved
- Spot mix: -30% nodes = $20k
- Karpenter consolidation: -10% = $10k
- Total: $50k/mo saved

Worth 1 engineer.

## FinOps

Discipline:
- Visibility
- Optimization
- Governance

Cross-functional: Finance + Engineering + Ops.

## Quick Refs

```bash
# Kubecost
helm install kubecost kubecost/cost-analyzer

# Resource usage
kubectl top pod -A

# Idle pods
kubectl top pod -A | sort -k 2

# Right-size with VPA
kubectl get vpa -A

# Karpenter consolidation
kubectl get nodepool
```

## Interview Prep

**Mid**: "K8s cost drivers."

**Senior**: "Cost optimization program."

**Staff**: "FinOps strategy for org."

## Next Topic

→ [T04 — Compliance Posture](T04-Compliance.md)
