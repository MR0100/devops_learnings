# L13/C17 — Multi-Cluster Management

## Topics

- **T01 Cluster API** — K8s-native cluster lifecycle management. Define clusters as K8s objects.
- **T02 Karmada, Open Cluster Management** — Schedule workloads across clusters. Policy-driven.
- **T03 Multi-Cluster Service Mesh** — Istio multi-cluster, Linkerd multi-cluster, Cilium ClusterMesh.
- **T04 Crossplane** — IaC via K8s API; provision cloud resources as K8s objects.

## Why Multi-Cluster

- **Blast radius** — limit failure scope
- **Regulatory** — data sovereignty
- **Geographic latency** — clusters close to users
- **Scale ceilings** — K8s scales to ~5000 nodes; beyond that, multi-cluster
- **Tenancy** — strong isolation per team/customer

## Approaches

| Approach | Pros | Cons |
|---|---|---|
| Independent clusters + DNS/LB | Simple | No unified ops |
| Federation v2 (KubeFed) | Was once promising | Mostly abandoned |
| Karmada | Workload distribution | Newer, less mature |
| Cluster API | Cluster lifecycle | Doesn't do workload scheduling |
| Crossplane | Cross-cluster + multi-cloud IaC | Steep curve |
| Service Mesh multi-cluster | Cross-cluster service-to-service | Complex to operate |

## Cluster API Concept

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: my-cluster
spec:
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: my-cluster-control-plane
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: AWSCluster
    name: my-cluster
```

Manages cluster creation as a K8s object. Infra providers: AWS, Azure, GCP, vSphere, etc.

## Interview Themes

- "When would you go multi-cluster?"
- "Compare Cluster API and Crossplane"
- "How do you do cross-cluster service-to-service communication?"
- "Strategies for cluster failover"
