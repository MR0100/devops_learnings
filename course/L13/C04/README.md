# L13/C04 — Networking in Kubernetes

## Overview

Networking is the most asked area in K8s interviews. Understand pod-to-pod, services, CNI, kube-proxy, ingress, and NetworkPolicies.

## Topics

- **T01 Pod-to-Pod, Pod-to-Service, External-to-Service** — Flat pod network: every pod gets a unique IP across the cluster. Services give stable virtual IP to a set of pods.
- **T02 CNI Plugins (Calico, Cilium, Flannel, AWS VPC CNI)** — CNI is the standard interface. Calico uses BGP + iptables. Cilium uses eBPF (modern). Flannel is simple overlay. AWS VPC CNI gives pods real VPC IPs.
- **T03 kube-proxy Modes (iptables vs IPVS vs eBPF)** — iptables is default; rules grow O(n) with services. IPVS uses hashtable; better at scale. eBPF (Cilium) replaces kube-proxy entirely.
- **T04 Services (ClusterIP, NodePort, LoadBalancer, Headless)** — ClusterIP = internal VIP. NodePort = port on every node. LoadBalancer = cloud LB. Headless (None) = no VIP, returns pod IPs directly via DNS.
- **T05 Ingress Controllers (Nginx, Traefik, HAProxy, AWS ALB)** — Layer 7 routing. Ingress is the K8s object; controller is the implementation (nginx-ingress, traefik, ALB controller, etc.)
- **T06 Gateway API (The Future of Ingress)** — Replaces Ingress at scale. Separates roles (infra/platform/app) and supports L4/L7.
- **T07 NetworkPolicies** — L3/L4 firewall rules per pod. Default-deny, then allow specific traffic. Requires CNI that supports them (Calico, Cilium, not basic Flannel).

## Network Model Rules

1. Every pod gets a unique IP across cluster
2. Pods can reach all other pods without NAT (in the same network)
3. Agents on nodes (kubelet, system daemons) can reach all pods on that node
4. With host network: pod uses node's network namespace

## CNI Comparison

| CNI | Approach | Strengths | Use Case |
|---|---|---|---|
| Flannel | VXLAN overlay | Simple | Small clusters |
| Calico | BGP routing | Mature, NetworkPolicy support | Most production |
| Cilium | eBPF | Performance, observability, replaces kube-proxy | Modern, large clusters |
| AWS VPC CNI | ENI per pod | Real VPC IP, integrates with AWS networking | EKS standard |
| Azure CNI | Real VNET IP | Integrates with Azure | AKS |

## Common Issues

- DNS slow → CoreDNS scaling, NodeLocalDNS, ndots:5 search domain explosion
- Service not reachable → check Endpoints, NetworkPolicy, kube-proxy
- Ingress not routing → controller logs, paths, TLS secret existence
- "Connection refused" intra-pod → readiness probe not passing, no endpoints

## Interview Themes

- "Walk me through how a request reaches a pod"
- "Compare iptables vs IPVS kube-proxy modes"
- "How does CNI work?"
- "Difference between Service types"
- "What does the new Gateway API solve?"
