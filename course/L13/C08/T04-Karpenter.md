# L13/C08/T04 — Karpenter (Next-Gen Node Provisioning)

## Learning Objectives

- Use Karpenter
- Configure NodePools

## Karpenter

AWS-built node provisioner. Modern replacement for Cluster Autoscaler.

Advantages:
- Per-pod optimal instance
- Faster scale-up (seconds)
- Bin-packing / consolidation
- Spot-aware (better than CA)
- No ASG dependency

## Install (EKS)

```bash
helm install karpenter karpenter/karpenter \
  -n karpenter \
  --create-namespace \
  --set settings.clusterName=my-cluster \
  --set settings.interruptionQueue=karpenter-queue \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="arn:aws:iam::123:role/KarpenterRole"
```

Plus IAM role with permissions.

## NodePool

Defines what Karpenter can provision:
```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
      - key: karpenter.sh/capacity-type
        operator: In
        values: [spot, on-demand]
      - key: karpenter.k8s.aws/instance-category
        operator: In
        values: [m, c, r]
      - key: karpenter.k8s.aws/instance-generation
        operator: Gt
        values: ["3"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  limits:
    cpu: 1000
    memory: 1000Gi
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
    expireAfter: 720h
```

Karpenter picks among matching instance types.

## EC2NodeClass

Defines launch config:
```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2023
  subnetSelectorTerms:
  - tags:
      karpenter.sh/discovery: my-cluster
  securityGroupSelectorTerms:
  - tags:
      karpenter.sh/discovery: my-cluster
  role: KarpenterNodeRole
  userData: |
    #!/bin/bash
    ...
```

For: AMI, subnets, SGs, instance profile.

## Provisioning Flow

1. Pod Pending (unschedulable)
2. Karpenter sees pod
3. Computes ideal instance (based on requirements)
4. Calls EC2 RunInstances
5. Node joins cluster
6. Pod scheduled
7. ~30-60s total

vs CA: 3-5 min typically.

## Consolidation

When nodes underutilized:
- Karpenter computes if pods can fit on fewer nodes
- Drains + replaces with cheaper/smaller

Aggressive cost optimization.

```yaml
disruption:
  consolidationPolicy: WhenUnderutilized
  consolidateAfter: 30s
```

## Spot Integration

```yaml
requirements:
- key: karpenter.sh/capacity-type
  operator: In
  values: [spot]
```

Karpenter picks Spot pools likely to last.

Plus aws-node-termination-handler: graceful drain on Spot interruption.

## Multi-Capacity-Type

```yaml
- key: karpenter.sh/capacity-type
  operator: In
  values: [spot, on-demand]
```

Spot first; on-demand fallback if Spot unavailable.

## Instance Selection

Karpenter picks from matching instances + cheapest:
- Spot diversity (avoid all in one pool)
- Right-size for pod
- Avoid recently-interrupted Spot pools

## NodePool Weight

For multiple NodePools:
```yaml
spec:
  weight: 10   # higher = preferred
```

Karpenter prefers high-weight NodePool.

For tiered: Spot first; on-demand backup.

## Limits

```yaml
limits:
  cpu: 1000
  memory: 1000Gi
```

Cap total resources Karpenter provisions.

For budget control.

## Disruption Controls

### Consolidation
- `WhenUnderutilized`: aggressive (replace)
- `WhenEmpty`: only empty nodes
- Manual: never auto-consolidate

### Expiration
```yaml
expireAfter: 720h   # 30 days
```

Force replace nodes; pick up new AMI.

For: security patches.

### Drift
Karpenter detects when node config drifts (e.g., NodePool updated). Replaces.

## Budgets

```yaml
disruption:
  budgets:
  - nodes: "10%"
  - nodes: "5"
    schedule: "0 9 * * mon-fri"
    duration: 8h
```

Limit disruption rate. Business hours: less aggressive.

## NodeClaim

Karpenter's intermediate object:
```bash
kubectl get nodeclaim
```

Represents "I want a node like this." Karpenter creates EC2.

## When Karpenter

- EKS (primary target)
- Want fast scaling
- Want cost optimization
- Mixed workloads

## When NOT Karpenter

- Non-AWS (limited; growing)
- Strict ASG requirements
- Compliance forbids dynamic instances

## Best Practices

- Multiple NodePools (different tiers)
- Spot for tolerant workloads
- Anti-affinity respected
- Consolidation enabled (cost)
- expireAfter for security
- Limits on each NodePool
- Monitor

## Common Mistakes

- One NodePool only (no flexibility)
- No instance requirements (Karpenter picks expensive)
- Consolidation off (waste)
- Misconfigured SGs / subnets

## Real-World

### Mixed Tier
```yaml
# NodePool: critical (on-demand only)
weight: 100
requirements:
- key: karpenter.sh/capacity-type
  values: [on-demand]
```

```yaml
# NodePool: standard (mostly spot)
weight: 50
requirements:
- key: karpenter.sh/capacity-type
  values: [spot, on-demand]
```

Critical pods on first NodePool; rest on second.

## Cost Savings

Typical:
- vs CA: 30-50% less waste
- + Spot: 60-80% less
- + Consolidation: more

Real customers report 40-70% node cost reduction with Karpenter.

## Multi-Cloud

Karpenter primarily AWS. Other providers:
- AKS Karpenter Provider (Azure; preview)
- GKE doesn't have Karpenter; Cluster Autoscaler typical (with native consolidation)

## Configuration Hot-Reload

NodePool updated → Karpenter applies to new nodes. Existing: marked drift; replaced over time.

For: pick up new instance types, AMI updates.

## Integration with Spot

aws-node-termination-handler:
- Watches Spot interruption notice
- Cordons + drains node
- Karpenter provisions replacement
- Graceful failover

## Monitoring

Karpenter metrics:
- `karpenter_nodes_created_total`
- `karpenter_nodes_terminated_total`
- `karpenter_pods_pending_total`

Dashboard: provisioning rate, capacity, costs.

## IAM Setup

Karpenter needs:
- EC2 launch / terminate
- IAM PassRole (for node IAM role)
- Pricing API
- SQS (for interruption queue)

IRSA for Karpenter pod.

## Quick Refs

```bash
# NodePools
kubectl get nodepool

# NodeClaims (provisioning)
kubectl get nodeclaim

# Logs
kubectl logs -n karpenter karpenter-xxx

# Force consolidation
kubectl annotate node my-node karpenter.sh/voluntary-disruption=eligible
```

## Interview Prep

**Mid**: "Karpenter vs CA."

**Senior**: "Karpenter NodePool design."

**Staff**: "Cost optimization with Karpenter."

## Next Topic

→ [T05 — KEDA (Event-Driven Autoscaling)](T05-KEDA.md)
