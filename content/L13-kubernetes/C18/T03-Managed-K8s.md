# L13/C18/T03 — EKS, GKE, AKS Lifecycle

## Learning Objectives

- Distinguish managed K8s offerings
- Apply per cloud

## Comparison

| | EKS | GKE | AKS |
|---|---|---|---|
| Cost (control plane) | $0.10/hr | Free (zonal) or $0.10/hr (regional) | Free |
| Control plane HA | Multi-AZ | Multi-AZ (regional) | Multi-AZ |
| Default CNI | AWS VPC CNI | GCP CNI / Dataplane V2 | Azure CNI / kubenet |
| Auto-upgrade | Manual trigger | Auto (default) | Manual or scheduled |
| Serverless | Fargate, Auto Mode | Autopilot | Automatic |
| Mature | Yes | Yes (longest) | Yes |
| Ease | Medium | Easiest | Medium |

## EKS

Amazon's managed K8s.

### Create
```bash
eksctl create cluster --name mycluster --region us-east-1
# or
aws eks create-cluster --name mycluster --kubernetes-version 1.30 ...
```

### Auto Mode (Newer)
```bash
aws eks create-cluster --name mycluster --compute-config enabled=true
```

EKS manages nodes too (like Fargate but for EKS).

### Cost
- Control plane: $73/mo
- Plus nodes (EC2 / Fargate)
- Plus LBs, EBS, etc.

### Versioning
- New version every ~6 months
- Old versions deprecated; force upgrade
- Standard support: 14 months
- Extended support: $0.50/hr per cluster (after standard)

### Upgrades
1. Upgrade control plane (in-place)
2. Upgrade node groups (replace with new AMI)
3. Test workloads

```bash
aws eks update-cluster-version --name mycluster --version 1.31
```

Or eksctl:
```bash
eksctl upgrade cluster --name mycluster --version 1.31
```

### Networking
- VPC CNI: pods get VPC IPs
- Security Groups for Pods
- IPv6 supported
- ENI per node limit (raise via prefix delegation)

### IAM
- IRSA: K8s SA → IAM role
- Pod Identity (newer): simpler IRSA
- Cluster admin via IAM principal

### Add-Ons
EKS-managed add-ons:
- VPC CNI
- CoreDNS
- kube-proxy
- EBS CSI Driver
- EFS CSI Driver
- Pod Identity Agent

```bash
aws eks create-addon --cluster-name mycluster --addon-name vpc-cni
```

Auto-updates by EKS.

## GKE

Google's managed K8s; longest-running.

### Create
```bash
gcloud container clusters create mycluster --region us-central1
```

### Modes
- **Standard**: manage node pools
- **Autopilot**: GCP manages nodes; pay per pod-second

### Versioning
- Auto-upgrade (default; with maintenance windows)
- Release channels: rapid, regular, stable

### Networking
- GCP CNI / Dataplane V2 (Cilium-based)
- Native VPC integration
- Network Policy via Calico or Dataplane V2

### IAM
- Workload Identity: K8s SA → GCP SA
- Cluster admin via GCP IAM

### Features
- Image streaming (fast pod start)
- Cluster Autoscaler / Node Auto-Provisioning
- Multi-cluster ingress
- Backup for GKE

### Autopilot
- Pay per pod (not nodes)
- GCP manages everything
- Pod resources requested = billed
- Simpler ops

### Cost
- Zonal: free control plane
- Regional: $73/mo
- Autopilot: pay per pod

## AKS

Microsoft's managed K8s.

### Create
```bash
az aks create --resource-group mygroup --name mycluster --node-count 3
```

### Modes
- **Standard**: manage node pools
- **Automatic**: AKS manages nodes (newer)

### Versioning
- Manual or scheduled auto-upgrade
- 1-year support per version

### Networking
- Azure CNI (pods on VNet)
- Kubenet (overlay)
- Azure CNI Overlay (newer)
- Network Policy via Calico or Azure

### IAM
- Workload Identity: K8s SA → Azure AD
- Cluster admin via Azure RBAC

### Features
- Azure AD integration native
- Azure Policy for cluster
- Free control plane
- Sovereign cloud support

### Cost
- Control plane: FREE
- Plus nodes (VMs)
- Plus LBs, disks, etc.

For cost-sensitive: AKS attractive.

## Choosing

| Factor | EKS | GKE | AKS |
|---|---|---|---|
| AWS ecosystem | Best | n/a | n/a |
| GCP ecosystem | n/a | Best | n/a |
| Azure ecosystem | n/a | n/a | Best |
| Ease | Medium | Easiest | Medium |
| Cost (small) | Higher | Free zonal | Free |
| Mature | Yes | Most | Yes |
| Sovereign | No | Limited | Yes |

For most: pick by cloud already in use.

## Multi-Cloud

If multi-cloud:
- Same K8s API; portable workloads
- But add-ons differ
- Service mesh (Istio) for cross-cluster

## Cluster Lifecycle

### Create
Via CLI / Terraform / CDK / CAPI.

### Configure
- Node pools / groups
- Add-ons
- Networking
- IAM

### Operate
- Monitor health
- Scale nodes
- Patch / upgrade
- Backup

### Upgrade
- Control plane first
- Then nodes (rolling)
- Then workloads

### Delete
- Drain workloads
- Delete cluster
- Cleanup networking, IAM, storage

## EKS Specifics

### Node Group Types
- Managed (EKS controls AMI updates)
- Self-managed (you control)
- Fargate (serverless pods)

### Bottlerocket
AWS-optimized OS for containers. Smaller surface; faster updates.

### Karpenter
Recommended for new EKS. Replaces Cluster Autoscaler.

## GKE Specifics

### Image Streaming
Faster pod start by streaming image instead of full pull.

### Multi-Cluster Ingress
Native cross-cluster traffic via GCLB.

### Backup for GKE
Service for backing up cluster.

## AKS Specifics

### Azure Arc
Manage non-AKS K8s from Azure. Hybrid.

### Pod Sandboxing
gVisor / Kata Containers; extra isolation.

### Azure Linux
Microsoft's container OS.

## Production Considerations

For all:
- Multi-AZ
- Multiple node groups (different instance types)
- Spot/preemptible mix
- IRSA/Workload Identity
- Network policies
- Centralized logging/monitoring
- Backup (Velero)
- DR plan

## Cost Comparison Example

10-node m5.large × 24/7:
- EKS: $0.10/hr CP + 10 × $0.096 = $863/mo
- GKE zonal: $0 CP + 10 × ~$70 (sustained use) = $700/mo
- AKS: $0 CP + 10 × ~$75 (similar VM cost) = $750/mo

For huge: nodes dominate; CP cost negligible.

## When NOT Managed

- Hyper-cost-sensitive at huge scale
- Specific control plane mods
- On-prem
- Compliance forbids cloud-managed

For 95%: managed wins.

## Upgrade Strategy

For all:
1. Test in dev
2. Upgrade control plane
3. Add new node group with new version
4. Drain old node group
5. Delete old node group

Less disruption.

## EKS Anywhere

Run EKS on your hardware. Hybrid.

## Anthos (GKE)

Hybrid K8s with Google-managed control plane on your hardware.

## Best Practices

- IRSA/Workload Identity (not static keys)
- Network policies
- Pod Security Standards
- Encrypted etcd (where supported)
- Audit logging
- Cost monitoring per cluster
- Documented runbooks

## Common Mistakes

- Single-AZ
- Wide IAM
- No backup
- Skip upgrades (deprecated versions)
- No monitoring

## Quick Refs

```bash
# EKS
eksctl create cluster --name X
eksctl upgrade cluster --name X --version Y
aws eks update-cluster-version --name X --version Y

# GKE
gcloud container clusters create X
gcloud container clusters upgrade X

# AKS
az aks create --name X --resource-group RG
az aks upgrade --name X --resource-group RG
```

## Interview Prep

**Mid**: "EKS / GKE / AKS differences."

**Senior**: "Upgrade strategy."

**Staff**: "Multi-cloud K8s platform."

## Next Topic

→ [T04 — Self-Managed vs Managed Tradeoffs](T04-Self-vs-Managed.md)
