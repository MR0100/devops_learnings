# L26/C03/T01 — Right-Sizing

## Learning Objectives

- Right-size compute
- Find waste

## Right-Sizing

Match instance size to actual usage:
- Avoid over-provisioning
- Save money

## Why

Common: 50-70% utilization average.

If average CPU 20%: can downsize.

## Methods

### Manual
- Check CloudWatch metrics
- Resize if low

### Auto
- AWS Compute Optimizer
- Azure Advisor
- GCP Recommender

### Tools
- Vantage
- CloudHealth
- Custom analysis

## AWS Compute Optimizer

```bash
aws compute-optimizer get-ec2-instance-recommendations
```

Returns:
- Current size
- Recommendation
- Estimated savings

## Metrics to Check

- CPU %
- Memory %
- Network throughput
- IOPS

For 14 days:
- p95 CPU < 40% → downsize
- p95 CPU > 80% → upsize

## Right-Sizing Steps

1. Identify candidates (low utilization)
2. Plan resize (downtime?)
3. Test in staging
4. Resize prod
5. Monitor

## Auto-Scaling

For variable load:
- ASG
- HPA (K8s)
- Scale to demand

For: efficient.

## Spot for Variable

Combined with spot:
- Burstable + spot
- Save 70%+

## RDS Right-Sizing

```bash
aws rds describe-db-instances
# Check actual usage
```

DB sizing:
- CPU
- Memory (key for cache)
- IOPS
- Connections

## EBS

```bash
aws ec2 describe-volumes
```

- IOPS used vs provisioned
- gp3 (cheaper than gp2 often)
- Snapshots cleanup

## RDS gp3

Migrate gp2 → gp3:
- 20% cheaper at same perf

## Continuous

Monthly review:
- Top resources
- Utilization trends
- Resize candidates

## Quick Wins

- Idle EC2 (running but no traffic)
- Underutilized RDS
- Oversized Lambda memory
- Unused EBS volumes

## Cultural

Right-sizing as habit:
- PR review includes size
- Cost in design discussion

## Best Practices

- Compute Optimizer recommendations
- Quarterly right-sizing
- Auto-scale where possible
- Right-size on deploy

## Common Mistakes

- Over-provision "just in case"
- No review
- Skip auto-scale
- Same size for dev/prod

## Quick Refs

```bash
aws compute-optimizer get-ec2-instance-recommendations
aws compute-optimizer get-rds-database-recommendations
aws compute-optimizer get-lambda-function-recommendations
```

## Interview Prep

**Mid**: "Right-sizing."

**Senior**: "Continuous right-sizing."

**Staff**: "FinOps culture."

## Next Topic

→ [T02 — Reserved Instances & Savings Plans](T02-RI-SP.md)
