# L13/C08/T03 — Cluster Autoscaler

## Learning Objectives

- Use Cluster Autoscaler
- Configure for cost / availability

## Cluster Autoscaler (CA)

Adds/removes nodes based on pod demand.

When pods Pending (resources): adds node.
When nodes idle: removes (to save cost).

## Architecture

CA watches:
- Pending pods (unschedulable)
- Node utilization (CPU/memory)

Acts:
- Increase ASG / node pool desired count
- Or drain + remove nodes

## ASG Integration (AWS)

CA scales Auto Scaling Groups:
```yaml
spec:
  containers:
  - name: cluster-autoscaler
    command:
    - ./cluster-autoscaler
    - --cloud-provider=aws
    - --nodes=2:10:my-asg
```

Per ASG: min, max, current.

## Node Groups

CA manages "node groups" (ASG, Managed Node Group, etc.):
- Each group: instance type + AZ + config
- CA picks group fitting pending pod

For heterogeneous cluster: many node groups.

## When Add Node

1. Pod Pending (no node fits)
2. CA simulates: which node group could fit?
3. Scale up node group

For: handle pending pods.

## When Remove Node

1. Node utilization low for X minutes (default 10 min)
2. Pods on node can be rescheduled elsewhere
3. PDB respected
4. Drain + terminate

For: cost optimization.

## Scale-Down Behavior

CA evaluates each node:
- Are there pods? Can they move?
- Is utilization < threshold?
- Have no replicasets that can't shrink?

If yes for all: drain + remove.

## Limits

- 1000 nodes typical max
- 5-min scale-up latency
- Scale-down delay configurable

For: large clusters, consider Karpenter.

## Configuration

```yaml
# values.yaml (Helm)
autoDiscovery:
  clusterName: my-cluster
awsRegion: us-east-1
extraArgs:
  scale-down-delay-after-add: 10m
  scale-down-unneeded-time: 10m
  skip-nodes-with-local-storage: false
```

## Scale-Down Disabled Annotation

```yaml
metadata:
  annotations:
    cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
```

CA won't remove node with this pod.

For: stateful, important workloads.

## Node Group Discovery

Auto-discovery via tags:
- AWS: ASG tags `k8s.io/cluster-autoscaler/enabled: true`
- GCP: similar
- Azure: similar

CA finds matching ASGs.

## Spot Integration

For Spot ASGs: CA + Spot termination handler.

When Spot reclaimed: handler drains; CA replaces.

## Mixed Node Groups

```yaml
extraArgs:
  expander: priority   # or least-waste, random, most-pods
```

Priority: order node groups; CA prefers first.

For: prefer on-demand fallback to Spot.

## Cost Optimization

CA helps reduce idle nodes:
- Scale up only when needed
- Scale down after idle

Plus:
- Spot for tolerant workloads
- Right-sized node groups
- Multiple node groups for instance variety

## Limitations

- Per-ASG scaling (not arbitrary instance choice)
- 10-min scale-down delay (default)
- Cool-down between scales
- Doesn't consolidate (move pods to fit fewer nodes)

For consolidation: Karpenter (covered T04).

## Karpenter vs CA

| | Cluster Autoscaler | Karpenter |
|---|---|---|
| Provisioner | ASG-based | Per-pod optimal |
| Scale-up speed | Minutes | Seconds |
| Instance choice | Pre-defined | Dynamic |
| Spot management | OK | Better |
| Consolidation | No | Yes |
| Multi-cloud | Yes | AWS-focused (mostly) |

For EKS: Karpenter recommended.
For others: CA still valid.

## Install (EKS)

```bash
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --set autoDiscovery.clusterName=my-cluster \
  --set awsRegion=us-east-1 \
  --set rbac.serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="arn:aws:iam::123:role/CAroleARN"
```

IAM role required (IRSA).

## IAM Permissions

CA needs:
```json
[
  "autoscaling:DescribeAutoScalingGroups",
  "autoscaling:DescribeAutoScalingInstances",
  "autoscaling:DescribeLaunchConfigurations",
  "autoscaling:SetDesiredCapacity",
  "autoscaling:TerminateInstanceInAutoScalingGroup",
  "ec2:DescribeInstanceTypes"
]
```

For: scale ASGs.

## Monitoring

```bash
kubectl logs -n kube-system cluster-autoscaler-xxx
```

Logs:
- Pending pods detected
- Scale-up decisions
- Scale-down decisions

Metrics:
- `cluster_autoscaler_unschedulable_pods_count`
- `cluster_autoscaler_nodes_count`
- `cluster_autoscaler_scale_down_in_cooldown`

## Common Issues

### Pods Stuck Pending; CA Not Scaling
- ASG at max
- Wrong instance type for pod
- Taints / tolerations mismatch
- Pod can't schedule on any node group

```bash
kubectl describe pod <pending>
# Events show why
```

### Nodes Not Scaling Down
- Pods without `safe-to-evict`
- Local volumes
- PDB blocks
- System pods present

### CA Crashes
Check logs; usually IAM permissions or ASG access.

## Best Practices

- Multiple node groups (heterogeneous)
- Spot + on-demand mix
- PDB on important workloads
- safe-to-evict annotations carefully
- Monitor CA logs
- Set sensible cooldowns

## Common Mistakes

- Single node group (no flexibility)
- No PDB (pods evicted aggressively)
- ASG limits hit (CA can't scale)
- safe-to-evict on everything (CA can't scale down)
- Wrong IAM permissions

## Pod Priority + CA

CA prefers Pending high-priority pods. For:
- Critical pods get nodes first
- Low-priority pods wait

## Capacity Planning

With CA:
- Baseline = min ASG capacity
- Burst = scale up
- Idle = scale down

Buffer:
- Keep 10-20% headroom for fast scheduling
- Avoid 100% utilization (pod start delays)

## Multi-Region

CA per cluster; not cross-region.

For multi-region: cross-cluster orchestration (Cluster API, Karmada).

## Test

Test scale-up:
```bash
# Create burst Deployment
kubectl scale deployment burst --replicas=100
# Watch
kubectl get nodes -w
```

Test scale-down:
```bash
# Reduce
kubectl scale deployment burst --replicas=0
# Wait 10+ min
kubectl get nodes -w   # nodes removed
```

## Quick Refs

```bash
# CA pods
kubectl get pods -n kube-system | grep cluster-autoscaler

# Logs
kubectl logs -n kube-system cluster-autoscaler-xxx

# Annotate pod safe-to-evict false
kubectl annotate pod my-pod cluster-autoscaler.kubernetes.io/safe-to-evict=false
```

## Interview Prep

**Mid**: "What CA does."

**Senior**: "CA vs Karpenter."

**Staff**: "Multi-tenant cluster scaling."

## Next Topic

→ [T04 — Karpenter (Next-Gen Node Provisioning)](T04-Karpenter.md)
