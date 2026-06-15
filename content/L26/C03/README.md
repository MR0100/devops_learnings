# L26/C03 — Compute Optimization

## Topics

- **T01 Right-Sizing** — Match resources to actual usage
- **T02 Reserved Instances & Savings Plans** — Commitment discounts
- **T03 Spot Instances** — 70-90% off for interruptible
- **T04 Graviton & ARM Migration** — 20-40% off compute

## Right-Sizing

The single biggest lever for most teams. 30-50% of instances are oversized.

### Approach
1. Collect 14-30 days of CPU + memory metrics
2. Find p95 usage
3. Compare to provisioned
4. If p95 < 50% of provisioned: drop down a size
5. Verify (don't go too small; leave headroom for spikes)

### Tools
- **AWS Compute Optimizer** (free) — recommends size based on metrics
- **AWS Trusted Advisor**
- **Densify** (commercial) — across clouds
- **K8s VPA** (Vertical Pod Autoscaler) — recommends pod requests

### K8s Pod Right-Sizing
```yaml
resources:
  requests:
    cpu: 100m       # actual baseline
    memory: 256Mi
  limits:
    memory: 512Mi   # cap; for OOM protection
```

Common mistakes:
- requests = limits = waste if usage is variable
- requests too low → eviction risk
- no limits → noisy neighbor

### Storage Right-Sizing
- EBS gp3 with provisioned IOPS where needed
- S3 lifecycle (Standard → IA → Glacier)
- Snapshot cleanup (orphans add up)

### DB Right-Sizing
- Trickier (data growth + IOPS need)
- Postgres / MySQL: monitor connections, IOPS, buffer pool hit
- RDS Performance Insights helps

## Reserved Instances (RI)

Commit to instance type + region + 1-3 years. ~30-72% off.

### Variants
- Standard (no flexibility)
- Convertible (can change family within tenure)
- Zonal (one AZ; no flex) vs Regional (any AZ in region)

### Strategy
- Buy for steady-state baseline (analyze 90-day usage)
- Don't 100% commit (leave 20-30% on-demand for flex)
- Mix tenures (some 1-yr, some 3-yr)
- Convertible if you might change families

### RI Marketplace
Sell unused RIs (Standard, not Convertible). Recover some cost.

## Savings Plans (AWS)

More flexible than RIs.

### Compute Savings Plans
- $X/hr commitment for 1 or 3 years
- Apply across instance family, size, region, OS, tenancy
- ~66% off (3-year, no upfront)
- **Recommended starting point**

### EC2 Instance Savings Plans
- Lock to specific family + region
- Better discount than Compute SP (~72%)
- Less flexibility

### Compute SP also applies to:
- EC2
- Fargate
- Lambda

### Best Practice
1-yr Compute Savings Plans for baseline (sustainable commitment).

## Spot

Interruptible compute at 70-90% off.

### AWS Spot
- 2-min interruption warning
- Capacity-optimized strategy minimizes interruption
- Spot Fleet across types/AZs for resilience

### Best For
- Stateless web (with proper drain)
- Batch jobs (idempotent, restartable)
- CI runners (ephemeral)
- K8s workloads with PDB + graceful shutdown
- ML training (with checkpointing)

### Worst For
- Stateful (lose state on interruption)
- Long-running critical requests
- Single-instance services (no redundancy)

### Karpenter + Spot
Modern K8s pattern: Karpenter provisions spot nodes; gracefully drains on interruption.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]      # fall back to on-demand
```

### Spot Interruption Handling
- aws-node-termination-handler DaemonSet drains nodes
- App handles SIGTERM with grace period

## Graviton / ARM

AWS Graviton (m6g, c7g, r7g, etc.) — ARM-based, ~20-40% cheaper, ~20% better performance per dollar.

### Compatible Workloads
- Most modern languages (Go, Rust, Java, Python, Node)
- Containers (multi-arch images)
- Most databases (Postgres, MySQL, Redis)
- Lambda (ARM option)
- ECS/EKS (multi-arch builds)

### Migration
- Build multi-arch images (`docker buildx --platform linux/amd64,linux/arm64`)
- Test on Graviton (CI matrix)
- Cut over by instance family swap

### Wins
A typical workload: 20-30% lower bill for same performance. Significant for large fleets.

## Auto-Scaling Discipline

### Horizontal
- HPA on CPU/memory or custom metrics
- Down to a minimum to avoid cold pods
- KEDA for event-driven (Kafka lag, queue depth)

### Vertical
- VPA recommendations for pod sizing
- VPA Updater is risky; recommend mode + manual review

### Cluster
- Cluster Autoscaler or Karpenter
- Scale to zero off-hours (dev environments)

### Schedule-Based
- Cron-scaled (scale up before peak; scale down after)
- Pre-warm before known load surges

## Off-Hours Shutdown

For dev/test:
- Shut down nights + weekends
- Save 60-70% over 24/7
- Resume in minutes
- Tools: Instance Scheduler, lambda + EventBridge cron

## Idle Resource Cleanup

Common waste sources:
- Stopped instances (still paying for EBS)
- Unattached EBS volumes
- Old snapshots
- Unused Elastic IPs (charged if not associated)
- Idle ALBs
- Empty load balancers
- Orphaned EKS clusters
- Unused NAT GWs

Run cleanup weekly. Tools: Cloud Custodian policies.

## Compute Cost Wins (Approximate)

| Lever | Savings |
|---|---|
| Right-sizing | 20-40% on compute |
| Savings Plans | 25-50% on compute |
| Spot | 70-90% on eligible workloads |
| Graviton | 20-30% on compute |
| Right-sizing + SP + Graviton | 50-70% combined |
| Off-hours shutdown (dev) | 60-70% on dev |

## Interview Themes

- "Right-sizing — process"
- "Compute SP vs EC2 Instance SP"
- "When Spot? When NOT?"
- "Graviton — migrate strategy"
- "K8s cost optimization"
