# L13/C07/T04 — Taints & Tolerations

## Learning Objectives

- Use taints for node isolation
- Configure tolerations correctly

## Taints

Mark nodes so pods avoid them.

```bash
kubectl taint nodes gpu-1 dedicated=ml:NoSchedule
```

Pods can't schedule on `gpu-1` unless they tolerate.

## Tolerations

```yaml
spec:
  tolerations:
  - key: dedicated
    operator: Equal
    value: ml
    effect: NoSchedule
```

Pod can schedule on tainted nodes.

## Effects

| Effect | Behavior |
|---|---|
| NoSchedule | Don't schedule new pods unless tolerated |
| PreferNoSchedule | Prefer not to schedule |
| NoExecute | Don't schedule + evict existing pods (without toleration) |

## Toleration Operators

```yaml
# Exact match
- key: dedicated
  operator: Equal
  value: ml
  effect: NoSchedule

# Exists (any value)
- key: dedicated
  operator: Exists
  effect: NoSchedule

# Tolerate everything
- operator: Exists
```

## Use Cases

### Dedicated Nodes
Taint:
```bash
kubectl taint nodes gpu-1 dedicated=ml:NoSchedule
```

Only ML pods (with toleration) schedule on gpu-1.

### GPU Nodes
```bash
kubectl taint nodes gpu-1 nvidia.com/gpu=present:NoSchedule
```

GPU pods tolerate; non-GPU pods avoid.

### Control Plane Isolation
Master nodes tainted by default:
```
node-role.kubernetes.io/control-plane:NoSchedule
```

User pods avoid; system components tolerate.

### Spot / Preemptible
```bash
kubectl taint nodes spot-1 spot=true:NoSchedule
```

Only tolerant workloads on Spot.

## NoExecute

Evicts non-tolerating pods:
```bash
kubectl taint nodes problem-1 maintenance=true:NoExecute
```

All non-tolerant pods evicted.

For: draining, maintenance.

## tolerationSeconds

How long pod tolerates before eviction:
```yaml
- key: node.kubernetes.io/not-ready
  operator: Exists
  effect: NoExecute
  tolerationSeconds: 300
```

Pod tolerates not-ready for 5 min before evicted.

K8s auto-adds:
- `node.kubernetes.io/not-ready` (5 min default)
- `node.kubernetes.io/unreachable` (5 min default)

## Built-in Taints (Auto)

K8s adds based on node conditions:
- `node.kubernetes.io/not-ready`
- `node.kubernetes.io/unreachable`
- `node.kubernetes.io/memory-pressure`
- `node.kubernetes.io/disk-pressure`
- `node.kubernetes.io/network-unavailable`
- `node.kubernetes.io/unschedulable`

Pods auto-tolerate some (e.g., DaemonSets tolerate most).

## Affinity vs Taints

Different mechanisms:
- **Affinity**: pod chooses node (positive)
- **Taints**: node repels pods (negative)

Combine:
- Taint GPU nodes (no random pods)
- ML pods: toleration + node affinity

```yaml
tolerations:
- key: nvidia.com/gpu
  effect: NoSchedule

affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: nvidia.com/gpu
          operator: Exists
```

Both: tolerate AND prefer GPU nodes.

## Remove Taint

```bash
kubectl taint nodes gpu-1 dedicated=ml:NoSchedule-
```

Suffix `-` removes.

## Node Drain

```bash
kubectl drain my-node --ignore-daemonsets
```

Internally:
- Cordons node (taints with `node.kubernetes.io/unschedulable:NoSchedule`)
- Evicts pods (NoExecute behavior)
- DaemonSet pods stay (ignored)

For maintenance.

## Uncordon

```bash
kubectl uncordon my-node
```

Removes unschedulable taint.

## DaemonSet Tolerations

DaemonSets often `tolerations: [operator: Exists]` to land on every node.

```yaml
tolerations:
- operator: Exists
```

For: monitoring, logging agents everywhere.

## Multiple Taints

Node can have multiple:
```bash
kubectl taint nodes node-1 dedicated=ml:NoSchedule gpu=true:NoSchedule
```

Pod must tolerate ALL.

## Tolerating Without Specific Effect

```yaml
- key: dedicated
  operator: Equal
  value: ml
# No effect specified: tolerates ANY effect for this key
```

Wider tolerance.

## Common Patterns

### Heterogeneous Cluster
- General nodes (no taint)
- GPU nodes (`gpu=true:NoSchedule`)
- High-mem nodes (`type=highmem:NoSchedule`)
- Spot nodes (`spot=true:NoSchedule`)

Per-workload: toleration + node affinity.

### Maintenance Window
```bash
kubectl taint nodes my-node maintenance=true:NoExecute
sleep 30   # wait for evictions
# perform maintenance
kubectl taint nodes my-node maintenance:NoExecute-
```

### Graceful Drain
```bash
kubectl drain my-node --grace-period=300 --ignore-daemonsets
```

Wait for graceful shutdown of pods.

## Spot Instance Pattern

Spot nodes tainted:
```bash
kubectl taint nodes spot-1 spot=true:NoSchedule
```

Tolerant workloads (batch, dev):
```yaml
tolerations:
- key: spot
  effect: NoSchedule
```

Critical: untolerated; stays on on-demand.

## Karpenter Taints

Karpenter applies taints based on NodePool config. Pods explicitly tolerate.

## Best Practices

- Taint specialty nodes
- Built-in tolerations for system pods
- NoExecute for evacuation
- DaemonSets tolerate all
- Document taint conventions

## Common Mistakes

- Taint without toleration on user pods (Pending)
- NoExecute without grace
- Tolerating everything (defeats purpose)
- Untainting wrong nodes

## Cordoned vs Tainted

- Cordoned: `unschedulable=true` field set; old way
- Modern: taint `node.kubernetes.io/unschedulable:NoSchedule`

`kubectl cordon` does both.

## Inspection

```bash
# Node taints
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

# Specific
kubectl describe node my-node | grep Taints

# Pod tolerations
kubectl get pod my-pod -o jsonpath='{.spec.tolerations}'
```

## Examples

### Critical Workload Stays
```yaml
tolerations:
- key: node.kubernetes.io/unschedulable
  effect: NoSchedule
  operator: Exists
```

Pod tolerates cordoned nodes. For DaemonSets typically.

### Tolerate All
```yaml
tolerations:
- operator: Exists
```

Schedule anywhere. For monitoring DaemonSets.

### Wait Before Eviction
```yaml
tolerations:
- key: node.kubernetes.io/not-ready
  effect: NoExecute
  tolerationSeconds: 600
```

Tolerate not-ready 10 min before evicted.

## Drain Workflow

For node maintenance:
1. `kubectl cordon my-node` (no new pods)
2. `kubectl drain my-node --ignore-daemonsets --delete-emptydir-data`
3. Wait
4. Patch / reboot
5. `kubectl uncordon my-node`

PDB respected during drain (waits if would violate).

## Spot Termination Handler

For Spot interruption (AWS 2-min warning):
- aws-node-termination-handler watches
- Cordons node
- Drains pods
- Graceful

## Quick Refs

```bash
# Add taint
kubectl taint nodes my-node key=value:NoSchedule

# Remove
kubectl taint nodes my-node key=value:NoSchedule-

# All taints on node
kubectl get node my-node -o jsonpath='{.spec.taints}'

# Drain
kubectl drain my-node --ignore-daemonsets

# Uncordon
kubectl uncordon my-node
```

## Interview Prep

**Mid**: "Taint vs nodeSelector."

**Senior**: "GPU node strategy."

**Staff**: "Heterogeneous cluster taints + Karpenter."

## Next Topic

→ [T05 — Topology Spread Constraints](T05-Topology-Spread.md)
