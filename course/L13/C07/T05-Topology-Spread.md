# L13/C07/T05 — Topology Spread Constraints

## Learning Objectives

- Use TopologySpreadConstraints
- Replace anti-affinity

## TopologySpreadConstraints

Modern API for even distribution across topology domains:
```yaml
spec:
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: web
```

## Key Fields

- **maxSkew**: max difference in pod count between domains
- **topologyKey**: domain (zone, node, region)
- **whenUnsatisfiable**: action if can't satisfy
- **labelSelector**: which pods to count

## maxSkew

Difference between most-loaded and least-loaded domain:
- maxSkew: 1 → balanced
- maxSkew: 2 → tolerate slight imbalance

For 6 replicas across 3 zones, maxSkew=1: 2-2-2 (balanced) or 3-2-1 (skew 2; violates).

## topologyKey

Common:
- `topology.kubernetes.io/zone`: AZ spread (HA)
- `kubernetes.io/hostname`: per-node spread
- `topology.kubernetes.io/region`: cross-region (multi-cluster ish)

## whenUnsatisfiable

### DoNotSchedule
Hard constraint. Pod Pending if can't satisfy.

### ScheduleAnyway
Soft. Schedule but try best.

Default: DoNotSchedule.

For most HA: ScheduleAnyway. Avoid hard Pending.

## Example: HA Across AZs

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: web
```

6 replicas across 3 AZs: 2-2-2 evenly.

## Example: Spread Across Nodes

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: web
```

Replicas on different nodes (when possible).

## Combined

Two constraints:
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: ScheduleAnyway
  labelSelector: {matchLabels: {app: web}}
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
  labelSelector: {matchLabels: {app: web}}
```

Spread across zones AND nodes within each zone.

## vs Anti-Affinity

| | Anti-Affinity | Topology Spread |
|---|---|---|
| Granularity | Binary | Skew-tolerant |
| Multiple domains | Hard | Easy |
| Pending if can't | requiredYes | configurable |
| Modern | Older | Newer |

Topology Spread more flexible.

## Cluster Default Constraints

Set via scheduler config:
```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
- pluginConfig:
  - name: PodTopologySpread
    args:
      defaultConstraints:
      - maxSkew: 3
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: ScheduleAnyway
      defaultingType: List
```

All pods without explicit constraints get defaults.

## minDomains (1.27+)

Minimum domains required:
```yaml
- maxSkew: 1
  minDomains: 3
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
```

Pod requires at least 3 zones available.

For: enforce multi-AZ deployment.

## matchLabelKeys (1.27+)

Spread by template hash too:
```yaml
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  matchLabelKeys: [pod-template-hash]
```

Different ReplicaSet versions don't conflict (during rolling update).

## nodeAffinityPolicy / nodeTaintsPolicy

Control what pods/nodes are considered:
```yaml
- maxSkew: 1
  ...
  nodeAffinityPolicy: Honor   # consider only nodes matching pod's nodeSelector
  nodeTaintsPolicy: Honor      # consider only nodes pod tolerates
```

More precise.

## Real-World

### Stateless Web (HA)
3 replicas; 3 AZs:
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels: {app: web}
```

1 per AZ guaranteed.

### Stateful (DB)
StatefulSet replicas in different zones:
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels: {app: db}
```

For Postgres replicas; cross-AZ.

### Heavy Workload
Spread across nodes (don't cram):
```yaml
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
```

## DoNotSchedule Risk

For 3 replicas / 2 zones, maxSkew=1, DoNotSchedule:
- 2 in zone A, 1 in zone B: OK (skew 1)
- 3rd replica: depends — could be either; if both zones already 2-1, third may go to 2-2 (skew 0).

For 3 replicas / 2 zones: 2-1 valid (skew 1).
For 4 replicas / 2 zones: 2-2 ideal; if not possible (e.g., insufficient capacity), Pending.

## minDomains Risk

minDomains > available zones: pods stay Pending.

For: deliberate enforcement.

## Default vs Per-Pod

Per-pod constraints override cluster defaults.

For specific apps: override defaults.

## Best Practices

- TopologySpread for AZ HA
- maxSkew=1 for balanced
- ScheduleAnyway unless strict
- Combine zone + node spread
- Document why
- minDomains for compliance (multi-AZ enforce)

## Common Mistakes

- DoNotSchedule everywhere (Pending issues)
- maxSkew too low (rigid)
- labelSelector mismatch (counts wrong pods)
- Forgetting node labels (zones not labeled)

## Performance

For huge clusters: many spread constraints can slow scheduling.

Tune scheduler if needed.

## Inspection

```bash
# Where are pods?
kubectl get pods -l app=web -o wide

# Per zone (using node label)
kubectl get pods -l app=web -o json | jq '.items[] | .spec.nodeName' | while read n; do
  kubectl get node $n -o jsonpath='{.metadata.labels.topology\.kubernetes\.io/zone}{"\n"}'
done | sort | uniq -c
```

## Combining with Anti-Affinity

You can combine. But topology spread usually sufficient.

If both: rules ANDed. Pending more likely.

For: complex requirements.

## Use With Karpenter

Karpenter respects topology spread:
- Provisions nodes to satisfy spread
- Across zones if needed

Plus zones in NodePool requirements:
```yaml
requirements:
- key: topology.kubernetes.io/zone
  operator: In
  values: [us-east-1a, us-east-1b, us-east-1c]
```

## DR Patterns

For multi-region: not topology spread (intra-cluster). Cross-cluster needs:
- Multi-cluster routing (mesh)
- Cluster API / Karmada
- Active-active / active-passive

## Quick Refs

```yaml
# Basic HA across zones
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels: {app: web}

# Strict multi-AZ
- maxSkew: 1
  minDomains: 3
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
```

## Interview Prep

**Mid**: "TopologySpread vs anti-affinity."

**Senior**: "HA Deployment design."

**Staff**: "Multi-AZ enforcement."

## Next Topic

→ [T06 — Priority & Preemption](T06-Priority-Preemption.md)
