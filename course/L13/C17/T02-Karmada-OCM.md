# L13/C17/T02 — Karmada, Open Cluster Management

## Learning Objectives

- Schedule across clusters
- Apply multi-cluster policy

## Multi-Cluster Workload Distribution

CAPI provisions clusters.
Karmada / OCM schedule workloads across them.

## Karmada

CNCF project for cross-cluster orchestration.

Architecture:
```
Karmada Control Plane (separate K8s cluster)
   ↓ schedules
Member Cluster A
Member Cluster B
Member Cluster C
```

You apply Deployment to Karmada; Karmada decides where + propagates.

## Install Karmada

```bash
helm install karmada karmada-charts/karmada
```

In separate K8s (host) cluster.

## Register Clusters

```bash
karmadactl join cluster-a --cluster-kubeconfig=cluster-a.config
karmadactl join cluster-b --cluster-kubeconfig=cluster-b.config
karmadactl join cluster-c --cluster-kubeconfig=cluster-c.config
```

Now Karmada knows about them.

## PropagationPolicy

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: PropagationPolicy
metadata:
  name: my-app
spec:
  resourceSelectors:
  - apiVersion: apps/v1
    kind: Deployment
    name: my-app
  placement:
    clusterAffinity:
      clusterNames: [cluster-a, cluster-b, cluster-c]
    replicaScheduling:
      replicaSchedulingType: Divided
      replicaDivisionPreference: Weighted
      weightPreference:
        staticWeightList:
        - targetCluster:
            clusterNames: [cluster-a]
          weight: 1
        - targetCluster:
            clusterNames: [cluster-b]
          weight: 1
        - targetCluster:
            clusterNames: [cluster-c]
          weight: 1
```

Apply Deployment of 30 replicas → 10 per cluster.

## OverridePolicy

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: OverridePolicy
metadata:
  name: my-app
spec:
  resourceSelectors:
  - apiVersion: apps/v1
    kind: Deployment
    name: my-app
  overrideRules:
  - targetCluster:
      clusterNames: [cluster-a]
    overriders:
      imageOverrider:
      - component: Tag
        operator: replace
        value: v1.2.3-us-east
```

Per-cluster customization.

## Cluster Failover

If cluster fails: Karmada redistributes:
```yaml
placement:
  clusterTolerations:
  - key: cluster.karmada.io/not-ready
    operator: Exists
    effect: NoExecute
    tolerationSeconds: 60
```

After 60s NotReady: move pods to healthy clusters.

For DR scenarios.

## Open Cluster Management (OCM)

Red Hat-led. Multi-cluster:
- Hub (management)
- ManagedClusters (workload)
- Klusterlet on each managed

```bash
clusteradm init
clusteradm join --hub-token X
```

For: Red Hat / RHACM users.

## OCM Placement

```yaml
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: Placement
metadata:
  name: my-placement
spec:
  clusterSets: [prod-clusters]
  numberOfClusters: 3
  clusterAffinity:
    matchLabels:
      env: prod
```

Placement decisions for ManifestWork.

## Use Cases

### DR
Deploy to 2 regions; if one fails: traffic shifts.

### Latency
Deploy near users; route locally.

### Compliance
Specific data in specific region.

### Capacity
Spread across clusters for total capacity.

## Multi-Cluster vs Multi-Region

Multi-cluster = multiple K8s clusters (could be same region).

Multi-region = clusters in different regions.

Common: multi-region multi-cluster.

## When NOT Multi-Cluster

- Single region works
- Workload doesn't need DR
- Complexity > benefit
- Cost (2× clusters)

For most: one cluster per region; not many per region.

## Cross-Cluster Service Discovery

Without mesh:
- Apps know cluster endpoints
- Cross-cluster traffic via Internet / VPN

With mesh (Istio multi-cluster, Cilium ClusterMesh):
- Services discovered cross-cluster
- mTLS across
- Failover

Covered T03.

## Federation Old

K8s Federation v1 (deprecated). v2 evolved into Karmada / OCM.

For new: Karmada / OCM.

## Karmada vs OCM

| | Karmada | OCM |
|---|---|---|
| Origin | CNCF | Red Hat |
| Maturity | Growing | Mature (in RH stack) |
| Style | Native CRDs | Native CRDs |
| Use | General | RH ecosystem |

For Red Hat shops: OCM (RHACM).
For others: Karmada.

## Architecture Considerations

Management cluster:
- HA
- Limited workloads (only orchestration)
- Backup
- Separate from workload clusters

## Operations

```bash
# Karmada
kubectl --kubeconfig=karmada-api.config get clusters
kubectl --kubeconfig=karmada-api.config apply -f deployment.yaml
kubectl --kubeconfig=karmada-api.config apply -f propagation-policy.yaml

# Check distribution
kubectl --kubeconfig=karmada-api.config get cluster-a -o wide
karmadactl get deployment my-app
```

## Networking

For cross-cluster traffic:
- Each cluster's pods don't see other cluster's
- Service mesh bridges
- Or LB + Ingress per cluster + DNS

## Centralized Logging / Monitoring

For all clusters: ship to central Loki / Prometheus.

Per-cluster:
- Promtail / Fluent Bit DaemonSet
- Remote-write to central Loki / Prometheus
- Grafana dashboards aggregate

## GitOps + Multi-Cluster

ArgoCD ApplicationSet:
```yaml
generators:
- clusters: {}
```

Deploy app to all registered clusters.

Karmada handles cluster registration; ArgoCD handles app distribution.

## Identity Across Clusters

For cross-cluster auth:
- Federated identity (OIDC)
- Each cluster trusts central IdP
- Same RBAC mapped

## Cost

Multi-cluster:
- N × control planes (each)
- Networking (cross-region traffic)
- Management cluster

For: HA / DR / latency justifies.

## Disaster Recovery

Multi-cluster + Karmada:
- Cluster A fails
- Karmada detects (60s)
- Redistributes pods to B, C
- Auto-scales B, C
- Service continues

Or DNS-based: shift traffic.

## When Multi-Cluster Worth It

- Tier-0 service with <1 min RTO
- Global users + latency targets
- Compliance per region
- Massive scale beyond one cluster

Not for: typical apps.

## Best Practices

- Separate management cluster
- Karmada / OCM for orchestration
- Service mesh for cross-cluster
- Central observability
- GitOps for config
- DR drills

## Common Mistakes

- Multi-cluster without service mesh (apps can't talk)
- Same workload to multiple clusters without coordination
- Network not setup
- No DR testing

## Quick Refs

```bash
# Karmada
karmadactl join CLUSTER --cluster-kubeconfig=PATH
kubectl --kubeconfig=KARMADA apply -f propagation-policy.yaml

# OCM
clusteradm init
clusteradm join --hub-token X
```

## Interview Prep

**Mid**: "Multi-cluster purpose."

**Senior**: "Karmada vs OCM."

**Staff**: "Multi-cluster platform design."

## Next Topic

→ [T03 — Multi-Cluster Service Mesh](T03-Multi-Cluster-Mesh.md)
