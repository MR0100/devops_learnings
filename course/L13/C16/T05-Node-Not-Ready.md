# L13/C16/T05 — Node Not Ready

## Learning Objectives

- Diagnose NotReady nodes
- Apply fixes

## Node States

```bash
kubectl get nodes
# NAME         STATUS     ROLES   AGE   VERSION
# ip-10-0-1-1  Ready      worker  10d   v1.30
# ip-10-0-1-2  NotReady   worker  10d   v1.30
# ip-10-0-1-3  Unknown    worker  10d   v1.30
```

- Ready: healthy
- NotReady: detected unhealthy
- Unknown: kubelet not reporting

## Effects of NotReady

- New pods not scheduled
- Existing pods evicted (after grace period)
- Services remove pods from endpoints

## Diagnose

```bash
kubectl describe node ip-10-0-1-2
```

Look for:
- Conditions
- Events
- Allocatable

Conditions:
```
Conditions:
  Type             Status  LastHeartbeatTime  Reason
  MemoryPressure   False   ...                KubeletHasSufficientMemory
  DiskPressure     True    ...                KubeletHasDiskPressure
  PIDPressure      False   ...                KubeletHasSufficientPID
  Ready            False   ...                KubeletNotReady
```

Conditions show what's wrong.

## Conditions Reference

- **Ready=False**: kubelet not healthy
- **MemoryPressure=True**: low memory
- **DiskPressure=True**: low disk
- **PIDPressure=True**: too many PIDs
- **NetworkUnavailable=True**: networking issue

## Common Causes & Fixes

### kubelet Down
Most common cause.

```bash
# SSH to node
ssh node
systemctl status kubelet
journalctl -u kubelet -f
```

Restart:
```bash
systemctl restart kubelet
```

If keeps crashing: read logs, fix root cause.

### Disk Pressure
```bash
df -h
# /var full
```

Causes:
- Images accumulated (cleanup)
- Logs not rotated
- App data on / partition

Fix:
```bash
crictl rmi --prune                # remove unused images
journalctl --vacuum-time=7d        # truncate journal
```

Or extend disk / move data.

### Memory Pressure
Node OOM:
```bash
free -h
dmesg | grep -i oom
```

kubelet evicts pods. Allocatable shrinks.

Fix:
- Larger node
- Move pods elsewhere
- Reduce memory requests

### Container Runtime Issue
```bash
systemctl status containerd
crictl ps
```

Sometimes runtime stuck:
```bash
systemctl restart containerd
systemctl restart kubelet
```

### Network Partition
Node can't reach control plane.

Test from node:
```bash
curl -k https://kube-apiserver:6443/healthz
```

If fails: network issue. Check:
- Routes
- DNS
- Firewall
- VPC

### Certificate Expired
```bash
openssl x509 -in /var/lib/kubelet/pki/kubelet.crt -text -noout | grep "Not After"
```

If expired: rotate. Most distros auto-rotate; check kubelet logs.

### Disk I/O Saturated
```bash
iostat -xz 1
```

If %util 100%: disk bottleneck. kubelet operations slow.

Fix: faster disk; reduce I/O.

## SSH to Node

For self-hosted: SSH directly.

For managed (EKS/GKE/AKS): often limited.

EKS via SSM:
```bash
aws ssm start-session --target i-xxxxx
```

## kubelet Logs

```bash
journalctl -u kubelet -f
```

Or for managed: provider's log integration.

## Recovery

### Soft Restart
```bash
systemctl restart kubelet
```

If kubelet was stuck.

### Hard Reboot
```bash
reboot
```

If kernel-level issue.

For ASG: terminate; ASG replaces:
```bash
aws autoscaling terminate-instance-in-auto-scaling-group \
  --instance-id i-xxx --should-decrement-desired-capacity false
```

For Karpenter:
```bash
kubectl delete node ip-10-0-1-2
# Karpenter notices; provisions replacement
```

## Evict Pods First

If node NotReady but want to migrate gracefully:
```bash
kubectl drain ip-10-0-1-2 --ignore-daemonsets --delete-emptydir-data
```

Then terminate.

## Cordon to Stop New Scheduling

```bash
kubectl cordon ip-10-0-1-2
```

Doesn't evict; just stops new pods.

For maintenance window.

## Pod Eviction on NotReady

```yaml
# Pod with toleration
tolerations:
- key: node.kubernetes.io/not-ready
  operator: Exists
  effect: NoExecute
  tolerationSeconds: 300
```

Default 300s (5 min) before pods evicted.

For critical pods: extend (3600 = 1 hr) to ride out blips.

## Network Plugin Issue

CNI agent (Calico, Cilium, AWS VPC CNI) on node:
```bash
kubectl get pods -n kube-system -l app=calico-node
kubectl logs -n kube-system <calico-pod>
```

If CNI agent crashes: pods can't get IPs; node effectively unusable.

## Cgroup Issue

For:
- CrashLoopBackOff cluster-wide
- Slow operations

Check cgroup driver:
```bash
docker info | grep Cgroup
# kubelet --cgroup-driver=systemd
```

Mismatch between containerd + kubelet: pods fail.

## Inspection Tools

On node:
```bash
top                       # processes
free -h                   # memory
df -h                     # disk
iostat -xz 1              # disk IO
netstat -anpt             # connections
systemctl status kubelet
journalctl -u kubelet -f
crictl ps                 # containers
crictl images             # images
```

## Auto-Recovery

Cluster Autoscaler / Karpenter:
- Detects unhealthy node
- Drains (graceful)
- Removes
- Provisions replacement

For managed: provider handles for unhealthy detection.

## Common Patterns

### Disk Full
Pattern: nodes go NotReady; restart kubelet recovers temp; goes back.

Long term: image cleanup automation; smaller disk thresholds.

### kubelet Memory Leak
Pattern: kubelet itself grows; restart fixes.

Workaround: periodic restart. Long term: upgrade kubelet.

### Container Runtime Hang
Pattern: pods stuck Terminating; node otherwise fine.

Fix: restart containerd:
```bash
systemctl restart containerd
```

Or delete pod force:
```bash
kubectl delete pod stuck-pod --grace-period=0 --force
```

## Alert on NotReady

```yaml
- alert: NodeNotReady
  expr: kube_node_status_condition{condition="Ready", status="true"} == 0
  for: 5m
  labels:
    severity: critical
```

For: immediate response.

## Auto-Replace

For ASG / Karpenter:
- NotReady > N min → replace
- Cattle-style

Without auto-replace: manual intervention.

## DaemonSet on NotReady

DaemonSet pods often tolerate NotReady (keep running for log collection during issues).

For most workloads: evicted.

## Monitoring

```promql
# Nodes NotReady
sum(kube_node_status_condition{condition="Ready", status="true"} == 0)

# Memory pressure
sum(kube_node_status_condition{condition="MemoryPressure", status="true"})

# Disk pressure
sum(kube_node_status_condition{condition="DiskPressure", status="true"})
```

Dashboard + alerts.

## Best Practices

- Multi-AZ
- Multiple node types
- Auto-replace via Karpenter
- Monitor node conditions
- Tolerations for critical pods
- Pre-pull images (less time in NotReady)
- Logs / metrics agents in DaemonSets

## Common Mistakes

- Single-node control plane (HA needed)
- Disk too small (pressure quickly)
- No auto-replace (manual debt)
- Long tolerationSeconds (long downtime)

## Recovery Time

Typical:
- Detection: 40s (kubelet heartbeat)
- Pod eviction: 5 min default
- Replacement (Karpenter): 30-60s
- Pod scheduled: <30s
- App ready: depends

Total: ~6-8 min from failure to recovery.

For faster: tune timing, pre-warm.

## Test

Chaos engineering:
```bash
# Cordon
kubectl cordon ip-10-0-1-2
# Force NotReady
kubectl exec -n kube-system <kubelet-pod> -- killall kubelet
```

Observe recovery.

## Quick Refs

```bash
# Status
kubectl get nodes
kubectl describe node NAME

# Drain + delete
kubectl drain NAME --ignore-daemonsets
kubectl delete node NAME

# Manual restart kubelet (on node)
systemctl restart kubelet

# Events
kubectl get events --field-selector involvedObject.kind=Node
```

## Interview Prep

**Mid**: "Node NotReady causes."

**Senior**: "Disk pressure mitigation."

**Staff**: "Cluster autoscaling + node recovery."

## Next Topic

→ Move to [L13/C17 — Multi-Cluster](../C17/README.md)
