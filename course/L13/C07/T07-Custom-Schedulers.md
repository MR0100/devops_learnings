# L13/C07/T07 — Custom Schedulers

## Learning Objectives

- Run multiple schedulers
- Build scheduler plugins

## Why Custom Scheduler

Default scheduler covers most. Custom for:
- ML / HPC workloads (gang scheduling)
- Cost-aware (cheapest spot)
- Custom placement logic
- Specific hardware affinity
- Latency-aware (NUMA, etc.)

## Multi-Scheduler

Multiple schedulers running. Pods select:
```yaml
spec:
  schedulerName: my-custom-scheduler
```

Default scheduler: `default-scheduler`.

## Approaches

### Approach 1: Scheduler Configuration
Tune default scheduler via config:
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
    disabled:
      - name: ImageLocality
```

For most needs.

### Approach 2: Scheduler Plugins (Framework)
Write Go plugins for extension points:
- PreFilter, Filter, PostFilter
- PreScore, Score, NormalizeScore
- Reserve, Permit, PreBind, Bind, PostBind

Compile into scheduler binary.

### Approach 3: Second Scheduler
Run separate scheduler binary alongside default:
- Same code as default but configured differently
- Or completely different implementation

### Approach 4: Webhook / Scheduler Extender
Default scheduler calls your HTTP webhook for filter/score.

Simpler but slower (HTTP overhead).

## Plugin Framework Example

```go
package myplugin

import (
    "context"
    "k8s.io/kubernetes/pkg/scheduler/framework"
)

type MyPlugin struct{}

func (m *MyPlugin) Name() string { return "MyPlugin" }

func (m *MyPlugin) Filter(ctx context.Context, state *framework.CycleState, pod *v1.Pod, nodeInfo *framework.NodeInfo) *framework.Status {
    if nodeInfo.Node().Labels["my-label"] != "approved" {
        return framework.NewStatus(framework.Unschedulable, "not approved")
    }
    return nil
}

// Register
func New(_ runtime.Object, _ framework.Handle) (framework.Plugin, error) {
    return &MyPlugin{}, nil
}
```

Compile + run as scheduler with plugin enabled.

## Scheduler Extender

Older approach. HTTP-based.

```yaml
extenders:
- urlPrefix: "http://my-extender.namespace.svc"
  filterVerb: "filter"
  prioritizeVerb: "prioritize"
  weight: 1
  enableHTTPS: false
  nodeCacheCapable: true
  managedResources:
  - name: "example.com/foo"
```

For each pod: scheduler calls extender filter / prioritize.

Slower than plugins (HTTP per pod) but easier (no Go).

## Use Cases

### Gang Scheduling (HPC)
All pods of a job must schedule simultaneously (else none).

For: distributed training (need all workers at once).

Coscheduler / Volcano implement.

### Bin Packing
Pack pods tightly to minimize node count. Save cost.

Default: balanced. Custom: bin-pack.

### Cost-Aware
Pick cheapest spot instance type. Prefer reserved over on-demand.

### Latency-Aware
NUMA-aware; place pods on specific socket.

### GPU Scheduling
NVIDIA k8s-device-plugin handles GPUs. Custom for advanced (NVLink topology).

### Multi-Cluster
Schedule pod across clusters (Karmada, etc.).

## Volcano

Apache Volcano: batch scheduler:
- Gang scheduling
- Queue management
- DAG support
- Used for ML / HPC

```yaml
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
metadata:
  name: ml-training
spec:
  minAvailable: 4
  schedulerName: volcano
  tasks:
  - replicas: 4
    template: ...
```

Pods schedule together or not at all.

## Coscheduler

K8s sig-scheduling project; gang scheduling:
```yaml
apiVersion: scheduling.x-k8s.io/v1alpha1
kind: PodGroup
metadata:
  name: my-group
spec:
  minMember: 3
```

Pods reference PodGroup.

## YuniKorn

Apache YuniKorn: multi-tenant scheduler:
- Queues
- Hierarchical resource sharing
- Gang scheduling
- For big batch + interactive

For: Spark on K8s, multi-tenant.

## Scheduler Profiles

Multiple profiles in one scheduler:
```yaml
profiles:
- schedulerName: default-scheduler
- schedulerName: latency-aware
  plugins: ...
- schedulerName: bin-packer
  plugins: ...
```

Pods select via schedulerName.

For: workload-specific without separate binary.

## Performance

Default: ~100 pods/sec.

For massive (1000+ pods/sec):
- `percentageOfNodesToScore`: sample subset
- Custom plugins minimal computation

## Testing

```bash
# Run scheduler locally pointing at cluster
./my-scheduler --kubeconfig=~/.kube/config --leader-elect=false
```

Apply pods with schedulerName; observe scheduling.

## Best Practices

- Use default unless real need
- Scheduler config first
- Plugins over extenders (performance)
- One scheduler per workload type if needed
- Leader election for HA
- Monitor scheduler latency
- Audit scheduling decisions

## Production Considerations

- HA (multiple replicas + leader election)
- Resource requests for scheduler itself
- Metrics
- Logs

## When NOT Custom

- Default works
- Karpenter for nodes (modern AWS)
- Multi-scheduler complexity exceeds benefit

For most: stick with default + topology spread + priority.

## Common Mistakes

- Custom scheduler without need
- Forgetting schedulerName (uses default)
- HTTP extender for high-traffic (slow)
- No leader election (multiple deciders)

## Karpenter as Alternative

Karpenter watches pending pods; provisions nodes:
- Different problem space than scheduler
- Doesn't need custom scheduler usually
- Replaces Cluster Autoscaler

## Scheduling Gates (1.27+)

Block pod scheduling until removed:
```yaml
spec:
  schedulingGates:
  - name: waiting-for-batch
```

Scheduler skips pod with gates. External controller removes gate when ready.

For: batch coordination, dependent scheduling.

## Real Scheduler Code

Default scheduler: github.com/kubernetes/kubernetes/pkg/scheduler.

Plugins: github.com/kubernetes/kubernetes/pkg/scheduler/framework/plugins.

For learning + customization.

## Mature Schedulers

- Volcano (batch, HPC, ML)
- YuniKorn (multi-tenant, Spark)
- Coscheduler (gang)
- Yet-another-scheduler (cost-aware)

Pre-built; install via Helm.

## Quick Refs

```bash
# List schedulers (look at pods)
kubectl get pods -n kube-system | grep scheduler

# Pod schedulerName
kubectl get pod my-pod -o jsonpath='{.spec.schedulerName}'

# Volcano
helm install volcano volcano/volcano
```

## Interview Prep

**Mid**: "When use custom scheduler."

**Senior**: "Plugin framework structure."

**Staff**: "Multi-tenant batch scheduling."

## Next Topic

→ Move to [L13/C08 — Autoscaling](../C08/README.md)
