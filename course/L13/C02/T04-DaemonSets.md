# L13/C02/T04 — DaemonSets

## Learning Objectives

- Use DaemonSets for per-node workloads
- Apply common patterns

## DaemonSet

Runs one pod per node (matching selector).

For:
- Node-level logging (Fluent Bit, Vector)
- Node-level monitoring (Prometheus node-exporter)
- Networking (CNI components like Calico, Cilium agent)
- Storage (CSI node plugin)
- Security (Falco, runtime monitor)

## YAML

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      tolerations:
      - operator: Exists   # tolerate all taints
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

## Scheduling

DaemonSet controller assigns pods directly (bypassing scheduler historically; now uses scheduler).

Pod added per node:
- New node joins → DaemonSet pod created on it
- Node removed → pod deleted

## Node Selection

By default: every node. Filter via:

### NodeSelector
```yaml
spec:
  template:
    spec:
      nodeSelector:
        disktype: ssd
```

Only on labeled nodes.

### Affinity
More flexible:
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node-role.kubernetes.io/worker
          operator: Exists
```

## Tolerations

To run on tainted nodes (master, GPU):
```yaml
tolerations:
- key: node-role.kubernetes.io/control-plane
  operator: Exists
  effect: NoSchedule
```

Common: `tolerations: [operator: Exists]` (tolerate all).

For: monitor agents that must be everywhere.

## Update Strategies

### RollingUpdate (default)
```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1   # or %
```

One pod at a time updated.

### OnDelete
No auto-update. Delete pod manually; new is updated.

For: critical agents needing manual control.

## Use Cases

### Log Collector
Fluent Bit / Vector on every node:
- Read `/var/log/containers/`
- Ship to backend (S3, Loki, Datadog)

```yaml
volumeMounts:
- name: varlog
  mountPath: /var/log
- name: containers
  mountPath: /var/log/containers
volumes:
- hostPath:
    path: /var/log
- hostPath:
    path: /var/log/containers
```

### Metric Collector
Prometheus node-exporter on every node:
- Expose `/metrics` on port 9100
- Prometheus scrapes

```yaml
hostNetwork: true   # uses node's network
ports:
- containerPort: 9100
  hostPort: 9100
```

### CNI Agent
Cilium / Calico agent on every node:
- Implements pod networking
- Privileged (needs iptables/eBPF)

### CSI Node Plugin
EBS / GCE PD / Azure Disk node plugin:
- Handle volume mount on node
- Privileged

### Security
Falco for runtime monitoring:
- Watches syscalls
- Alerts on suspicious

## Privileged

Many DaemonSets need privileged access:
```yaml
securityContext:
  privileged: true
```

Or specific capabilities:
```yaml
capabilities:
  add: [NET_ADMIN, SYS_ADMIN]
```

For: hostNetwork access, iptables manipulation.

## hostNetwork

Pod uses node's network stack:
```yaml
spec:
  hostNetwork: true
  dnsPolicy: ClusterFirstWithHostNet
```

For: kube-proxy, CNI, hostPort access.

## hostPath Volumes

Mount node FS into pod:
```yaml
volumes:
- name: varlog
  hostPath:
    path: /var/log
```

For: read host files (logs).

Caveat: tight coupling; hard to migrate.

## Resource Requests

DaemonSet pods on every node = N × resources.

Be conservative:
```yaml
resources:
  requests:
    cpu: 50m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

Else: starves user pods.

## Scaling

DaemonSet = (number of matching nodes) pods. No `replicas`.

Add more nodes → more pods. Add nodeSelector to restrict.

## Versioning / Rollout

```bash
# Update image
kubectl set image daemonset/fluent-bit fluent-bit=fluent/fluent-bit:2.0

# Status
kubectl rollout status daemonset/fluent-bit

# Undo
kubectl rollout undo daemonset/fluent-bit
```

## Priority

```yaml
priorityClassName: system-node-critical
```

For critical: scheduled even when resources tight.

`system-node-critical` and `system-cluster-critical`: built-in.

## Common Patterns

### Per-Node Logging
```yaml
# Fluent Bit
spec:
  tolerations:
  - operator: Exists
  containers:
  - name: fluent-bit
    image: ...
    volumeMounts:
    - {name: varlog, mountPath: /var/log}
    - {name: containers, mountPath: /var/lib/docker/containers, readOnly: true}
    - {name: config, mountPath: /fluent-bit/etc}
```

### Node Exporter (Prometheus)
```yaml
spec:
  hostNetwork: true
  containers:
  - name: node-exporter
    image: prom/node-exporter
    args:
    - --path.procfs=/host/proc
    - --path.sysfs=/host/sys
    volumeMounts:
    - {name: proc, mountPath: /host/proc, readOnly: true}
    - {name: sys, mountPath: /host/sys, readOnly: true}
  volumes:
  - {name: proc, hostPath: {path: /proc}}
  - {name: sys, hostPath: {path: /sys}}
```

### CSI Node Plugin
Mount paths to host so kubelet can mount volumes into pods.

## Failure Modes

### Node Down
Pod on dead node Pending; gone when node removed from cluster.

### Pod Crash
Recreated; daemon controller maintains.

### Updates
RollingUpdate one node at a time. If maxUnavailable too high: log collection gap.

## Best Practices

- Tolerate all taints (or specific)
- Resource limits
- Privileged only as needed
- hostPath read-only when possible
- Update strategy: RollingUpdate with maxUnavailable 1
- Priority class for critical

## Common Mistakes

- High resource requests (starves user pods)
- No tolerations (misses tainted nodes)
- hostPath without ro (security risk)
- Updating critical without testing (kills monitoring)

## Operating

```bash
# List
kubectl get daemonset -A

# Pods per node
kubectl get pods -l app=fluent-bit -o wide

# Logs from one
kubectl logs <pod>

# All pod logs (parallel)
for pod in $(kubectl get pods -l app=fluent-bit -o name); do
  kubectl logs $pod | tail -10
done
```

## When NOT DaemonSet

- App pods (use Deployment)
- Per-namespace stuff
- One-off jobs (use Job)

## Helm Common Patterns

Helm charts often install DaemonSets:
```bash
helm install fluent-bit fluent/fluent-bit
```

Configure values; DaemonSet deployed.

## Quick Refs

```bash
# Status
kubectl get daemonset
kubectl rollout status daemonset/X

# Restart
kubectl rollout restart daemonset/X

# Scale (not really)
# DaemonSet = per-node; no replicas

# Delete (removes all pods)
kubectl delete daemonset X
```

## Interview Prep

**Junior**: "What's a DaemonSet."

**Mid**: "When use DaemonSet."

**Senior**: "Update DaemonSet across 1000 nodes."

**Staff**: "Log collection architecture."

## Next Topic

→ [T05 — Jobs & CronJobs](T05-Jobs-CronJobs.md)
