# L26 — FinOps & Cloud Cost Optimization

## Overview

Cloud bills grow. Senior engineers are accountable for spend. This lecture covers FinOps practice and concrete optimizations.

**7 chapters, 22 topics.**

## Chapter Map

### [C01](C01/) — FinOps Principles
- T01 The FinOps Foundation Framework
- T02 Inform, Optimize, Operate Phases

### [C02](C02/) — Cost Visibility
- T01 Cost Allocation Tags
- T02 Showback vs Chargeback
- T03 Tools (CUR + Athena, CUDOS, Cloudability, Vantage)
- T04 Unit Economics (Cost per Request & per Tenant)

### [C03](C03/) — Compute Optimization
- T01 Right-Sizing
- T02 Reserved Instances & Savings Plans
- T03 Spot Instances (and Karpenter Strategy)
- T04 Graviton & ARM Migration

### [C04](C04/) — Storage Optimization
- T01 S3 Storage Class Analysis
- T02 Intelligent Tiering
- T03 Snapshot Cleanup

### [C05](C05/) — Networking Cost Traps
- T01 Cross-AZ Traffic
- T02 NAT Gateway Costs
- T03 Data Egress

### [C06](C06/) — Kubernetes Cost Management
- T01 Kubecost / OpenCost
- T02 Pod Right-Sizing
- T03 Cluster Bin-Packing

### [C07](C07/) — Building a FinOps Practice
- T01 Anomaly Detection
- T02 Forecasting & Budgets
- T03 Engineering Incentives

## The FinOps Framework

```
Inform     → visibility, allocation, benchmarking
Optimize   → right-sizing, RIs/SPs, spot, architecture
Operate    → policy, automation, accountability
```

## Quick Wins (Order of Investment)

1. **Tagging discipline** — can't optimize what you can't allocate
2. **Right-size compute** — 30–50% of instances are oversized
3. **Reserved/Savings Plans** — 30–60% off on stable load
4. **Storage class tiering** — S3 lifecycle / Intelligent-Tiering
5. **Snapshot/log cleanup** — often huge silent costs
6. **Spot for stateless** — 50–90% off
7. **Networking review** — cross-AZ, NAT, egress
8. **Graviton/ARM** — 20–40% off compute on supported workloads

## Cross-AZ Cost Trap

AWS charges $0.01/GB *each direction* for cross-AZ traffic. A chatty microservices architecture spanning AZs can cost $1000s/day.

Mitigations:
- Topology-aware routing (K8s Service `internalTrafficPolicy: Local`, Topology Aware Hints)
- Per-AZ caches
- Co-locate chatty dependencies

## NAT Gateway

- $0.045/hr per NAT GW + $0.045/GB data processed
- Multi-AZ HA × 3 = $97/month minimum + data
- A chatty service can hit $10K/month easily
- Mitigations: VPC endpoints for AWS services, centralized egress, per-AZ NAT

## Spot Strategy

```
Workload type        Spot suitability
─────────────────    ────────────────
Web (stateless)      Excellent (graceful drain)
Batch / training     Excellent
Stateful (DB)        Poor (data loss risk)
Critical request     Bad without fallback
Cron jobs            Excellent
CI runners           Excellent
```

Use Karpenter to mix spot+on-demand for risk management.

## K8s Cost Allocation

Kubecost/OpenCost queries:
- Per-namespace cost
- Per-deployment cost
- Idle cost (unused requests)
- Efficiency (usage / request ratio)

Show back to teams; create accountability.

## Engineering Incentives

- Surface cost in dev dashboards
- Quarterly cost OKRs per team
- Idle resource decom monthly
- Cost regression as SLO (with a budget)

## Recommended Reading

- *Cloud FinOps* — Storment & Fuller
- *FinOps Foundation* training
- Vantage / Cloudability blogs

## Interview Themes

- "Walk me through FinOps practice"
- "Top 5 levers to reduce cloud cost"
- "Spot — when and when not"
- "K8s cost allocation — how?"

## Next

→ [L27 — Disaster Recovery, HA & Multi-Region](../L27/README.md)
