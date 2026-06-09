# L13 — Kubernetes (Beginner to Internals)

## Overview

Kubernetes is THE central technology for any FAANGM DevOps interview in 2026. This is the largest lecture in the course: 20 chapters, 80+ topics. You must master it.

**20 chapters, 86 topics. Budget 120+ hours.**

## Learning Outcomes

By the end:
1. Diagram the entire pod lifecycle from `kubectl apply` to running container
2. Operate etcd in production (backup, restore, performance)
3. Write a Custom Resource + Controller in Go
4. Diagnose any K8s issue using kubectl and Linux internals
5. Design and operate multi-cluster, multi-region K8s platforms
6. Pass any K8s interview question at any level

## Chapter Map

### [C01](C01/) — Kubernetes Architecture
- T01 The Control Plane (API Server, etcd, Scheduler, Controller Manager, Cloud Controller Manager)
- T02 The Data Plane (kubelet, kube-proxy, container runtime)
- T03 The Pod Lifecycle (End-to-End)
- T04 The Scheduler Internals
- T05 etcd Deep Dive

### [C02](C02/) — Core Workload Resources
- T01 Pods (The Atomic Unit)
- T02 ReplicaSets & Deployments
- T03 StatefulSets
- T04 DaemonSets
- T05 Jobs & CronJobs

### [C03](C03/) — Configuration
- T01 ConfigMaps
- T02 Secrets (And Why They're Not Really Secret)
- T03 Downward API
- T04 Environment Variables vs Files

### [C04](C04/) — Networking in Kubernetes
- T01 Pod-to-Pod, Pod-to-Service, External-to-Service
- T02 CNI Plugins (Calico, Cilium, Flannel, AWS VPC CNI)
- T03 kube-proxy Modes (iptables vs IPVS vs eBPF)
- T04 Services (ClusterIP, NodePort, LoadBalancer, Headless)
- T05 Ingress Controllers (Nginx, Traefik, HAProxy, AWS ALB)
- T06 Gateway API (The Future of Ingress)
- T07 NetworkPolicies

### [C05](C05/) — Storage in Kubernetes
- T01 Volumes, PersistentVolumes, PersistentVolumeClaims
- T02 StorageClasses & Dynamic Provisioning
- T03 CSI (Container Storage Interface)
- T04 Stateful Workloads & Data Gravity
- T05 Snapshots

### [C06](C06/) — Security
- T01 RBAC Deep Dive
- T02 Service Accounts & Token Volumes
- T03 Pod Security Standards (replaces PSP)
- T04 NetworkPolicies (Defense in Depth)
- T05 Secrets Encryption at Rest
- T06 OPA Gatekeeper & Kyverno
- T07 Image Pull Secrets, Image Policy

### [C07](C07/) — Scheduling & Resources
- T01 Requests & Limits
- T02 QoS Classes (Guaranteed, Burstable, BestEffort)
- T03 Node Selectors, Affinity, Anti-Affinity
- T04 Taints & Tolerations
- T05 Topology Spread Constraints
- T06 Priority & Preemption
- T07 Custom Schedulers

### [C08](C08/) — Autoscaling
- T01 Horizontal Pod Autoscaler (HPA)
- T02 Vertical Pod Autoscaler (VPA)
- T03 Cluster Autoscaler
- T04 Karpenter (Next-Gen Node Provisioning)
- T05 KEDA (Event-Driven Autoscaling)

### [C09](C09/) — Application Patterns
- T01 Init Containers
- T02 Sidecars (and the new Sidecar API)
- T03 Ambassadors & Adapters
- T04 Graceful Shutdown & PreStop Hooks
- T05 Health Probes (Liveness, Readiness, Startup)

### [C10](C10/) — Operators & CRDs
- T01 Custom Resource Definitions
- T02 Controller Pattern
- T03 Operator SDK (Go, Ansible, Helm)
- T04 kubebuilder
- T05 Writing Your First Operator

### [C11](C11/) — Helm
- T01 Charts, Templates, Values
- T02 Helm Repos & OCI Registries
- T03 Helm 3 Architecture (No Tiller)
- T04 Best Practices

### [C12](C12/) — Kustomize
- T01 Bases & Overlays
- T02 Patches (Strategic Merge, JSON Patch)
- T03 Generators

### [C13](C13/) — GitOps
- T01 ArgoCD Deep Dive
- T02 Flux v2
- T03 App-of-Apps Pattern
- T04 Sync Strategies, Hooks, Waves

### [C14](C14/) — Observability for K8s
- T01 Metrics Server
- T02 kube-state-metrics
- T03 Prometheus Operator
- T04 Container & Pod Metrics

### [C15](C15/) — Logging in K8s
- T01 Logging Architecture Patterns
- T02 Fluent Bit / Fluentd / Vector DaemonSets
- T03 Loki & ELK on K8s

### [C16](C16/) — Troubleshooting K8s
- T01 kubectl describe, logs, exec, debug
- T02 ImagePullBackOff, CrashLoopBackOff, OOMKilled
- T03 DNS Issues, Service Issues, Ingress Issues
- T04 etcd Recovery
- T05 Node Not Ready

### [C17](C17/) — Multi-Cluster Management
- T01 Cluster API
- T02 Karmada, Open Cluster Management
- T03 Multi-Cluster Service Mesh
- T04 Crossplane

### [C18](C18/) — Cluster Provisioning
- T01 kubeadm
- T02 kops, kubespray
- T03 EKS, GKE, AKS Lifecycle
- T04 Self-Managed vs Managed Tradeoffs

### [C19](C19/) — Day 2 Operations
- T01 Cluster Upgrades
- T02 etcd Backup & Restore
- T03 Certificate Rotation
- T04 Capacity Planning

### [C20](C20/) — Production Kubernetes Checklist
- T01 Cluster Hardening (CIS)
- T02 Disaster Recovery
- T03 Cost Controls
- T04 Compliance Posture

## Architecture Diagram

```
Control Plane (master nodes)
┌────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌────────┐  ┌─────────────────┐ │
│  │ kube-        │  │ etcd   │  │ kube-scheduler  │ │
│  │ apiserver    │◄►│ (KV)   │  │                 │ │
│  └──────┬───────┘  └────────┘  └─────────────────┘ │
│         │           ┌──────────────────────────┐    │
│         │           │ kube-controller-manager  │    │
│         │           └──────────────────────────┘    │
│         │           ┌──────────────────────────┐    │
│         │           │ cloud-controller-manager │    │
│         │           └──────────────────────────┘    │
└─────────┼──────────────────────────────────────────┘
          │
Worker Nodes (data plane)
┌─────────▼──────────────────────────────────────────┐
│  Node 1                Node 2                Node N│
│  ┌───────┐ ┌───────┐  ┌───────┐ ┌───────┐         │
│  │kubelet│ │kube-  │  │kubelet│ │kube-  │   ...   │
│  │       │ │proxy  │  │       │ │proxy  │         │
│  └───┬───┘ └───────┘  └───────┘ └───────┘         │
│      ▼                                              │
│  ┌───────────────┐                                  │
│  │ containerd    │  ← OCI runtime                   │
│  └───────────────┘                                  │
│  ┌───────────────┐                                  │
│  │  Pods (apps)  │                                  │
│  └───────────────┘                                  │
└─────────────────────────────────────────────────────┘
```

## The Famous Pod Lifecycle

```
kubectl apply deployment.yaml
    ↓ HTTPS
kube-apiserver
    ↓ validate, mutate, persist
etcd ← stores Deployment object
    ↓ watch event
deployment-controller ← creates ReplicaSet
    ↓
replicaset-controller ← creates Pod (with no node)
    ↓
kube-scheduler ← assigns node based on score
    ↓
kube-apiserver ← updates Pod with nodeName
    ↓ watch event
kubelet on that node
    ↓
container runtime (containerd) ← pulls image, runs container
    ↓
kubelet reports Running back to apiserver
```

## Recommended Reading

- *Kubernetes in Action* — Marko Lukša (THE book)
- *Kubernetes: Up & Running* — Burns, Beda, Hightower
- *Programming Kubernetes* — Hausenblas, Schimanski (for operators)
- Kubernetes documentation (especially Concepts section)
- KubeCon talks (re-watch the architecture/SIG talks)

## Interview Relevance

K8s is the #1 source of FAANGM DevOps interview questions:
- "Walk me through what happens when you apply a deployment"
- "How does the scheduler choose a node?"
- "Diagnose: my pod is stuck in Pending"
- "Design a multi-cluster K8s platform"
- "What is RBAC and how does it work?"
- "Explain CNI and the different implementations"
- "Difference between iptables and IPVS proxy modes"
- "Compare Helm and Kustomize"

## Next

→ [L14 — Service Mesh](../L14/README.md)
