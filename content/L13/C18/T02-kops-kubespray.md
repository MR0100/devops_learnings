# L13/C18/T02 — kops, kubespray

## Learning Objectives

- Choose cluster provisioner
- Apply per use case

## kops

K8s on AWS / GCP / DigitalOcean. Mature.

```bash
brew install kops
kops create cluster --name=mycluster.example.com \
  --cloud=aws \
  --zones=us-east-1a,us-east-1b,us-east-1c \
  --node-count=3 \
  --master-count=3 \
  --master-size=t3.medium \
  --node-size=t3.large \
  --state=s3://kops-state
```

Stores cluster state in S3.

## kops vs EKS

| | kops | EKS |
|---|---|---|
| Cost | EC2 only | $0.10/hr + EC2 |
| Control plane | Self-hosted (on EC2) | AWS-managed |
| Operations | You manage | AWS manages |
| Upgrade | kops handles | EKS API |
| Customization | More | Less |

For: control + customization → kops.
For: less ops → EKS.

Most teams now: EKS.

## kops Operations

```bash
# Update
kops update cluster mycluster --yes

# Rolling update
kops rolling-update cluster mycluster --yes

# Get
kops get cluster
kops get ig nodes  # instance groups

# Edit
kops edit cluster mycluster

# Validate
kops validate cluster mycluster
```

## kubespray

Ansible-based; multi-cloud + on-prem:
- AWS, GCP, Azure
- VMware vSphere
- Bare metal
- OpenStack

```bash
git clone https://github.com/kubernetes-sigs/kubespray
cd kubespray
ansible-playbook -i inventory/mycluster/hosts.yaml --become --become-user=root cluster.yml
```

## kubespray Pros

- Multi-cloud
- On-prem
- Highly customizable
- Many CNI options
- Production-tested

## kubespray Cons

- Ansible expertise needed
- Setup more complex than kops
- Slower than managed

## Inventory

```yaml
# inventory/mycluster/hosts.yaml
all:
  hosts:
    node1:
      ansible_host: 10.0.0.1
    node2:
      ansible_host: 10.0.0.2
    node3:
      ansible_host: 10.0.0.3
  children:
    kube_control_plane:
      hosts:
        node1:
    kube_node:
      hosts:
        node2:
        node3:
    etcd:
      hosts:
        node1:
```

Define roles per node.

## Variables

```yaml
# inventory/mycluster/group_vars/all.yml
kube_version: v1.30.0
container_manager: containerd
kube_network_plugin: calico
ingress_nginx_enabled: true
metrics_server_enabled: true
```

Many options.

## kubespray Operations

```bash
# Install cluster
ansible-playbook cluster.yml

# Add node
ansible-playbook scale.yml

# Remove node
ansible-playbook remove-node.yml

# Upgrade
ansible-playbook upgrade-cluster.yml
```

## Comparison

| | kops | kubespray | kubeadm |
|---|---|---|---|
| Cloud | AWS+ | Any | Any |
| Bare metal | No | Yes | Yes |
| Customization | Medium | High | Highest |
| Speed | Fast | Slower | Manual |
| Maintenance | Low | Medium | High |

For AWS only: kops or EKS.
For multi-cloud / on-prem: kubespray.
For learning + custom: kubeadm.

## Other Tools

- **k3s**: lightweight K8s; ARM, edge
- **kind**: K8s in Docker; testing
- **minikube**: local dev
- **microk8s**: snap-based; Canonical
- **rancher**: GUI-based; multi-cluster

For learning: minikube / kind.
For prod: EKS / GKE / AKS or kops / kubespray.

## kops Cluster Lifecycle

```bash
# Create
kops create cluster --name=... > cluster.yaml
kops create -f cluster.yaml

# Apply
kops update cluster --yes

# Edit
kops edit cluster mycluster
# Reapply

# Validate
kops validate cluster

# Delete
kops delete cluster --yes
```

## kops Instance Groups

```bash
kops edit ig nodes
```

```yaml
spec:
  machineType: m6i.large
  minSize: 3
  maxSize: 10
  rootVolumeSize: 100
  cloudLabels:
    team: platform
```

Per-role configuration.

## Multi-Master

```bash
kops create cluster --master-count=3 --master-zones=us-east-1a,us-east-1b,us-east-1c
```

HA control plane.

## Cluster Upgrade

```bash
# Edit
kops edit cluster mycluster
# Change kubernetesVersion

# Apply
kops update cluster --yes

# Rolling
kops rolling-update cluster --yes
```

## When kops Still

- AWS pre-EKS investment
- Specific control plane customization
- Cost-sensitive at scale (no $0.10/hr)

## When kubespray Still

- On-prem K8s
- Multi-cloud agnostic
- Specific CNI / runtime choices
- Air-gapped

## Production with kops

- HA masters
- Multi-AZ
- Backup etcd
- Manage AMIs
- Monitor cluster

Plus all K8s ops.

## Production with kubespray

- Ansible CI for cluster definition
- Test in non-prod
- Document inventory
- Backup procedures

## Cost

Self-managed (kops, kubespray):
- EC2 / VM costs only
- 3 control plane × m5.large × 24/7 = ~$300/mo

EKS:
- $73/mo control plane
- + EC2 nodes

For huge clusters: self-managed saves $73/mo.
For ops sanity: EKS worth it.

## Backup

kops + kubespray:
- etcd snapshot (etcdctl)
- Velero for K8s resources

## Disaster Recovery

Rebuild cluster from:
- Terraform / configs in Git
- etcd snapshot
- Velero backups

Test annually.

## Common Mistakes

- **Treating the kops S3 state store as disposable** — it *is* the cluster definition; losing or corrupting it (no versioning, no backups) means you can no longer manage the cluster.
- **Running `kops update cluster` without `--yes` and assuming it applied** — the dry-run prints the diff but changes nothing until `--yes`.
- **Skipping `kops rolling-update`** after a spec change — `kops update` reconciles infra, but existing nodes keep the old config until they roll.
- **kubespray on under-provisioned control-plane nodes** — Ansible runs succeed but etcd starves later; size control-plane/etcd disks (low-latency SSD) up front.
- **Editing nodes by hand on a kubespray/kops cluster** — the next playbook/rolling-update run reverts drift; all changes belong in inventory/group_vars or the kops spec.
- **No etcd snapshot before an upgrade** on self-managed clusters — there is no managed control plane to fall back to.
- **Choosing kops/kubespray when a managed offering fits** — you inherit etcd, certs, and patching for marginal cost savings (~$73/mo for EKS control plane).

## Best Practices

- Keep the cluster definition in Git: kops cluster spec (`kops get cluster -o yaml`) or kubespray inventory + group_vars, reviewed via PR.
- Enable S3 versioning on the kops state bucket; restrict access with IAM.
- HA control plane: 3 control-plane/master nodes across AZs; odd-numbered etcd.
- Automate etcd snapshots and rehearse restore at least quarterly; pair with Velero for namespaced resources and PVs.
- Pin and test the Kubernetes version (`kube_version` / `kubernetesVersion`) in non-prod before prod; upgrade one minor at a time.
- Run kubespray from CI for repeatability; never run `cluster.yml` ad-hoc from a laptop against prod.
- Manage node AMIs/images explicitly and roll them on a cadence to pick up CVE patches.
- Prefer a managed offering (EKS/GKE/AKS) unless on-prem, air-gapped, or specific customization forces self-managed.

## Quick Refs

```bash
# kops
kops create cluster --name=... --state=s3://state
kops update cluster --yes
kops rolling-update cluster --yes

# kubespray
ansible-playbook -i inventory/HOSTS cluster.yml
ansible-playbook scale.yml
ansible-playbook upgrade-cluster.yml

# k3s (lightweight)
curl -sfL https://get.k3s.io | sh -

# kind (local)
kind create cluster
```

## Interview Prep

**Mid**: "kops vs kubeadm."

**Senior**: "Cluster provisioner choice."

**Staff**: "Multi-region multi-tool platform."

## Next Topic

→ [T03 — EKS, GKE, AKS Lifecycle](T03-Managed-K8s.md)
