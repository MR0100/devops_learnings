# L13/C18 — Cluster Provisioning

## Topics

- **T01 kubeadm** — Official bootstrap tool. Used by managed services internally. Good for self-managed clusters.
- **T02 kops, kubespray** — Higher-level provisioners. kops for AWS; kubespray (Ansible-based) for multi-cloud and on-prem.
- **T03 EKS, GKE, AKS Lifecycle** — Cloud managed. Differences in: control plane HA, networking, IAM integration, node groups.
- **T04 Self-Managed vs Managed Tradeoffs** — Cost, control, ops burden, upgrade speed.

## Managed Comparison

| | EKS | GKE | AKS |
|---|---|---|---|
| Control plane cost | $0.10/hr per cluster | Free up to 1 zonal, paid for regional | Free |
| Control plane HA | Multi-AZ | Multi-AZ (regional) or single | Multi-AZ |
| Networking | AWS VPC CNI default | GKE native (alias IP) or dataplane-v2 (Cilium) | Azure CNI or kubenet |
| Node mgmt | Self or Karpenter | GKE Autopilot or Standard | AKS or VMSS |
| Upgrades | Manual minor, auto patch | Auto by default (release channels) | Manual |
| IAM | IRSA (Pod Identity is new) | Workload Identity | Pod Identity / Workload Identity |

## Self-Managed Considerations

| Pro | Con |
|---|---|
| Full control of version, kernel, addons | You own upgrades, etcd, patching |
| Avoid managed services premium | Significant ops burden |
| Run anywhere (on-prem, edge, air-gapped) | Hire the expertise |

For most teams: managed (EKS/GKE/AKS) wins.

## kubeadm Bootstrap

```bash
# On control-plane node
kubeadm init --pod-network-cidr=10.244.0.0/16 \
             --control-plane-endpoint=cluster.example.com

# On worker
kubeadm join cluster.example.com:6443 \
  --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

## EKS via eksctl Example

```bash
eksctl create cluster \
  --name prod \
  --region us-east-1 \
  --version 1.30 \
  --nodegroup-name workers \
  --node-type m6i.large \
  --nodes 3 --nodes-min 1 --nodes-max 10 \
  --managed
```

## Interview Themes

- "Compare EKS, GKE, AKS"
- "When would you self-manage K8s?"
- "Walk me through cluster upgrade strategy"
- "Cluster API vs kubeadm vs cloud-managed"
