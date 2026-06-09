# L08/C03/T05 — Spot, Savings Plans, Reserved Instances

## Learning Objectives

- Use each pricing model
- Optimize portfolio

## On-Demand

Pay per second / hour. No commitment.

Use: dev, prototyping, unknowns, short-lived.

Most expensive.

## Savings Plans (Modern)

Commit $X/hr for 1 or 3 years.

Two types:
- **Compute SP**: 66% off; flexible across EC2 family, region, OS, Fargate, Lambda
- **EC2 Instance SP**: 72% off; specific family + region; less flexible

Payment: No Upfront, Partial, All Upfront (bigger discount).

```
Compute SP: $5/hr × 1 yr = $43,800 commitment
Saves vs on-demand: ~$30k
```

Apply to running workload automatically; SP credit consumed by usage.

## Reserved Instances (Legacy)

Older; same idea; less flexible:
- Standard RI: specific instance type / OS / tenancy / region (not size? size flex for Standard)
- Convertible RI: can change family later

Discount: 30-72%.

SPs generally preferred now. Existing RIs grandfather.

## Spot Instances

Use spare AWS capacity; up to 90% off; can be reclaimed with 2-min notice.

```bash
aws ec2 request-spot-instances --spot-price 0.05 --instance-count 5 ...
```

Or via ASG with Spot allocation strategy.

Allocation strategies:
- price-capacity-optimized (default; recommended)
- capacity-optimized (least likely to interrupt)
- lowest-price (cheapest; more interruptions)
- diversified (spread across pools)

## Spot Use Cases

- Batch processing
- Stateless web tier (with on-demand fallback)
- CI/CD runners
- K8s worker nodes (with checkpointing)
- ML training (with snapshots)
- Big data (EMR Spot)

Avoid:
- Production DBs
- Stateful services without checkpointing
- Sensitive to interruption

## Mixed ASG

```yaml
MixedInstancesPolicy:
  LaunchTemplate: ...
  InstancesDistribution:
    OnDemandBaseCapacity: 2          # always 2 on-demand
    OnDemandPercentageAboveBaseCapacity: 0    # rest Spot
    SpotAllocationStrategy: price-capacity-optimized
  Overrides:
    - InstanceType: m6i.large
    - InstanceType: m6a.large
    - InstanceType: m7g.large
```

Baseline on-demand; surge Spot. ASG handles failover.

## Spot Best Practices

- Diversify instance types (different pools)
- Diversify AZs
- price-capacity-optimized strategy
- Handle 2-min termination warning
- Checkpoint state
- Restart-friendly app

## Spot Termination Handler

Detect impending termination:
```bash
curl http://169.254.169.254/latest/meta-data/spot/instance-action
# Returns 200 if termination scheduled; 404 otherwise
```

App should:
- Drain connections
- Save state
- Exit cleanly

K8s: aws-node-termination-handler installs DaemonSet.

## Spot Fleet

Pre-Mixed-ASG approach. Still supported. ASG Mixed Instances simpler.

## Capacity Reservations

Reserve capacity (no discount; vs pricing):
- Standalone: guaranteed capacity in AZ
- Linked with SP: capacity + discount
- Useful for: ensuring capacity in scale-out events

## On-Demand Capacity Reservation

```bash
aws ec2 create-capacity-reservation --instance-type m6i.large --instance-count 10 --availability-zone us-east-1a
```

Pay even if not used. For predictable need.

## Right-Sizing

Compute Optimizer (free) recommends. Often 30-50% savings via right-size.

## Strategy

For typical app:
- 60% on Savings Plan (steady baseline)
- 30% on-demand (variable)
- 10% Spot (batch, dev/test)

Adjust based on workload predictability.

## Calculation Example

App: 100 m6i.large 24/7.
- On-demand: 100 × $0.096/hr × 8760 = $84,000/yr
- 3-yr All Upfront SP: ~$30,000/yr (saves $54k)
- ROI: years 1-3 break even quickly

## Convertible vs Standard RI

Convertible: change family (m → r). Smaller discount.
Standard: fixed family. Larger discount.

For uncertain: Convertible. For sure: Standard.

## Workload Migration to SP

1. Run on on-demand
2. CloudWatch / Cost Explorer: identify steady usage
3. Commit SP for steady portion
4. Reserve excess for known spikes
5. Use Spot for tolerant

## Spot for K8s

EKS managed node groups with Spot:
```yaml
spec:
  capacityType: SPOT
  instanceTypes: [m6i.large, m6a.large, m7g.large]
```

Karpenter (modern node provisioning): picks Spot intelligently.

```yaml
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: [spot, on-demand]
```

## Coverage Tracking

SP utilization should be ~100%. If <70%: over-committed.

Cost Explorer:
- SP coverage: % of usage covered by SP
- SP utilization: % of SP commitment used

Both > 80% target.

## Don't Over-Commit

Commit only what you'll definitely use. Unused commit = wasted.

Recommendation: commit 70% of baseline; allow 30% on-demand for variation.

## Anomaly Detection

Spot price changes: AWS Cost Anomaly Detection alerts.

Sudden Spot interruption increase: capacity constraint; investigate.

## Common Mistakes

- All on-demand (most expensive)
- All Spot (interruptions kill prod)
- Long Standard RI for changing workload
- Forgotten SP for legacy
- Spot for stateful

## ProsperOps / Vendor Tools

Automate SP/RI portfolio. Buy/sell to optimize. Worthwhile at >$50k/mo spend.

## Quick Refs

```bash
# Buy SP
aws savingsplans create-savings-plan --upfront-payment-amount 100 ...

# RI list
aws ec2 describe-reserved-instances

# Spot price history
aws ec2 describe-spot-price-history --instance-types m6i.large --start-time ...
```

## Interview Prep

**Mid**: "Spot vs On-demand."

**Senior**: "SP portfolio strategy."

**Staff**: "Optimize $1M/mo EC2 bill."

## Next Topic

→ [T06 — Nitro System Architecture](T06-Nitro.md)
