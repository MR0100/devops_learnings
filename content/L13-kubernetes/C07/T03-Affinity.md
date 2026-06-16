# L13/C07/T03 — Node Selectors, Affinity, Anti-Affinity

## Learning Objectives

- Control pod placement
- Apply affinity patterns

## Node Selector (Simple)

```yaml
spec:
  nodeSelector:
    disktype: ssd
    gpu: "true"
```

Pod scheduled only on nodes matching ALL labels.

Limited: equality only.

## Node Affinity (Flexible)

Two types:
- `requiredDuringSchedulingIgnoredDuringExecution`: hard rule
- `preferredDuringSchedulingIgnoredDuringExecution`: soft preference

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64]
        - key: node-role
          operator: NotIn
          values: [master]
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      preference:
        matchExpressions:
        - key: disktype
          operator: In
          values: [ssd]
```

Operators: In, NotIn, Exists, DoesNotExist, Gt, Lt.

## Required vs Preferred

Required: no fit = Pending.
Preferred: schedule anyway, just lower score.

For: strict requirements vs nice-to-have.

## Pod Affinity (Co-Location)

Schedule pods near other pods:
```yaml
affinity:
  podAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: cache
        topologyKey: kubernetes.io/hostname
```

Pod prefers nodes already running `cache` pods.

For: latency (frontend near backend).

## Pod Anti-Affinity (Spread)

Schedule pods AWAY from each other:
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: web
      topologyKey: kubernetes.io/hostname
```

Pods with `app=web` won't be on same node.

For HA: replicas on different nodes.

## topologyKey

Defines "location":
- `kubernetes.io/hostname`: per-node
- `topology.kubernetes.io/zone`: per-AZ
- `topology.kubernetes.io/region`: per-region
- Custom labels

For zone spread:
```yaml
topologyKey: topology.kubernetes.io/zone
```

## Required AntiAffinity Risk

```yaml
requiredDuringSchedulingIgnoredDuringExecution: ...
```

If only 2 nodes match labels + 3 replicas: third Pending forever.

Prefer `preferred` unless certainty needed.

## Topology Spread (Recommended)

Modern alternative; covered T05.

For most: topologySpreadConstraints simpler.

## Common Patterns

### HA Replicas Across Nodes
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: web
      topologyKey: kubernetes.io/hostname
```

3 replicas → 3 different nodes.

### HA Replicas Across Zones
```yaml
topologyKey: topology.kubernetes.io/zone
```

### Cache Near App
```yaml
podAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    podAffinityTerm:
      labelSelector:
        matchLabels:
          app: redis
      topologyKey: kubernetes.io/hostname
```

Better cache locality.

### Avoid Specific Nodes
```yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: node-type
        operator: NotIn
        values: [spot]
```

For: critical workloads not on Spot.

### GPU Nodes
```yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: gpu
        operator: Exists
```

Plus tolerations (covered T04).

## Performance

Affinity rules evaluated by scheduler:
- O(nodes × labels)
- Can slow with many rules + nodes

For huge clusters: simpler rules.

## Node Labels

Set:
```bash
kubectl label nodes my-node tier=production zone=us-east-1a
```

Or via cloud-provider (auto-set):
- `topology.kubernetes.io/zone`
- `topology.kubernetes.io/region`
- `node.kubernetes.io/instance-type`
- `kubernetes.io/arch`
- `kubernetes.io/os`

## Common Mistakes

- Required when preferred suffices (pending pods)
- Wrong topologyKey
- Anti-affinity without enough nodes (Pending)
- AndOr confusion (multiple terms)
- Forgetting matchLabels case

## And vs Or

Multiple matchExpressions in single term: AND.
Multiple nodeSelectorTerms: OR.

```yaml
# AND (both must match)
matchExpressions:
- key: a
  operator: In
  values: [x]
- key: b
  operator: In
  values: [y]

# OR (either term matches)
nodeSelectorTerms:
- matchExpressions:
  - key: a
    operator: In
    values: [x]
- matchExpressions:
  - key: b
    operator: In
    values: [y]
```

Tricky; test.

## DaemonSet Affinity

DaemonSet has its own placement (per-node). Affinity in template restricts.

```yaml
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: gpu
                operator: Exists
```

DaemonSet only on GPU nodes.

## Weight (preferred)

Multiple preferences:
```yaml
preferredDuringSchedulingIgnoredDuringExecution:
- weight: 100
  preference: {...}
- weight: 50
  preference: {...}
```

Scheduler scores; higher weight wins.

## Real-World

### Stateful DB
- Anti-affinity: replicas on different nodes
- Node affinity: storage-optimized instance type
- Anti-affinity zone-level: replicas across AZs

### Web Service
- Topology spread: across AZs
- No specific node affinity

### Cache
- Pod affinity: near consumers (when local cache matters)

## Best Practices

- Use Topology Spread Constraints for spread (newer)
- Preferred > Required when possible
- topologyKey: zone for AZ spread, hostname for node spread
- Node labels stable
- Test in real cluster

## Pod Anti-Affinity vs Topology Spread

| | Anti-affinity | Topology Spread |
|---|---|---|
| Granularity | Binary (yes/no same topo) | Skew-based |
| Flexibility | Less | More |
| Modern | Older | Newer |

For new: Topology Spread.

## Limitations

Anti-affinity evaluated at schedule time. If pods crash + reschedule with different topology, may end up imbalanced over time.

Topology Spread similar but with maxSkew tolerance.

## Operations

```bash
# Add label
kubectl label node my-node tier=production

# Remove label
kubectl label node my-node tier-

# List node labels
kubectl get nodes --show-labels
```

## Inspection

```bash
# Pod's effective placement
kubectl describe pod my-pod | grep Node

# Why Pending?
kubectl describe pod my-pod | grep -A 20 Events
```

## Quick Refs

```yaml
# Node affinity
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: KEY
          operator: In
          values: [VAL]

# Pod anti-affinity
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels: {app: X}
      topologyKey: kubernetes.io/hostname
```

## Interview Prep

**Junior**: "nodeSelector basics."

**Mid**: "Anti-affinity for HA."

**Senior**: "Pod affinity vs topology spread."

**Staff**: "Placement strategy for multi-AZ stateful."

## Next Topic

→ [T04 — Taints & Tolerations](T04-Taints-Tolerations.md)
