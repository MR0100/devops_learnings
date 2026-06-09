# L13/C01/T02 — The Data Plane (kubelet, kube-proxy, runtime)

## Learning Objectives

- Understand data plane components
- Reason about pod execution

## Components Per Node

```
kubelet           - manages pods on this node
kube-proxy        - manages service routing on this node
container runtime - actually runs containers (containerd, CRI-O)
CNI plugin        - configures pod networking
CSI plugin        - mounts storage
```

## kubelet

Agent that:
- Registers node with API Server
- Watches Pod spec assigned to this node (`spec.nodeName == this-node`)
- Calls runtime to start/stop containers
- Reports pod status
- Runs liveness/readiness/startup probes
- Manages volumes (mount/unmount)
- Performs garbage collection
- Updates node status

Runs as systemd service typically.

## kubelet → Runtime

Via CRI (Container Runtime Interface):
- gRPC API
- Implementations: containerd, CRI-O
- Replaces deprecated Docker shim (dockershim) removed in 1.24

```
kubelet → CRI gRPC → containerd → runc → container
```

## containerd / CRI-O

Container runtimes:
- Pull images
- Manage container lifecycle
- Provide CRI API
- Use runc / crun as low-level runtime

## kube-proxy

Manages Service routing on each node.

For each Service: configures iptables / IPVS / eBPF rules so:
- Pod or external traffic to ClusterIP → DNAT to one of Service's pod IPs

Modes:
- **iptables**: default; rules per endpoint; CPU-bound at scale
- **IPVS**: kernel-level LB; scales better
- **eBPF**: Cilium replaces kube-proxy with eBPF programs (faster)

## CNI Plugin

Configures pod network:
- Allocates IP per pod
- Sets up pod's network namespace
- Configures routes
- May implement NetworkPolicy

Plugins: Calico, Cilium, Flannel, AWS VPC CNI, Weave.

## CSI Plugin

Container Storage Interface:
- Dynamic provisioning
- Mounting
- Snapshot
- Resize

Per-cloud: EBS CSI, GCP PD CSI, Azure Disk CSI.

## Pod Lifecycle

1. Scheduler assigns pod → API Server writes `spec.nodeName`
2. Watch on kubelet → sees pod
3. kubelet pulls image (via CRI)
4. CNI sets up network
5. CSI mounts volumes
6. Runtime starts containers
7. Probes run
8. Status reported back to API Server

## kubelet Components

- **Pod Manager**: tracks desired pods
- **Container Manager**: runtime interactions
- **Volume Manager**: mount/unmount
- **Probe Manager**: liveness/readiness
- **CAdvisor**: resource metrics
- **Eviction Manager**: handle resource pressure

## Node Status

kubelet reports:
- Capacity (CPU, RAM, storage)
- Allocatable (capacity - system reserved)
- Conditions (Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable)
- Addresses
- NodeInfo (OS, kernel, runtime version)

```bash
kubectl describe node my-node
```

## Heartbeat

Two mechanisms:
- NodeStatus updates (full status, every few min)
- Node Lease (lightweight, every 10s)

If kubelet doesn't heartbeat for 40s: node marked NotReady. Pods evicted after 5 min by default.

## Eviction

kubelet evicts pods on resource pressure:

### Soft Eviction
- Threshold + grace period
- Pod terminated cleanly

### Hard Eviction
- Threshold exceeded
- Pod killed immediately

Signals:
- `memory.available`
- `nodefs.available`
- `imagefs.available`
- `pid.available`

Priority order:
- BestEffort first
- Burstable next
- Guaranteed last

## Static Pods

Pods defined in manifest files on node:
```
/etc/kubernetes/manifests/etcd.yaml
/etc/kubernetes/manifests/kube-apiserver.yaml
```

kubelet watches this dir; runs pods.

For: control plane components themselves (bootstrap).

## Garbage Collection

kubelet collects:
- Dead containers (--maximum-dead-containers, --minimum-container-ttl-duration)
- Unused images (when disk pressure)
- Orphan volumes

## Logging

Container logs:
- stdout/stderr → runtime
- Runtime writes to /var/log/containers/...
- Log rotation by runtime / kubelet

External: Fluent Bit / Fluentd / Vector DaemonSet to ship to central.

## kubelet Authentication

To API Server: kubelet has cert. Kubelet bootstrap protocol for fresh nodes.

API Server to kubelet: cert for `kubelet-serving-cert`.

## kube-proxy Failure

If kube-proxy down:
- Services don't work (no DNAT)
- Direct pod-to-pod still works (CNI provides)
- New endpoints not picked up

Existing connections may persist (conntrack).

## Runtime Interface

CRI calls:
- RunPodSandbox
- CreateContainer
- StartContainer
- StopContainer
- RemoveContainer
- ListContainers
- ContainerStatus
- ImageStatus
- PullImage

## Sandbox / Pod

Pod = group of containers sharing:
- Network namespace (same IP)
- IPC namespace
- Sometimes PID namespace
- Volumes

Implemented via pause container holding namespaces; other containers join.

## Networking Setup

1. CNI ADD: pod IP allocated, veth pair, route
2. Pod gets IP, can reach other pods (via CNI overlay or routing)
3. /etc/resolv.conf points to CoreDNS Service

## Volume Setup

For PVC:
- CSI plugin attaches volume to node (if block)
- Mounts to node path
- Bind-mounts into pod

## Inspecting

```bash
# kubelet on node (if accessible)
systemctl status kubelet
journalctl -u kubelet -f

# runtime
crictl ps
crictl logs <containerid>

# kube-proxy
ps aux | grep kube-proxy
iptables -t nat -L

# CNI logs
ls /var/log/calico/ or /var/log/aws-node/

# Network interfaces in pod
nsenter --target $(crictl inspect <id> | jq .info.pid) --net ip addr
```

For managed K8s: limited node access; use logs / metrics via DaemonSet.

## High-Level Flow

```
kubectl apply
↓
API Server
↓
Scheduler binds pod to node N
↓
kubelet on N sees pod
↓
kubelet calls CRI to RunPodSandbox (network setup via CNI)
↓
kubelet calls CRI to CreateContainer for each container
↓
kubelet runs probes
↓
Pod Ready
↓
kube-proxy programs iptables to route Service → pod IP
↓
Traffic flows
```

## Common Failures

### kubelet Crash
Node goes NotReady. Pods evicted after grace.

### Runtime Crash
Containers may continue (if cgroups intact) but no new ops possible. Restart runtime.

### CNI Misconfig
Pods stuck in ContainerCreating. Check CNI logs.

### kube-proxy Hung
Services flaky; new endpoints not added.

## Scale Considerations

Per node:
- ~110 pods default
- ~250 with config (changes pod CIDR / IP per pod)

Cluster:
- 5000 nodes
- 150,000 pods
- 300,000 containers

Tested limits; some exceed (custom tuning).

## Best Practices

- Resource limits (prevent OOM)
- Multi-AZ pod spread
- Probes (liveness, readiness)
- Node taints for special hardware
- Image pull policy (consider IfNotPresent)
- Don't run privileged containers

## Common Anti-Patterns

- No resource requests → bad scheduling
- No probes → traffic to broken
- Privileged everywhere → security risk
- HostPath volumes → tight coupling to node

## Interview Prep

**Junior**: "What does kubelet do?"

**Mid**: "Pod creation flow on a node."

**Senior**: "kube-proxy iptables vs IPVS."

**Staff**: "Diagnose node NotReady."

## Next Topic

→ [T03 — The Pod Lifecycle (End-to-End)](T03-Pod-Lifecycle.md)
