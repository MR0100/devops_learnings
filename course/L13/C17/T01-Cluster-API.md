# L13/C17/T01 — Cluster API

## Learning Objectives

- Manage cluster lifecycle with CAPI
- Apply CAPI to cloud providers

## Cluster API (CAPI)

K8s-native cluster lifecycle management. Define K8s clusters as CRs.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-cluster
spec:
  clusterNetwork:
    pods:
      cidrBlocks: [10.244.0.0/16]
  infrastructureRef:
    kind: AWSCluster
    name: prod-cluster
  controlPlaneRef:
    kind: KubeadmControlPlane
    name: prod-cluster-control-plane
```

Apply: management cluster provisions workload cluster.

## Why CAPI

- Declarative cluster provisioning
- Version control clusters
- Upgrade fleet
- Multi-cloud consistent API
- GitOps-friendly

## Architecture

```
Management Cluster (CAPI)
  ↓ provisions
Workload Clusters (managed)
```

Single management cluster manages many workload clusters.

## Providers

CAPI has provider plugins:
- AWS (CAPA)
- Azure (CAPZ)
- GCP (CAPG)
- vSphere (CAPV)
- OpenStack
- Docker (CAPD) for testing
- BYOH (bring your own host)

## Install

Management cluster (any K8s):
```bash
clusterctl init --infrastructure aws
```

Installs:
- Cluster API controllers
- Provider-specific controllers
- CRDs

## Create Cluster

```bash
clusterctl generate cluster prod-cluster \
  --kubernetes-version v1.30.0 \
  --control-plane-machine-count 3 \
  --worker-machine-count 5 \
  > prod-cluster.yaml

kubectl apply -f prod-cluster.yaml
```

Generates CRs; CAPI provisions actual EC2 / VMs / etc.

## CRs Involved

```yaml
# Cluster (top-level)
Cluster

# Infrastructure
AWSCluster
AzureCluster

# Control plane
KubeadmControlPlane

# Worker nodes
MachineDeployment
MachineSet
Machine

# Per-machine infra
AWSMachineTemplate
```

## Lifecycle

```
1. User applies Cluster CR
2. CAPI controllers reconcile
3. Provider provisions cloud resources (VPC, IAM, EC2)
4. Control plane VMs come up
5. CAPI bootstraps K8s on them
6. Workers added
7. Cluster Ready
```

## Upgrade

Change version in CR:
```yaml
spec:
  version: v1.31.0
```

CAPI rolling-upgrades nodes:
1. New control plane node with new version
2. Replace old
3. Repeat
4. Then workers

## Scale

```yaml
spec:
  replicas: 10   # in MachineDeployment
```

Add/remove worker nodes.

## Multi-Cluster Management

One management cluster → many workload clusters across regions/clouds.

```yaml
# Cluster A (AWS us-east-1)
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-us-east
  namespace: prod
spec: ...

# Cluster B (AWS eu-west-1)
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-eu-west
  namespace: prod
spec: ...
```

Manage fleet centrally.

## clusterctl

CLI for CAPI ops:
```bash
clusterctl init --infrastructure aws         # init mgmt
clusterctl generate cluster                  # generate templates
clusterctl upgrade plan                       # upgrade plan
clusterctl upgrade apply                      # apply
clusterctl describe cluster prod              # status
```

## GitOps with CAPI

Cluster CRs in Git → ArgoCD/Flux applies → CAPI provisions.

For: declarative fleet management.

## Comparison

| | EKS / GKE / AKS | CAPI |
|---|---|---|
| Type | Cloud-managed | Self-managed |
| Setup | Provider portal | CRs |
| Multi-cloud | No | Yes |
| Control plane | Provider | You (with CAPI) |
| Cost | Provider fee | Just VMs |

For: multi-cloud, self-managed, infrastructure-as-code clusters.
For: AWS-only simple → EKS.

## Reasons NOT CAPI

- Single cloud + EKS / GKE / AKS works
- Don't want to manage control plane
- Small scale (overkill)

For most cloud users: managed K8s.

## Reasons FOR CAPI

- Multi-cloud
- On-prem
- Strict requirements (FIPS, etc.)
- Many clusters (50+)
- Declarative cluster ops

## Bootstrap

Bootstrap chicken-egg: need K8s to run CAPI. Options:
- kind (local)
- minikube
- Existing cluster
- Then "pivot" to managed cluster

```bash
clusterctl move --to-kubeconfig=workload.yaml
```

CAPI moves itself to workload cluster.

## ClusterClass

Templated cluster definitions:
```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: ClusterClass
metadata:
  name: standard-aws
spec:
  controlPlane:
    ref:
      kind: KubeadmControlPlaneTemplate
      name: standard-control-plane
  infrastructure:
    ref:
      kind: AWSClusterTemplate
      name: standard-aws-infra
```

Instantiate:
```yaml
spec:
  topology:
    class: standard-aws
    version: v1.30.0
    controlPlane:
      replicas: 3
    workers:
      machineDeployments:
      - class: standard-workers
        name: workers
        replicas: 5
```

For: many similar clusters from one template.

## ArgoCD Integration

ApplicationSet generators support CAPI:
```yaml
generators:
- clusterDecisionResource:
    configMapRef: my-configmap
    name: my-cluster-decisions
    requeueAfterSeconds: 60
```

Deploy workloads to CAPI-managed clusters.

## Operations

```bash
# List clusters
kubectl get clusters -A

# Describe
clusterctl describe cluster prod-us-east -n prod

# Status
kubectl get cluster prod-us-east -n prod -o yaml

# Get kubeconfig for workload cluster
clusterctl get kubeconfig prod-us-east -n prod > prod-kubeconfig
```

## Upgrades

```bash
# Plan
clusterctl upgrade plan

# Apply
clusterctl upgrade apply --contract v1beta1
```

Updates CAPI components.

For workload cluster K8s upgrade: change `spec.version`.

## Production Considerations

- Management cluster itself HA
- Workload cluster backups (Velero)
- etcd snapshots per workload cluster
- Monitoring across fleet
- Per-cluster networking (VPC isolation)

## Best Practices

- ClusterClass for templates
- GitOps for declarative
- Separate management cluster (small, isolated)
- HA management cluster
- Test upgrades in dev
- Documented procedures

## Common Mistakes

- Workload on management cluster (bad)
- No HA management
- Forgetting workload cluster backups
- Upgrading CAPI without testing

## CAPI vs EKSCTL

EKSCTL: imperative CLI for EKS.
CAPI: declarative + multi-provider.

For EKS-only declarative: Crossplane or Terraform.

## CAPI vs Terraform

Terraform: provisions cluster (and other resources).
CAPI: also provisions, but K8s-native, with reconciliation.

For new: try both; pick.

## Vendor Solutions

- Rancher (SUSE): cluster management UI
- Tanzu (VMware): TKG based on CAPI
- Red Hat (ACM): Advanced Cluster Management
- D2iQ: Konvoy

Built on CAPI; add UI/features.

## Quick Refs

```bash
clusterctl init --infrastructure aws
clusterctl generate cluster NAME ... > cluster.yaml
kubectl apply -f cluster.yaml
clusterctl describe cluster NAME
clusterctl get kubeconfig NAME > kubeconfig
```

## Interview Prep

**Mid**: "CAPI purpose."

**Senior**: "CAPI vs EKS."

**Staff**: "Fleet management at 100 clusters."

## Next Topic

→ [T02 — Karmada, Open Cluster Management](T02-Karmada-OCM.md)
