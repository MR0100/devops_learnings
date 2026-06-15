# L13/C19/T01 — Cluster Upgrades

## Learning Objectives

- Plan K8s upgrades
- Apply skew policy

## Upgrade Order

1. etcd (if external)
2. Control plane (API server, scheduler, controllers)
3. Add-ons (CNI, CSI, ingress controller)
4. Workers (kubelet, kube-proxy)
5. Workloads (if API deprecations)

## Skew Policy

- **kube-apiserver**: latest
- **kube-controller-manager / scheduler**: ≤ 1 minor older than apiserver
- **kubelet**: ≤ 3 minor older than apiserver (widened from 2 by KEP-3935, GA since 1.28; was ≤ 2 before)
- **kube-proxy**: must match its node's kubelet minor (≤ 3 older than apiserver)
- **kubectl**: ±1 minor of apiserver

For upgrade: enforce constraints.

## Version Cadence

K8s: ~3 minor versions per year:
- 1.30 → 1.31 → 1.32

Each: 1 year support.

For: stay within supported.

## Upgrade Plan

For 1.30 → 1.32:
1. 1.30 → 1.31 (one minor)
2. 1.31 → 1.32 (one minor)

No skipping minor versions.

## EKS Upgrade

```bash
aws eks update-cluster-version --name mycluster --kubernetes-version 1.31
# Wait
aws eks describe-cluster --name mycluster
# Then nodes
eksctl upgrade nodegroup --name workers --cluster mycluster
```

Or replace node groups with new AMI.

## GKE Upgrade

```bash
gcloud container clusters upgrade mycluster --master --cluster-version 1.31
gcloud container clusters upgrade mycluster --node-pool default-pool
```

Or auto-upgrade with release channels.

## AKS Upgrade

```bash
az aks upgrade --name mycluster --resource-group rg --kubernetes-version 1.31
```

Or scheduled maintenance window.

## Self-Managed (kubeadm)

```bash
# Control plane (one at a time)
# pkgs.k8s.io version strings look like 1.31.0-1.1 (not the old -00 suffix)
sudo apt-get install -y kubeadm=1.31.0-1.1
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.31.0

# kubelet on this node
sudo apt-get install -y kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
sudo systemctl restart kubelet

# Repeat for other control plane
sudo kubeadm upgrade node

# Workers (one at a time)
kubectl drain NODE --ignore-daemonsets
sudo apt-get install -y kubeadm=1.31.0-1.1
sudo kubeadm upgrade node
sudo apt-get install -y kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
sudo systemctl restart kubelet
kubectl uncordon NODE
```

## API Deprecations

K8s deprecates APIs:
- batch/v1beta1 → batch/v1
- extensions/v1beta1 → networking.k8s.io/v1 / apps/v1

For: each release, check release notes; update YAML.

Tools:
- `kubectl convert`
- pluto (detect deprecated APIs)
- kube-no-trouble

## Pre-Upgrade Checks

```bash
# Detect deprecated APIs
kubectl get --raw /metrics | grep apiserver_requested_deprecated_apis

# Or
kubectl-deprecations --output table
```

For: avoid breakage post-upgrade.

## Workload Compatibility

Test:
- Custom controllers (CRDs may evolve)
- Webhooks (admission, conversion)
- Network plugins
- Storage plugins

In non-prod first.

## Rolling Upgrade Strategy

Production:
1. Test in dev
2. Upgrade staging
3. Soak (1 week)
4. Upgrade prod control plane
5. Soak (1 day)
6. Upgrade prod node groups
7. Monitor

## Node Group Upgrade Patterns

### Blue/Green
1. Create new node group (new version)
2. Cordon old; drain
3. Workloads migrate to new
4. Delete old

Less risk; can revert.

### Rolling
1. Update node group spec (new AMI)
2. ASG rolls instances
3. Workloads migrate

Faster; harder to rollback.

For prod: blue/green.

## Karpenter

Automates node upgrades:
```yaml
disruption:
  consolidationPolicy: WhenUnderutilized
  expireAfter: 720h   # 30 days
```

After 30 days: nodes replaced with current AMI.

For: rolling AMI updates.

## Backup Before Upgrade

- etcd snapshot
- Velero backup
- Document rollback procedure

## Rollback

For control plane:
- Cloud-managed: usually no rollback (must forward-fix)
- Self-managed: rollback possible (kubeadm reset + restore)

For: forward-fix preferred.

## Schedule

Maintenance windows:
- Off-peak hours
- Coordinated with stakeholders
- Status page

For 24/7 critical: rolling, careful.

## Multi-Cluster Upgrade

Stagger across clusters:
- Dev → Staging → Prod
- Region by region
- Test workloads in each

Avoid all clusters at once.

## Compatibility Matrix

For controllers / operators:
- Check supported K8s versions
- Upgrade controller before K8s sometimes
- Or after

For: Argo CD, cert-manager, etc.

## Common Issues

### API Removed
Workload uses deprecated API → fails on upgrade.

Fix: convert manifests before upgrade.

### Webhook Incompatibility
Webhook server uses old K8s API version → fails on upgrade.

Fix: upgrade webhook controller.

### CSI Driver
Old CSI driver may not support new K8s version.

Fix: upgrade driver before K8s.

### CRD Storage Version
CRD storage version mismatch.

Fix: convert before upgrade.

## Tools

- pluto: detect deprecated APIs
- kubent: detect deprecated APIs
- kube-no-trouble: check upgrade compatibility
- kustomize / Helm: regenerate manifests

## Best Practices

- Test in dev/staging first
- Soak time between envs
- Pre-upgrade checks (deprecations)
- Backup before
- Document procedure
- Monitor during
- Have rollback plan

## Common Mistakes

- Skipping minor versions
- Upgrading prod without testing
- No backup
- Workloads using deprecated APIs
- All clusters at once

## Long-Term Support

Some distributions offer LTS:
- Bottlerocket (AWS)
- TKG (VMware)
- OpenShift

For: longer between upgrades.

## Cost of Stale

Old K8s:
- Security CVEs unpatched
- Provider drops support (force upgrade or pay extra)
- Tools / vendors drop compatibility

Stay current.

## EKS Extended Support

Beyond standard 14 months: $0.50/hr per cluster (additional ~$365/mo).

For: avoid emergency upgrade.

But: still upgrade eventually.

## Quick Refs

```bash
# Versions
kubectl version
kubectl get nodes

# Detect deprecated
pluto detect-files -d ./manifests
kubent

# Upgrade (managed)
aws eks update-cluster-version --name X --kubernetes-version Y
gcloud container clusters upgrade X
az aks upgrade --name X --kubernetes-version Y

# Upgrade (kubeadm)
kubeadm upgrade plan
kubeadm upgrade apply vX.Y.Z
```

## Interview Prep

**Junior**: "K8s version cadence."

**Mid**: "Upgrade workflow."

**Senior**: "Pre-upgrade checks."

**Staff**: "Upgrade strategy for 100 clusters."

## Next Topic

→ [T02 — etcd Backup & Restore](T02-etcd-Backup.md)
