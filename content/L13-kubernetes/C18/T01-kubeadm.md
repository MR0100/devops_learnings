# L13/C18/T01 — kubeadm

## Learning Objectives

- Use kubeadm
- Bootstrap K8s cluster

## kubeadm

Official K8s bootstrap tool. Sets up control plane + joins nodes.

Used internally by managed services. Good for:
- Self-managed clusters
- On-prem
- Learning K8s internals

## Prerequisites

- Linux nodes (Ubuntu, RHEL, etc.)
- Container runtime (containerd, CRI-O)
- kubeadm, kubelet, kubectl installed
- Swap disabled
- Required ports open
- Time synced

## Install kubeadm

```bash
# Ubuntu (pkgs.k8s.io; version string is e.g. 1.30.0-1.1)
sudo apt-get install -y kubeadm=1.30.0-1.1 kubelet=1.30.0-1.1 kubectl=1.30.0-1.1
sudo apt-mark hold kubelet kubeadm kubectl
```

## Init Control Plane

On first control plane node:
```bash
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --control-plane-endpoint=lb.example.com:6443 \
  --upload-certs
```

Output: join commands for control plane + workers.

## What kubeadm Does

1. Pre-flight checks
2. Generate certs (CA, kubelet, etcd, etc.)
3. Create kubeconfig
4. Bootstrap kube-apiserver, controller-manager, scheduler as static pods
5. Install CoreDNS
6. Install kube-proxy

## Static Pods

Control plane runs as static pods (managed by kubelet directly):
```
/etc/kubernetes/manifests/
├── etcd.yaml
├── kube-apiserver.yaml
├── kube-controller-manager.yaml
└── kube-scheduler.yaml
```

kubelet watches dir; runs pods.

## kubeconfig

After init:
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

kubectl works.

## Install CNI

kubeadm doesn't install CNI:
```bash
# Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Cilium
cilium install
```

Pods Pending until CNI ready.

## Join Workers

On each worker:
```bash
sudo kubeadm join lb.example.com:6443 \
  --token TOKEN \
  --discovery-token-ca-cert-hash sha256:HASH
```

Worker installs kubelet + kube-proxy; registers with API server.

Token expires after 24 hr; generate new:
```bash
kubeadm token create --print-join-command
```

## HA Control Plane

For HA, 3 control plane nodes:
```bash
# First
kubeadm init --upload-certs --control-plane-endpoint=lb:6443

# Get cert key from output

# Other control plane nodes
kubeadm join lb:6443 \
  --token TOKEN \
  --discovery-token-ca-cert-hash sha256:HASH \
  --control-plane \
  --certificate-key KEY
```

LB in front of API servers.

etcd: stacked (on control plane nodes) or external cluster.

## Stacked etcd

Default: etcd runs on control plane nodes.
- 3 control plane = 3 etcd members
- Simpler
- Less HA (lose control plane node = lose etcd member)

## External etcd

Dedicated etcd cluster:
```bash
kubeadm init --config kubeadm-config.yaml
```

```yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
etcd:
  external:
    endpoints:
    - https://etcd1:2379
    - https://etcd2:2379
    - https://etcd3:2379
    caFile: /etc/etcd/ca.crt
    certFile: /etc/etcd/server.crt
    keyFile: /etc/etcd/server.key
```

For: production HA; isolate etcd issues from control plane.

## Upgrade

```bash
# Upgrade plan
kubeadm upgrade plan

# Upgrade first control plane
kubeadm upgrade apply v1.31.0

# Upgrade other control planes
kubeadm upgrade node

# Upgrade workers
# Drain
kubectl drain NODE --ignore-daemonsets
# Update kubeadm (pkgs.k8s.io version string)
apt install kubeadm=1.31.0-1.1
# kubeadm
sudo kubeadm upgrade node
# Update kubelet
apt install kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
sudo systemctl restart kubelet
# Uncordon
kubectl uncordon NODE
```

One minor version at a time.

## Reset

```bash
sudo kubeadm reset
sudo rm -rf /etc/cni/net.d
sudo iptables -F
```

For: clean slate.

## Configuration File

```yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.30.0
clusterName: my-cluster
controlPlaneEndpoint: lb.example.com:6443
networking:
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/12
etcd:
  external:
    endpoints: [...]
apiServer:
  extraArgs:
    audit-log-path: /var/log/audit.log
```

```bash
kubeadm init --config kubeadm-config.yaml
```

For complex setups.

## Certificate Renewal

Certs expire (default 1 year):
```bash
kubeadm certs check-expiration
kubeadm certs renew all
```

Auto-renewal on upgrade.

For long-lived: set higher expiration in init.

## Common Issues

### Init Fails
```bash
journalctl -u kubelet
# Check kubelet logs
```

Common:
- Container runtime issue
- Network issue
- Required ports blocked
- Memory/CPU low

### Worker Won't Join
- Wrong token (expired)
- Wrong API server URL
- Firewall

```bash
kubeadm token list
```

### CoreDNS CrashLoopBackOff
- CNI not installed
- Network policy issue

Install CNI first.

## Common Mistakes

- Forgetting to install a CNI after `kubeadm init` — nodes stay NotReady and CoreDNS sits in CrashLoopBackOff/Pending until the network plugin is applied.
- Leaving swap enabled or required ports (6443, 2379-2380, 10250) blocked — pre-flight checks fail or the kubelet won't start.
- Single control-plane node in production — losing it loses the cluster; use 3 control planes behind a load balancer (and set `--control-plane-endpoint` from the start).
- Letting the 24-hour join token expire and being unable to add workers — regenerate with `kubeadm token create --print-join-command`.
- Skipping certificate renewal — kubeadm certs default to 1-year expiry; an un-upgraded cluster silently breaks when they lapse.
- Skipping minor versions or not draining nodes during upgrades — upgrade one minor version at a time and drain/uncordon each node.

## Best Practices

- HA: 3 control plane + LB
- External etcd for tier-0
- Backup etcd
- Test upgrade in non-prod
- Document procedures

## When kubeadm vs Managed

For self-managed:
- On-prem
- Specific compliance
- Cost-sensitive at scale
- Learning

For managed:
- Cloud-native shops
- Don't want to manage control plane
- Provider integrations matter

For most cloud users: managed (EKS/GKE/AKS).

## kubeadm Output

Save outputs:
- Join command (workers)
- Certificate key (control plane)
- Token

For: future joins.

## Networking Ports

Control plane:
- 6443: API server
- 2379-2380: etcd
- 10250: kubelet
- 10257: controller manager
- 10259: scheduler

Workers:
- 10250: kubelet
- 30000-32767: NodePort

Open in SG / firewall.

## Quick Refs

```bash
# Init
kubeadm init --pod-network-cidr=...

# Join control plane
kubeadm join ... --control-plane --certificate-key KEY

# Join worker
kubeadm join ... --token T --discovery-token-ca-cert-hash sha256:H

# Reset
kubeadm reset

# Upgrade
kubeadm upgrade plan
kubeadm upgrade apply v1.31.0

# Token
kubeadm token create --print-join-command

# Certs
kubeadm certs check-expiration
kubeadm certs renew all
```

## Interview Prep

**Mid**: "What kubeadm does."

**Senior**: "kubeadm vs managed K8s."

**Staff**: "Self-managed K8s for compliance."

## Next Topic

→ [T02 — kops, kubespray](T02-kops-kubespray.md)
