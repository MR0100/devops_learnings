# L26/C06 — Kubernetes Cost Management

## Topics

- **T01 Kubecost / OpenCost** — K8s cost visibility
- **T02 Pod Right-Sizing** — Match requests to usage
- **T03 Cluster Bin-Packing** — Pack pods efficiently

## Why K8s Cost Is Hard

K8s shares infrastructure:
- Cloud bill shows cluster cost
- But which pod / namespace / team caused it?

Per-pod attribution = challenge solved by Kubecost / OpenCost.

## Kubecost / OpenCost

OpenCost is the OSS spec/implementation; Kubecost is the commercial product on top.

### What It Does
- Read K8s metrics (CPU/mem usage per pod)
- Read cloud bill (cluster cost)
- Allocate cluster cost to pods proportionally
- Aggregate to namespace, label, deployment
- Idle cost calculation

### Install
```bash
helm install kubecost kubecost/cost-analyzer
```

### Outputs
- Per-namespace cost (last 30 days)
- Per-deployment cost
- Per-label cost
- Efficiency (usage / request ratio)
- Idle cost (allocated but unused)
- Forecast

### Integration
- Slack alerts on budget overruns
- Recommendations (right-size pod requests)
- Prometheus metric export

## Pod Right-Sizing

The biggest K8s cost lever.

### Overcommit
If requests = limits and limit = peak, you waste resources at average.
Typical: requests at p50, limits 2-3× requests.

### VPA Recommendations
```bash
kubectl describe vpa my-app
# Shows recommended requests based on historical usage
```

Apply recommendations; verify (don't shrink too aggressively).

### Memory Limit Trap
Java/Go runtime sees the limit and sizes heap accordingly.
- Limit too high: wastes
- Limit too low: OOM
- Use `MaxRAMPercentage` (Java), `GOMEMLIMIT` (Go) for container-awareness

## Cluster Bin-Packing

Goal: high utilization per node; fewer nodes total.

### Better Bin-Packing With
- Smaller pod requests (more pods fit per node)
- Diverse pod sizes (mix big + small fits puzzle better)
- Karpenter (provisioner picks right instance type per pod)

### Karpenter Consolidation
```yaml
disruption:
  consolidationPolicy: WhenEmpty
  consolidateAfter: 1m
```

Empty nodes are auto-removed. Karpenter then re-packs onto fewer nodes.

### Bad Bin-Packing Symptoms
- 30+ nodes at 30% utilization
- Many "right-sized" requests but lots of idle CPU
- Daemons preventing right-pack (some sticky pods)

## Multi-Tenant K8s Cost

If multiple teams share a cluster:
- Per-namespace cost (via labels/Kubecost)
- Showback monthly to teams
- Or chargeback (allocate cloud bill internally)

### Namespace ResourceQuota
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 100Gi
    limits.cpu: "40"
    limits.memory: 200Gi
    persistentvolumeclaims: "10"
```

Forces teams to be intentional.

## HPA Smarter Scaling

```yaml
spec:
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # scale up at 70%
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # be slow to scale down
    scaleUp:
      stabilizationWindowSeconds: 0     # be fast to scale up
```

Don't oversize for safety; HPA handles bursts. Set minReplicas low.

## Karpenter

Replaces Cluster Autoscaler for AWS. Choose instance type per pod requirement.

### Why Cheaper
- Right-sized nodes (not fixed instance types)
- Spot integration
- Faster provisioning (60s vs 3-5 min)
- Consolidation (kill empty / pack onto fewer)

### Config
```yaml
apiVersion: karpenter.k8s.aws/v1
kind: NodePool
spec:
  template:
    spec:
      requirements:
        - { key: karpenter.sh/capacity-type, operator: In, values: [spot, on-demand] }
        - { key: node.kubernetes.io/instance-type, operator: In, values: [m6i.large, m6i.xlarge, m6a.large, m6g.large] }
        - { key: kubernetes.io/arch, operator: In, values: [amd64, arm64] }
  limits:
    cpu: 1000
    memory: 1000Gi
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 1m
```

Karpenter picks the cheapest instance type satisfying pod requirements at the moment.

## Spot in K8s

Mix on-demand and spot:
- Critical baseline on on-demand
- Burst on spot
- PDBs + graceful drain handle interruption

```yaml
nodeSelector:
  karpenter.sh/capacity-type: spot
tolerations:
  - { key: spot, operator: Exists, effect: NoSchedule }
```

## Idle Resource Pruning

Find:
- Pods with very low CPU/memory usage
- Deployments scaled high (oversized)
- Hundreds of stale jobs
- Old completed CronJobs

Tools:
- Goldilocks (recommend requests)
- Kubecost waste reports
- Custom: query Prometheus for low-util workloads

## Container Image Optimization

Smaller images:
- Faster pod startup
- Less pull time
- Less storage on nodes
- Less network egress for pulls

Multi-stage builds, distroless, scratch where possible.

## Off-Hours

Scale dev clusters to zero off-hours:
- Karpenter terminates idle nodes
- Pods scaled to 0 (via cron)
- Resume in minutes when needed

Save 60-70% on dev environments.

## Cost-Aware Engineering Culture

- Surface per-team cost in Slack weekly
- Cost reviews in sprint retros
- "Spend like the founder" mindset

## Interview Themes

- "K8s cost — how visualize per team"
- "Right-size pods — strategy"
- "Karpenter vs Cluster Autoscaler"
- "Spot in K8s — graceful handling"
- "Bin-packing — what makes it good or bad"
