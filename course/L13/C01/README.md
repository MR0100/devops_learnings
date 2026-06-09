# L13/C01 — Kubernetes Architecture

## Chapter Overview

The architecture chapter is the most important interview chapter in K8s. You must be able to diagram and discuss every component, every interaction, and every failure mode.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Control-Plane.md) | The Control Plane (API Server, etcd, Scheduler, Controller Manager, CCM) | 2 hr |
| [T02](T02-Data-Plane.md) | The Data Plane (kubelet, kube-proxy, container runtime) | 1.5 hr |
| [T03](T03-Pod-Lifecycle.md) | The Pod Lifecycle (End-to-End) | 2 hr |
| [T04](T04-Scheduler-Internals.md) | The Scheduler Internals | 1.5 hr |
| [T05](T05-Etcd-Deep.md) | etcd Deep Dive | 2 hr |

## Components Diagram

```
                    Control Plane
   ┌─────────────────────────────────────────────────┐
   │  kube-apiserver  ◄────►  etcd (3+ nodes)         │
   │       ▲                                          │
   │       │ watch+write                              │
   │       │                                          │
   │  kube-scheduler  (assigns pods → nodes)          │
   │  kube-controller-manager (deployments, jobs...)  │
   │  cloud-controller-manager (LBs, nodes, routes)   │
   └───────┬─────────────────────────────────────────┘
           │ HTTPS (kubectl, kubelets)
           ▼
                    Worker Nodes
   ┌───────────────────────────────────────────────────┐
   │ kubelet  ◄►  CRI (containerd/CRI-O)               │
   │ kube-proxy  ◄►  kernel netfilter / IPVS / eBPF    │
   │ CNI plugin (Calico, Cilium, Flannel, AWS VPC CNI) │
   │ CSI plugin (EBS, GCE PD, Ceph, ...)               │
   │ Pods (your apps)                                  │
   └───────────────────────────────────────────────────┘
```

## Critical Interactions

### The Watch Loop
Every controller works the same way:
1. Watch a resource type via API
2. Compare desired vs actual
3. Take action to reconcile
4. Status update

This is the **fundamental K8s pattern**. Operators you'll write later follow it.

### How a Deploy Happens

```
kubectl apply  →  apiserver  →  etcd
                     │
                     ▼ watch
            ┌─ deployment-controller (creates RS)
            ├─ replicaset-controller (creates Pods, no node)
            └─ scheduler (assigns nodes)
                     │
                     ▼ updates apiserver
                  etcd
                     │
                     ▼ watch
                 kubelet
                     │
                     ▼ CRI
              containerd → runc → container
```

### Why etcd Matters

etcd is the source of truth. Everything else can rebuild from etcd. Lose etcd, lose the cluster (unless you have backups).

- Raft consensus, 3 or 5 nodes (odd for quorum)
- 8 GB practical size limit; use compaction
- Latency sensitive — local SSD, low network jitter

## Failure Modes

| Failure | Symptom | Recovery |
|---|---|---|
| API server down | kubectl times out; apps keep running | restart, check certs, check etcd |
| etcd quorum lost | All writes fail | restore from snapshot |
| Scheduler down | New pods Pending | restart |
| Controller-manager down | Deployments don't roll | restart |
| kubelet down on node | Node NotReady; pods evicted after timeout | investigate node |
| Single node failure | Pods rescheduled (if Deployment) | normal recovery |

## Interview Themes

- "Diagram the K8s control plane and explain each component"
- "What happens when etcd is down?"
- "How does the scheduler choose a node?"
- "Walk me through the entire pod lifecycle"
