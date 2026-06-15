# L13/C01/T04 — The Scheduler Internals

## Learning Objectives

- Understand scheduler decisions
- Use plugins / configurations

## Scheduler Job

Pick a node for each unscheduled pod.

```
Unscheduled pod (no spec.nodeName)
    ↓
Scheduler loop
    ↓
Filter eligible nodes
    ↓
Score nodes
    ↓
Pick highest-scored
    ↓
Bind pod (write spec.nodeName)
    ↓
kubelet picks up; runs
```

## Filter (Predicates)

Rules deciding can-this-node-fit:

### Resources
- Allocatable CPU/RAM ≥ pod requests
- Per node

### Volume Restrictions
- Volume types available
- AZ matches

### Taints / Tolerations
- Pod must tolerate node's taints

### Node Affinity
- Match node selector / affinity rules

### Pod Affinity / Anti-Affinity
- Co-locate / repel from other pods

### Existing Topology
- TopologySpreadConstraints

If no node passes: Pod stays Pending. Event: "0/N nodes are available."

## Score

Among filtered nodes, rank:

### Scoring Plugins
- **NodeResourcesBalancedAllocation**: balance CPU/RAM usage across nodes
- **NodeResourcesFit**: prefer least or most allocated (configurable)
- **InterPodAffinity**: pods prefer / avoid each other's nodes
- **PodTopologySpread**: spread across zones
- **ImageLocality**: prefer node with image already cached

Each plugin scores 0-100; weighted sum.

## Plugin Framework

```
Sort      → Order pending pods
Filter    → Filter nodes
Score     → Rank nodes
Reserve   → Reserve resources
Permit    → Approve / wait / reject binding
PreBind   → Volume mount, etc.
Bind      → Write to API
PostBind  → Cleanup
```

Each extension point can have multiple plugins.

## Configuring Scheduler

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
- schedulerName: default-scheduler
  plugins:
    score:
      enabled:
      - name: NodeResourcesBalancedAllocation
      - name: PodTopologySpread
        weight: 5
```

For: tune defaults, custom scheduling.

## Multiple Schedulers

```yaml
spec:
  schedulerName: my-custom-scheduler
```

Run another scheduler binary; handles pods with that name.

For: domain-specific (HPC, GPU-aware, etc.).

## Affinity / Anti-Affinity

### Node Affinity
Pod prefers / requires node labels:
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: instance-type
          operator: In
          values: [m5.large]
```

### Pod Affinity
Pods near specific other pods:
```yaml
podAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    podAffinityTerm:
      labelSelector:
        matchLabels:
          app: cache
      topologyKey: kubernetes.io/hostname
```

### Pod Anti-Affinity
Pods spread (replicas on different nodes):
```yaml
podAntiAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
  - labelSelector:
      matchLabels:
        app: web
    topologyKey: kubernetes.io/hostname
```

Common for: HA (don't co-locate replicas).

## Topology Spread

Newer + recommended:
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: web
```

Even distribution across zones.

## Taints / Tolerations

Repel pods unless tolerated:

```bash
kubectl taint nodes gpu-1 dedicated=ml:NoSchedule
```

Pod tolerates:
```yaml
tolerations:
- key: dedicated
  operator: Equal
  value: ml
  effect: NoSchedule
```

Effects:
- **NoSchedule**: don't schedule
- **PreferNoSchedule**: prefer not to
- **NoExecute**: evict running pods (if not tolerated)

For: dedicated nodes (GPU, special hardware).

## Priority Classes

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
```

Pod:
```yaml
priorityClassName: high-priority
```

Higher priority pod:
- Scheduled first
- Can preempt lower-priority pods (evict to make room)

For: critical workloads.

## Preemption

When high-priority pod can't be scheduled:
- Scheduler finds lower-priority pods to evict
- Sends SIGTERM (with grace period)
- New pod scheduled

Pre-emption + PDB: PDB checked first; preempt only if doesn't violate.

## Resource Quotas (Per Namespace)

Doesn't directly affect scheduling, but limits what's possible:
```yaml
kind: ResourceQuota
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    pods: "20"
```

Namespace can't exceed.

## Scheduling Performance

Default: ~100 pods/sec scheduled per scheduler.

For huge: tune `percentageOfNodesToScore` (sample subset for scoring at scale).

## Custom Scheduler

Write your own scheduler in Go:
- Watch pods
- For each: pick node
- Call API Server Bind

```go
binding := &v1.Binding{
  ObjectMeta: metav1.ObjectMeta{Name: pod.Name},
  Target: v1.ObjectReference{Kind: "Node", Name: chosenNode},
}
clientset.CoreV1().Pods(pod.Namespace).Bind(ctx, binding, metav1.CreateOptions{})
```

For: HPC, machine learning, custom needs.

## Pod Scheduling Gates (1.27+)

Block pod scheduling until external system removes gate:
```yaml
spec:
  schedulingGates:
  - name: waiting-for-external-system
```

Scheduler skips until gates cleared.

For: external coordination, batch scheduling.

## Specific Scheduler Pipeline

```
1. PrePreFilter / PreFilter:
   - Validate; compute state
2. Filter:
   - Each plugin runs; node either passes or fails
3. PostFilter (if all filtered):
   - Preemption logic
4. PreScore:
   - Compute state for scoring
5. Score:
   - Each plugin scores
6. NormalizeScore:
   - Normalize to 0-100
7. Reserve:
   - Reserve resources on node
8. Permit:
   - Approve, wait, or reject (custom for batch)
9. PreBind:
   - Volume setup
10. Bind:
    - Write to API
11. PostBind:
    - Cleanup
```

Custom plugins implement these extension points.

## Common Issues

### Pod Pending
```bash
kubectl describe pod <p>
```
Events show why:
- "0/3 nodes available: 3 insufficient cpu"
- "0/3 nodes: 1 didn't match node selector, 2 had taint"

### Unbalanced
All pods on one node. Cause:
- No pod anti-affinity
- No topology spread

Fix: spread constraints.

### Slow Scheduling
- Big clusters: tune `percentageOfNodesToScore`
- Custom plugins slow

## Best Practices

- Resource requests (scheduler needs to know)
- Anti-affinity / spread for HA
- Taints for special nodes
- Priority for tier-0
- Topology spread by zone
- PDB for safety

## Common Mistakes

- No requests (anything can fit)
- All on one node (no spread)
- Wrong topology key
- Forgetting whenUnsatisfiable
- Priorities everywhere (defeats)

## Debugging

```bash
# Pending reasons
kubectl describe pod <p> | grep -A 20 Events

# Scheduler logs
kubectl logs -n kube-system kube-scheduler-master-1

# Detail
kubectl get events --field-selector reason=FailedScheduling
```

## Karpenter (Modern AWS)

Provisions nodes per pod needs:
- Watch pending pods
- Provision optimal instance type (not ASG-bound)
- Spot-aware
- Consolidation

Replaces Cluster Autoscaler. Faster + better fit.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
spec:
  template:
    spec:
      requirements:
      - key: karpenter.k8s.aws/instance-category
        operator: In
        values: [m, c, r]
```

## Quick Refs

```bash
# Why is a pod Pending? (scheduler writes the reason as an event)
kubectl describe pod <pod> | sed -n '/Events:/,$p'
kubectl get events --field-selector reason=FailedScheduling --sort-by=.lastTimestamp

# Where did it land, and what's free on each node?
kubectl get pod <pod> -o wide
kubectl describe node <node> | grep -A6 'Allocated resources'

# Inspect / override placement
kubectl get pod <pod> -o jsonpath='{.spec.nodeName}'
kubectl taint nodes <node> key=value:NoSchedule       # add a taint
kubectl label nodes <node> disktype=ssd               # for nodeSelector/affinity

# Run a second scheduler-named pod
#   spec.schedulerName: my-scheduler
```

| Phase | What it does | Common failure event |
|---|---|---|
| Filter (predicates) | Eliminate nodes that *can't* fit | `0/N nodes available: insufficient cpu/memory`, taint, affinity |
| Score (priorities) | Rank the survivors | (no failure; picks best) |
| Bind | Write `spec.nodeName` | bind conflict (rare) |

Mnemonic for `FailedScheduling`: **resources, taints, affinity, volumes/topology, ports** — check those five first.

## Interview Prep

**Mid**: "Affinity vs anti-affinity."

**Senior**: "Pod preemption flow."

**Staff**: "Custom scheduler design."

## Next Topic

→ [T05 — etcd Deep Dive](T05-etcd.md)
