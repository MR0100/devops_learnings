# L13/C04/T02 — CNI Plugins (Calico, Cilium, Flannel, AWS VPC CNI)

## Learning Objectives

- Choose CNI for cluster
- Understand performance trade-offs

## CNI

Container Network Interface: spec for K8s networking plugins.

CNI plugin:
- Allocates IP to pod
- Sets up veth pair
- Configures routes
- Implements network policies (optional)

## When kubelet Creates Pod

kubelet calls CNI:
1. ADD: pod created
2. DEL: pod deleted
3. CHECK: pod IP valid?

CNI plugin binary at `/opt/cni/bin/`.

Config at `/etc/cni/net.d/`.

## Calico

Layer 3 routing (BGP) or overlay (IPIP / VXLAN).

Strengths:
- Mature
- Strong NetworkPolicy
- BGP performance
- eBPF dataplane option

Use:
- AWS, GCP, Azure, on-prem
- Standard choice for many

## Cilium

eBPF-based:
- Replaces kube-proxy
- L4-L7 policies
- Observability (Hubble)
- Faster than iptables
- Service mesh option (no sidecar)

Use:
- Performance-critical
- Modern features
- Advanced policy

## Flannel

Simple overlay (VXLAN typically):
- Easy setup
- Limited features (no NetworkPolicy by default)

Use:
- Quick start
- Simple needs
- Combined with other (Calico for policy)

## AWS VPC CNI

Default for EKS:
- Pods get VPC IPs (real)
- ENI per node holds IPs
- One pod = one VPC IP

Pros:
- AWS-native (SGs, ALB target, etc.)
- No overlay
- VPC visibility

Cons:
- Pod IP limit (per ENI)
- VPC IP exhaustion at scale
- Default no NetworkPolicy (use Calico for that)

For huge pod density: prefix delegation (16 IPs per ENI).

## Other CNI

- Weave Net (overlay)
- Antrea (OVS-based)
- Multus (multi-network)
- Kindnet (Kind default)
- kubenet (basic, legacy)

## Choosing CNI

| | Calico | Cilium | Flannel | AWS VPC CNI |
|---|---|---|---|---|
| Routing | BGP/Overlay | eBPF | Overlay | Real VPC IPs |
| Policy | Strong | Strongest (L7) | Need addon | Need Calico addon |
| Performance | Good | Fastest | Decent | Native |
| Observability | OK | Excellent (Hubble) | Limited | VPC FlowLogs |
| Complexity | Medium | High | Low | Medium |
| AWS Integration | Manual | Manual | Manual | Native |

For EKS: AWS VPC CNI default + Calico for policy.
For new performance-critical: Cilium.
For simple: Flannel.

## NetworkPolicy

K8s standard. CNI implements:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

Calico, Cilium support natively.
AWS VPC CNI: requires Calico add-on.
Flannel: no.

## Cilium NetworkPolicy

Beyond K8s standard:
- L7 policy (HTTP methods, paths)
- DNS-based egress
- Identity-based

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
spec:
  endpointSelector:
    matchLabels:
      app: web
  egress:
  - toFQDNs:
    - matchPattern: "*.amazonaws.com"
```

For: granular policy.

## eBPF

Cilium uses eBPF programs in kernel:
- Faster than iptables
- Programmable (rich logic)
- Visibility (Hubble)

Replaces kube-proxy entirely (Cilium ServiceLB option).

## Hubble

Cilium's observability:
- Real-time network flow
- L7 (HTTP requests visible)
- DNS visibility
- Policy verdicts

CLI:
```bash
hubble observe --follow
```

Or UI.

For: debugging service mesh traffic.

## Switching CNI

Difficult after deployment. Recreate cluster typically.

For new cluster: pick carefully.

## IP Address Management (IPAM)

CNI allocates pod IPs from:
- Pod CIDR (overlay)
- VPC subnet (AWS VPC CNI)
- Custom

Track usage; avoid exhaustion.

## Performance

iptables (kube-proxy default):
- O(n) rules; linear scaling
- 100ms+ for large clusters

IPVS:
- O(1)
- Better at scale

Cilium eBPF:
- O(1)
- Fastest

For 10000+ services: IPVS or eBPF.

## Observability

CNI logs:
- Calico: /var/log/calico/
- AWS VPC CNI: kubectl logs in kube-system aws-node
- Cilium: kubectl logs in kube-system cilium-*

CNI failures cause pod stuck ContainerCreating.

## Bandwidth

CNI implements bandwidth annotations:
```yaml
annotations:
  kubernetes.io/ingress-bandwidth: "10M"
  kubernetes.io/egress-bandwidth: "10M"
```

Some CNIs honor.

## Pod CIDR Sizing

For 1000 nodes × 50 pods = 50000 pods.
- /15 = 131000 IPs (overhead)
- /16 = 65000 IPs (tight)

Plan early.

## Service Mesh + CNI

Service mesh (Istio) usually adds Envoy sidecar; CNI handles pod IP, mesh handles cross-pod routing.

Cilium service mesh: no sidecar; mesh in CNI. Newer approach.

## CNI Chain

Multiple CNIs:
- bandwidth shaping
- portmap (hostPort)
- firewall

Chained for layered functionality.

Example:
```
calico → bandwidth → portmap
```

Each runs in sequence on pod creation.

## EKS Specifics

VPC CNI config:
- `ENABLE_PREFIX_DELEGATION=true`: 16 IPs per ENI
- `WARM_IP_TARGET`: pre-allocate IPs
- `WARM_ENI_TARGET`: pre-allocate ENIs

For high pod density.

## Migration

EKS VPC CNI → Cilium:
- New node group with Cilium
- Migrate pods over
- Retire old node group

Complex; testing in non-prod first.

## Common Issues

### Pods Stuck ContainerCreating
CNI failure. Check:
```bash
kubectl describe pod <pod>
# Events: Failed to setup network

kubectl logs -n kube-system <cni-pod>
```

### IP Exhaustion
No IPs available:
- Increase VPC CIDR / subnet
- Prefix delegation (AWS VPC CNI)
- Smaller pod density

### Network Policy Not Enforced
- CNI doesn't support (Flannel, default AWS VPC CNI)
- Install supported CNI / add Calico for policy

### Slow Service Routing
- iptables at scale
- Switch to IPVS or Cilium

## Cilium Install

```bash
helm install cilium cilium/cilium --namespace kube-system \
  --set kubeProxyReplacement=strict \
  --set k8sServiceHost=API_SERVER_IP \
  --set k8sServicePort=6443
```

Replaces kube-proxy.

## Cilium Service Mesh

Without sidecar:
```yaml
# CiliumEnvoyConfig for L7
apiVersion: cilium.io/v2
kind: CiliumEnvoyConfig
```

For: lower overhead than Istio.

## Best Practices

- Pick CNI for performance + features
- Test before production
- Monitor pod IP usage
- NetworkPolicy enforced
- Observability (Hubble or similar)

## Multi-Cluster Networking

For services across clusters:
- Service mesh (Istio multi-cluster)
- Cilium ClusterMesh (eBPF-based)
- Submariner

Allows service.namespace.cluster.local resolution across.

## Common Mistakes

- Wrong CNI for use case
- No NetworkPolicy
- Single-AZ VPC + cluster spans many AZs
- IP exhaustion not planned

## Quick Refs

```bash
# Pod CIDR per node
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'

# CNI pods
kubectl get pods -n kube-system

# Cilium status
cilium status
hubble observe

# Calico status
calicoctl node status
```

## Interview Prep

**Mid**: "Calico vs Flannel."

**Senior**: "Cilium eBPF advantages."

**Staff**: "CNI for 5000-node cluster."

## Next Topic

→ [T03 — kube-proxy Modes (iptables vs IPVS vs eBPF)](T03-Kube-Proxy.md)
