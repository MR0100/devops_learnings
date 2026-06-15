# L13/C07/T01 — Requests & Limits

## Learning Objectives

- Set requests + limits correctly
- Understand cgroup enforcement

## Requests vs Limits

### Requests
What pod is guaranteed:
- Scheduler reserves on node
- Pod always gets at least this

### Limits
What pod can use max:
- CPU: throttled at limit
- Memory: OOM-killed if exceeded

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

## Units

### CPU
- `1` = 1 vCPU
- `500m` = 0.5 vCPU (millicores)
- `100m` = 0.1 vCPU

### Memory
- `Ki`, `Mi`, `Gi` = binary (1024)
- `K`, `M`, `G` = decimal (1000)

Use `Mi`/`Gi` for clarity.

## Scheduler Behavior

Scheduler sums requests; checks against node Allocatable.

Pod fits if sum(requests on node) + pod.requests ≤ node.allocatable.

Limits NOT considered for scheduling.

## CPU Throttling

CFS (Completely Fair Scheduler) throttles based on:
- Period: 100ms (default)
- Quota: based on limit

CPU limit 1 = 100ms quota in 100ms period. If used 100ms in <100ms window → throttled until next.

For multi-threaded apps (Java, Go): throttling causes p99 latency spikes.

## CPU Limit Trap

CPU limit doesn't mean "max CPU" — it's per-period quota.

Java app with 8 threads:
- All can run simultaneously
- If sum 100ms in 12ms → throttled 88ms
- p99 latency huge

Common advice: don't set CPU limits. Just requests.

```yaml
requests:
  cpu: "500m"
# no limits.cpu
```

Pod can use any spare CPU; only throttled when no spare. Better p99.

## Memory Limit

Memory enforced strictly:
- App allocates > limit → OOM killed
- Container restarts

Set memory limit = max your app uses. Add 20% buffer.

For Java: set Xmx based on limit:
```yaml
env:
- name: MAX_HEAP
  valueFrom:
    resourceFieldRef:
      resource: limits.memory
      divisor: "1Mi"

# Use $MAX_HEAP × 0.75 for -Xmx
```

## Memory + Off-Heap

JVM uses memory beyond heap:
- Stack
- Metaspace
- Native libraries
- Direct byte buffers

Set -Xmx to 60-75% of pod limit; rest for off-heap.

## QoS Classes

Determined by requests/limits:
- **Guaranteed**: req=limit on all containers, all resources
- **Burstable**: at least one container has requests
- **BestEffort**: no requests, no limits

Eviction priority (highest evicted first):
1. BestEffort
2. Burstable
3. Guaranteed (last)

Covered T02.

## Setting Sensible Values

Process:
1. Run app
2. Measure CPU + memory usage (Prometheus)
3. Request = average + buffer
4. Limit memory = peak + buffer
5. Don't set CPU limit usually

For web app: 70%ile CPU as request.

## VPA (Vertical Pod Autoscaler)

Recommends / auto-adjusts:
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: Auto   # or "Off" for recommendation only
```

For: right-sizing.

## Compressible vs Incompressible

- **Compressible** (CPU): throttle, don't kill
- **Incompressible** (memory): no throttle, OOM

Implications:
- CPU pressure: slower
- Memory pressure: crashes

## Init Containers

Resources counted differently:
- Init containers run sequentially
- Effective pod request = max(init's request) OR sum(app's request) — whichever is greater per resource

Don't double-count.

## Node Allocatable

```
Allocatable = Capacity - Reserved - Eviction Threshold

Reserved:
- kube-reserved (kubelet, runtime)
- system-reserved (OS)
- eviction-hard threshold (memory.available < 100Mi etc.)
```

```bash
kubectl describe node my-node | grep -A 5 Allocatable
```

Allocatable < Capacity. Plan for this.

## ResourceQuota (Namespace)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "100"
    services: "20"
    persistentvolumeclaims: "50"
```

Namespace can't exceed.

## LimitRange (Defaults)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: defaults
  namespace: production
spec:
  limits:
  - default:
      memory: 256Mi
      cpu: 500m
    defaultRequest:
      memory: 128Mi
      cpu: 250m
    type: Container
```

Pods without limits get defaults.

For: enforce that all pods have limits.

## Cluster Autoscaler Behavior

Scheduler based on requests. If pending pod can't fit:
- Cluster Autoscaler / Karpenter adds node
- New node Allocatable for pod

Without requests set: scheduler thinks pods are tiny; over-schedules; OOM later.

## Karpenter

Modern node provisioner:
- Watches pending pods
- Provisions optimal instance (not bound to ASG)
- Bin-packs (efficient)
- Spot-aware
- Consolidation

Replaces Cluster Autoscaler. Faster + better fit.

## Monitoring

```bash
# Pod usage
kubectl top pod
kubectl top pod -n production --containers

# Node
kubectl top node

# Prometheus
container_cpu_usage_seconds_total
container_memory_working_set_bytes
container_cpu_cfs_throttled_seconds_total
```

For: tune requests/limits.

## CPU Manager Static Policy

For latency-critical: pin pods to specific CPUs:
- Integer CPU requests
- Guaranteed QoS
- CPU Manager static policy enabled on node

```yaml
resources:
  requests:
    cpu: "2"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "2Gi"
```

Pod gets dedicated CPUs (no context switching).

For: trading, gaming, HPC.

## HugePages

For DB / specific apps:
```yaml
resources:
  limits:
    hugepages-2Mi: 100Mi
```

Pre-allocated huge pages from node.

## Extended Resources (GPUs)

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

For GPU workloads (ML, etc.).

## OOM Killer

When container exceeds memory:
1. OOM-killer chooses victim (highest OOM score)
2. SIGKILL
3. Container restarts (if restartPolicy)
4. Event logged

```bash
kubectl describe pod
# Last State: Terminated, Reason: OOMKilled
```

## Memory Buffers

Linux fills memory with caches. Container memory usage includes cache.

`memory.working_set_bytes` is true working set (excludes inactive cache).

For limits: based on working set typically.

## Anti-Patterns

- No requests → bad scheduling
- CPU limit causing throttling
- Memory limit too tight → OOM
- Requests = limits everywhere (no flexibility)
- Default LimitRange too low

## Best Practices

- Set CPU requests (always)
- Set memory requests + limits
- Avoid CPU limits (consider)
- Test with VPA recommendations
- Monitor throttling + OOMs
- LimitRange for default
- ResourceQuota per namespace
- Tune per workload

## Common Mistakes

- BestEffort prod pods (evicted first)
- Java without -Xmx tied to limit
- Burstable critical workload (still possibly evicted)
- No quota → noisy neighbor

## Tools

- VPA: recommendations
- Goldilocks: simplifies VPA
- Kubecost: cost based on requests vs usage
- Prometheus container_* metrics

## Pattern: Microservice

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "256Mi"
# no CPU limit
```

Burstable; cap memory; CPU bursts when available.

## Pattern: DB on K8s

```yaml
resources:
  requests:
    cpu: "2"
    memory: "8Gi"
  limits:
    cpu: "2"
    memory: "8Gi"
```

Guaranteed; protected from eviction; predictable.

## Quick Refs

```bash
# Top
kubectl top pod
kubectl top node

# Describe (events show OOM)
kubectl describe pod my-pod

# Resource recommendations (VPA)
kubectl get vpa
```

## Interview Prep

**Junior**: "Request vs limit."

**Mid**: "Why avoid CPU limits."

**Senior**: "Right-size for production app."

**Staff**: "Resource strategy for 100-service platform."

## Next Topic

→ [T02 — QoS Classes](T02-QoS-Classes.md)
