# L30/C05 — Project 5: Cost-Optimized Spot-Heavy Workload Platform

## Topics

- **T01 Karpenter + Spot** — Provisioning
- **T02 Graceful Spot Interruption Handling** — Drain on signal
- **T03 Cost Dashboards** — Show the wins

## Goal

Demonstrate running a production-grade workload on spot at 70-80% cost reduction vs on-demand, with graceful handling of interruptions.

## Architecture

```
[EKS cluster]
├── Karpenter (provisioner)
├── Sample workload (web + worker)
├── aws-node-termination-handler (drain on spot interrupt)
├── PDBs (pod disruption budgets)
└── Kubecost / OpenCost (cost visibility)

Karpenter NodePool:
- Spot + On-Demand mix
- Multi-AZ
- Multi-instance-type (capacity-optimized strategy)
- Consolidation enabled
```

## Karpenter Setup

```bash
# Install Karpenter
helm install karpenter oci://public.ecr.aws/karpenter/karpenter \
  --version v1.0.0 \
  --namespace kube-system \
  --set settings.clusterName=demo \
  --set settings.interruptionQueue=karpenter-queue \
  --set controller.resources.requests.cpu=1 \
  --set controller.resources.requests.memory=1Gi
```

### NodePool
```yaml
apiVersion: karpenter.k8s.aws/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    metadata:
      labels:
        env: prod
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["m6i.large", "m6i.xlarge", "m6a.large", "m6a.xlarge", "m6g.large", "m6g.xlarge"]
        - key: topology.kubernetes.io/zone
          operator: In
          values: ["us-east-1a", "us-east-1b", "us-east-1c"]
      nodeClassRef:
        name: default
  
  limits:
    cpu: 1000
    memory: 1000Gi
  
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 1m
```

### EC2NodeClass
```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2023
  role: KarpenterNodeRole-demo
  subnetSelectorTerms:
    - tags: { karpenter.sh/discovery: demo }
  securityGroupSelectorTerms:
    - tags: { karpenter.sh/discovery: demo }
  metadataOptions:
    httpTokens: required           # IMDSv2 only
    httpPutResponseHopLimit: 2
```

## Spot-Optimized Application

### PDB
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web
spec:
  minAvailable: 75%
  selector:
    matchLabels:
      app: web
```

### Topology Spread
```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: ScheduleAnyway
      labelSelector:
        matchLabels: { app: web }
```

### Graceful Shutdown
```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: web
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 10 && /app/graceful-shutdown"]
```

App handles SIGTERM:
- Stop accepting new requests
- Finish in-flight
- Close DB connections
- Exit 0

## Spot Interruption Handling

### AWS Node Termination Handler
```bash
helm install aws-node-termination-handler \
  oci://public.ecr.aws/aws-ec2/aws-node-termination-handler \
  --namespace kube-system \
  --set enableSpotInterruptionDraining=true \
  --set enableRebalanceMonitoring=true
```

Monitors:
- Spot interruption notice (2-min warning)
- EC2 maintenance events
- Rebalance recommendations

On signal: cordon node + drain pods gracefully.

### Karpenter Built-in
Karpenter also handles spot interruption via the interruption queue. Either works; ANTH gives finer control.

## Cost Dashboards

### Install Kubecost
```bash
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost --create-namespace \
  --set kubecostToken="..."
```

Or OpenCost (free):
```bash
helm install opencost opencost-charts/opencost \
  --namespace opencost --create-namespace
```

### Metrics
- Per-namespace cost
- Per-deployment cost
- Per-team (via label)
- Efficiency (usage / request)
- Idle resources

## Comparison: Before / After

| | On-demand only | Karpenter + 80% spot |
|---|---|---|
| Compute cost | $5K/month | $1.2K/month |
| Reliability | 99.95% | 99.93% (small dip due to interruptions) |
| Operational complexity | Low | Slight increase (handle interrupts) |

Savings: 76%. With 99.93% still very acceptable.

## Demonstrating Robustness

Force spot interruption (FIS):
```yaml
# AWS FIS experiment
actions:
  interrupt-spot:
    actionId: aws:ec2:send-spot-instance-interruptions
    parameters: { durationBeforeInterruption: PT2M }
    targets: { SpotInstances: spot-targets }
```

Observe:
- Pod drain initiated
- New pod scheduled on different node (Karpenter quickly provisions)
- No customer-facing errors (PDB prevents too-many-going-down)

## Cost Allocation

Tag workloads by team:
```yaml
metadata:
  labels:
    team: payments
    cost-center: platform
```

Kubecost aggregates by label → per-team showback.

## Demo Script

10-min Loom:
1. Architecture (1 min)
2. Show Karpenter scaling up (1 min)
3. Show cost dashboard (2 min)
4. Trigger spot interruption (2 min)
5. Watch graceful drain + recovery (2 min)
6. Cost comparison vs on-demand-only (1 min)
7. Lessons (1 min)

## What to Highlight

- 70-80% cost reduction
- < 1% impact on reliability
- Automated lifecycle
- Per-team cost visibility
- Production-quality (PDBs, topology, graceful drain)

## Production Considerations

### Always-On Workloads
- Stateful (databases): keep on-demand
- Critical components (Vault, Istio control plane): on-demand
- Stateless workloads: 80%+ spot OK

### Diversification
- Multi-instance type (more pools = less interruption)
- Multi-AZ (different spot prices)
- Multi-family (avoid simultaneous depletion)

### Watch For
- Cold-start latency (Karpenter ~60s)
- Pre-warm during expected peaks
- High-priority workloads on guaranteed nodes

## Lessons Learned

- Multi-instance-type matters (single type → interruption clustering)
- Graceful shutdown is essential (app must handle SIGTERM)
- PDB prevents cascade (don't drain too many at once)
- Karpenter consolidation surprises (might re-arrange)
- Pre-warm for known peaks

## README Template

```markdown
# Cost-Optimized Spot Platform

## What This Demonstrates
- 80% workload on spot
- 70-76% cost reduction
- Graceful interruption handling
- Cost dashboards

## Demo
- Trigger interruption: watch drain + recovery
- Cost comparison: with vs without spot

## How to Run
[steps]

## What I Learned
[specifics]
```

## Interview Themes

- "Spot strategy for K8s"
- "Karpenter — why over Cluster Autoscaler?"
- "Graceful spot handling"
- "Cost reduction story"
- "When NOT spot?"
